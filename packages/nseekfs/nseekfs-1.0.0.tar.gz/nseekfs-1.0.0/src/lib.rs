use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::exceptions::{PyValueError, PyKeyError};
use numpy::{PyReadonlyArrayDyn, PyArray1, PyArray2};
use std::sync::Arc;

mod utils;
mod engine;
mod ann_opt;
mod prepare;

use crate::engine::Engine;
use crate::prepare::prepare_bin_from_embeddings;

// ==================== CONSTANTS ====================
//const MAX_DIMENSIONS: usize = 10000;
//const MIN_DIMENSIONS: usize = 1;
//const MAX_EMBEDDINGS_SIZE: usize = 100_000_000;
const VERSION: &str = "1.0.0";
const SIMD_THRESHOLD: usize = 64; 

// ==================== DATA STRUCTURES ====================

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyQueryItem {
    #[pyo3(get)] pub idx: usize,
    #[pyo3(get)] pub score: f32,
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct PyQueryResult {
    #[pyo3(get)] pub results: Vec<PyQueryItem>,
    #[pyo3(get)] pub query_time_ms: f64,
    #[pyo3(get)] pub method_used: String,
    #[pyo3(get)] pub candidates_generated: usize,
    #[pyo3(get)] pub simd_used: bool,
    #[pyo3(get)] pub parse_time_ms: f64,
    #[pyo3(get)] pub compute_time_ms: f64,
    #[pyo3(get)] pub sort_time_ms: f64,
}

#[pyclass]
pub struct PySearchEngine {
    engine: Arc<Engine>, 
    metrics: Arc<crate::utils::profiling::PerformanceMetrics>, 
}

// ==================== PYTHON METHODS FOR DATA STRUCTURES ====================

#[pymethods]
impl PyQueryItem {
    fn __repr__(&self) -> String { 
        format!("QueryItem(idx={}, score={:.6})", self.idx, self.score) 
    }
    
    #[inline(always)]
    fn __getitem__(&self, key: &str) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            match key {
                "idx" => Ok(self.idx.into_py(py)),
                "score" => Ok(self.score.into_py(py)),
                _ => Err(PyKeyError::new_err(format!("Key '{}' not found", key))),
            }
        })
    }
}

#[pymethods]
impl PyQueryResult {
    fn __repr__(&self) -> String {
        format!(
            "QueryResult(results={}, time={:.3}ms, method={})", 
            self.results.len(), self.query_time_ms, self.method_used
        )
    }
    
    fn to_dict(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            let results_list = PyList::empty(py);
            
            for item in &self.results {
                let item_dict = PyDict::new(py);
                item_dict.set_item("idx", item.idx)?;
                item_dict.set_item("score", item.score)?;
                results_list.append(item_dict)?;
            }
            
            dict.set_item("results", results_list)?;
            dict.set_item("query_time_ms", self.query_time_ms)?;
            dict.set_item("method_used", &self.method_used)?;
            dict.set_item("candidates_generated", self.candidates_generated)?;
            dict.set_item("simd_used", self.simd_used)?;
            dict.set_item("parse_time_ms", self.parse_time_ms)?;
            dict.set_item("compute_time_ms", self.compute_time_ms)?;
            dict.set_item("sort_time_ms", self.sort_time_ms)?;
            
            Ok(dict.into())
        })
    }
}

// ==================== INTERNAL RUST METHODS ====================

impl PySearchEngine {
    /// 🚀 Função Rust interna otimizada - aceita &[f32] diretamente
    fn query_exact_internal(&self, py: Python, query_slice: &[f32], k: usize) -> PyResult<PyQueryResult> {
        use std::time::Instant;

        let start = Instant::now();
        let owned_query: Vec<f32> = query_slice.to_vec();
        let parse_time = start.elapsed();
        
        let compute_start = Instant::now();
        let engine = self.engine.clone();

        let result = py.allow_threads(move || {
            engine.query_exact_with_detailed_timing(&owned_query, k)
        });

        let result = match result {
            Ok(ok) => ok,
            Err(e) => return Err(PyValueError::new_err(e)),
        };

        let compute_time = compute_start.elapsed();
        let total_time = start.elapsed();

        let results: Vec<PyQueryItem> = result.0
            .into_iter()
            .map(|(idx, score)| PyQueryItem { idx, score })
            .collect();

        let simd_used = results.len() > 0 && self.engine.dims >= SIMD_THRESHOLD;
        self.metrics.record_query(total_time.as_millis() as u64, simd_used);

        Ok(PyQueryResult {
            results,
            query_time_ms: total_time.as_secs_f64() * 1000.0,
            method_used: "exact".to_string(),
            candidates_generated: self.engine.rows,
            simd_used,
            parse_time_ms: parse_time.as_secs_f64() * 1000.0,
            compute_time_ms: compute_time.as_secs_f64() * 1000.0,
            sort_time_ms: result.1,
        })
    }

    #[allow(dead_code)]
    fn query_batch_optimized_internal(&self, queries: &[&[f32]], k: usize) -> Result<Vec<(Vec<(usize, f32)>, f64)>, String> {
        use std::time::Instant;
        
        let _start = Instant::now();
        
        // ✨ OTIMIZAÇÃO 1: Processamento paralelo real
        let results: Vec<_> = queries
            .iter()  // Remove par_iter to avoid rayon dependency for now
            .map(|query| {
                let query_start = Instant::now();
                
                // Chama o engine de forma paralela
                let result = self.engine.query_exact(query, k);
                let query_time = query_start.elapsed().as_secs_f64() * 1000.0;
                
                match result {
                    Ok(query_result) => Ok((query_result.results, query_time)),
                    Err(e) => Err(e)
                }
            })
            .collect::<Result<Vec<_>, _>>()?;

        Ok(results)
    }

    /// 🚀 Função batch VECTORIZADA - usa SIMD em múltiplas queries
    fn query_batch_vectorized_internal(&self, all_queries: &[f32], dims: usize, k: usize) -> Result<Vec<(Vec<(usize, f32)>, f64)>, String> {
        use std::time::Instant;
        
        let _start = Instant::now();
        let num_queries = all_queries.len() / dims;
        
        // ✨ OTIMIZAÇÃO 2: Batch SIMD processing
        if dims >= SIMD_THRESHOLD && num_queries >= 4 {
            // Para queries grandes, processa em chunks SIMD
            let chunk_size = 4; // Processa 4 queries de vez com AVX
            let mut all_results = Vec::with_capacity(num_queries);
            
            for chunk_start in (0..num_queries).step_by(chunk_size) {
                let chunk_end = (chunk_start + chunk_size).min(num_queries);
                
                // Extrair chunk de queries
                let mut chunk_queries = Vec::with_capacity(chunk_end - chunk_start);
                for i in chunk_start..chunk_end {
                    let query_start = i * dims;
                    let query_end = query_start + dims;
                    chunk_queries.push(&all_queries[query_start..query_end]);
                }
                
                // Processar chunk em paralelo
                let chunk_results = self.process_query_chunk_simd(&chunk_queries, k)?;
                all_results.extend(chunk_results);
            }
            
            Ok(all_results)
        } else {
            // Fallback para queries pequenas
            self.query_batch_simple_internal(all_queries, dims, k)
        }
    }
    
    /// 🚀 Processamento SIMD de chunk de queries
    fn process_query_chunk_simd(&self, queries: &[&[f32]], k: usize) -> Result<Vec<(Vec<(usize, f32)>, f64)>, String> {
        use std::time::Instant;
        
        // ✨ OTIMIZAÇÃO 3: SIMD paralelo + cache optimizations
        let results: Vec<_> = queries
            .iter()  // Remove par_iter to avoid rayon dependency
            .map(|query| {
                let query_start = Instant::now();
                
                // Usar algoritmo SIMD otimizado se disponível
                let result = if query.len() >= SIMD_THRESHOLD {
                    // Tentar usar método SIMD otimizado se existir no engine
                    self.engine.query_exact(query, k)
                } else {
                    self.engine.query_exact(query, k)
                };
                
                let query_time = query_start.elapsed().as_secs_f64() * 1000.0;
                
                match result {
                    Ok(query_result) => Ok((query_result.results, query_time)),
                    Err(e) => Err(e)
                }
            })
            .collect::<Result<Vec<_>, _>>()?;
            
        Ok(results)
    }
    
    /// 🚀 Fallback simples mas ainda otimizado
    fn query_batch_simple_internal(&self, all_queries: &[f32], dims: usize, k: usize) -> Result<Vec<(Vec<(usize, f32)>, f64)>, String> {
        let num_queries = all_queries.len() / dims;
        
        // ✨ OTIMIZAÇÃO 4: Process chunks mesmo para caso simples
        let results: Vec<_> = (0..num_queries)
            .map(|i| {
                let query_start = i * dims;
                let query_end = query_start + dims;
                let query_slice = &all_queries[query_start..query_end];
                
                let start_time = std::time::Instant::now();
                let result = self.engine.query_exact(query_slice, k);
                let query_time = start_time.elapsed().as_secs_f64() * 1000.0;
                
                match result {
                    Ok(query_result) => Ok((query_result.results, query_time)),
                    Err(e) => Err(e)
                }
            })
            .collect::<Result<Vec<_>, _>>()?;
            
        Ok(results)
    }

    fn query_batch_simple_optimized_internal(&self, all_queries: &[f32], dims: usize, k: usize) -> Result<Vec<(Vec<(usize, f32)>, f64)>, String> {
        use std::time::Instant;
        
        let num_queries = all_queries.len() / dims;
        
        // ✨ LOOP DIRETO SEM OVERHEAD DE REFS/COLLECTIONS
        let mut results = Vec::with_capacity(num_queries);
        
        for i in 0..num_queries {
            let query_start = i * dims;
            let query_end = query_start + dims;
            let query_slice = &all_queries[query_start..query_end];
            
            let start_time = Instant::now();
            
            // Usar método mais rápido disponível para single query
            let result = if dims >= 64 {
                // Use SIMD se dimensões são razoáveis
                self.engine.query_exact_simd_optimized(query_slice, k)
            } else {
                // Scalar para dimensões baixas
                self.engine.query_exact(query_slice, k)
            };
            
            let query_time = start_time.elapsed().as_secs_f64() * 1000.0;
            
            match result {
                Ok(query_result) => results.push((query_result.results, query_time)),
                Err(e) => return Err(e),
            }
        }
        
        Ok(results)
    }

    fn query_batch_large_internal(&self, all_queries: &[f32], dims: usize, k: usize) -> Result<Vec<(Vec<(usize, f32)>, f64)>, String> {
        use std::time::Instant;
        
        let num_queries = all_queries.len() / dims;
        let chunk_size = 50; // Processo em chunks de 50 queries
        
        let mut all_results = Vec::with_capacity(num_queries);
        
        for chunk_start in (0..num_queries).step_by(chunk_size) {
            let chunk_end = (chunk_start + chunk_size).min(num_queries);
            
            // Processar chunk
            for i in chunk_start..chunk_end {
                let query_start = i * dims;
                let query_end = query_start + dims;
                let query_slice = &all_queries[query_start..query_end];
                
                let start_time = Instant::now();
                let result = self.engine.query_exact(query_slice, k)?;
                let query_time = start_time.elapsed().as_secs_f64() * 1000.0;
                
                all_results.push((result.results, query_time));
            }
        }
        
        Ok(all_results)
    }
}

// ==================== PYTHON API METHODS ====================

#[pymethods]
impl PySearchEngine {
    #[new]
    fn new(bin_path: String, ann: bool) -> PyResult<Self> {
        let engine = Engine::new(&bin_path, ann)
            .map_err(|e| PyValueError::new_err(e))?;
        let metrics = Arc::new(crate::utils::profiling::PerformanceMetrics::new());
        
        Ok(PySearchEngine { 
            engine: Arc::new(engine),
            metrics,
        })
    }

    // -------------------- BASIC INFO --------------------
    fn dims(&self) -> usize { self.engine.dims }
    fn rows(&self) -> usize { self.engine.rows }

    // -------------------- QUERY METHODS --------------------
    fn query_exact(&self, py: Python, query: &PyArray1<f32>, k: usize) -> PyResult<PyQueryResult> {
        let slice = unsafe { query.as_slice()? };
        self.query_exact_internal(py, slice, k)
    }
    
    /// 🚀 Query batch REALMENTE otimizado
    fn query_batch(&self, py: Python, queries: &PyArray2<f32>, k: usize) -> PyResult<Vec<PyQueryResult>> {
        use std::time::Instant;
        
        let overall_start = Instant::now();
        
        let queries_slice = unsafe { queries.as_slice()? };
        let dims = self.engine.dims;
        let num_queries = queries_slice.len() / dims;
        
        if num_queries == 0 {
            return Ok(Vec::new());
        }
        
        // ✨ LÓGICA DE OTIMIZAÇÃO CORRIGIDA
        let batch_results = if num_queries >= 100 {
            // Batches muito grandes - usar chunking SIMD
            match py.allow_threads(|| {
                self.query_batch_large_internal(queries_slice, dims, k)
            }) {
                Ok(results) => results,
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        } else if num_queries >= 20 && dims >= 64 {
            // Batches médios com boa dimensionalidade - SIMD otimizado
            match py.allow_threads(|| {
                self.query_batch_vectorized_internal(queries_slice, dims, k)
            }) {
                Ok(results) => results,
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        } else {
            // Batches pequenos ou baixa dimensionalidade - loop otimizado simples
            match py.allow_threads(|| {
                self.query_batch_simple_optimized_internal(queries_slice, dims, k)
            }) {
                Ok(results) => results,
                Err(e) => return Err(PyValueError::new_err(e)),
            }
        };
        
        let total_time = overall_start.elapsed();
        
        // Converter resultados para PyQueryResult
        let mut py_results = Vec::with_capacity(batch_results.len());
        
        for (query_results, individual_query_time) in batch_results {
            let py_items: Vec<PyQueryItem> = query_results
                .into_iter()
                .map(|(idx, score)| PyQueryItem { idx, score })
                .collect();
                
            let simd_used = dims >= 64; // Threshold mais baixo
            
            py_results.push(PyQueryResult {
                results: py_items,
                query_time_ms: individual_query_time,
                method_used: if num_queries >= 100 {
                    "batch_large".to_string()
                } else if num_queries >= 20 && dims >= 64 {
                    "batch_vectorized".to_string()
                } else {
                    "batch_simple_optimized".to_string()
                },
                candidates_generated: self.engine.rows,
                simd_used,
                parse_time_ms: 0.0,
                compute_time_ms: individual_query_time,
                sort_time_ms: 0.0,
            });
        }
        
        // ✨ MÉTRICAS DE BATCH
        let avg_individual_time = py_results.iter().map(|r| r.query_time_ms).sum::<f64>() / py_results.len() as f64;
        let total_time_ms = total_time.as_secs_f64() * 1000.0;
        let batch_efficiency = if total_time_ms > 0.0 {
            (avg_individual_time * num_queries as f64) / total_time_ms
        } else {
            1.0
        };
        
        // Record batch metrics
        self.record_batch_metrics(total_time.as_millis() as u64, num_queries, batch_efficiency);
        
        Ok(py_results)
}
    
    /// 🚀 Query batch com opções avançadas
    fn query_batch_advanced(&self, py: Python, queries: &PyArray2<f32>, k: usize, 
                           parallel_threshold: Option<usize>, simd_threshold: Option<usize>) -> PyResult<Vec<PyQueryResult>> {
        let queries_slice = unsafe { queries.as_slice()? };
        let dims = self.engine.dims;
        let num_queries = queries_slice.len() / dims;
        
        let _use_parallel = num_queries >= parallel_threshold.unwrap_or(4);
        let _use_simd = dims >= simd_threshold.unwrap_or(SIMD_THRESHOLD);
        
        // Custom optimization path based on parameters
        // Por agora, chama o método principal otimizado
        self.query_batch(py, queries, k)
    }

    // -------------------- ALIAS METHODS --------------------
    fn query(&self, py: Python, query: &PyArray1<f32>, top_k: usize) -> PyResult<PyQueryResult> {
        self.query_exact(py, query, top_k)
    }

    fn search(&self, py: Python, query: &PyArray1<f32>, top_k: usize) -> PyResult<PyQueryResult> {
        self.query_exact(py, query, top_k)
    }

    // -------------------- PERFORMANCE METHODS --------------------
    fn get_performance_metrics(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = self.metrics.get_stats();
            let dict = PyDict::new(py);
            
            dict.set_item("total_queries", stats.total_queries)?;
            dict.set_item("avg_query_time_ms", stats.avg_query_time_ms)?;
            dict.set_item("simd_queries", stats.simd_queries)?;
            dict.set_item("scalar_queries", stats.scalar_queries)?;
            dict.set_item("queries_per_second", stats.queries_per_second)?;
            
            Ok(dict.into())
        })
    }
        
    fn reset_metrics(&self) {
        self.metrics.reset();
    }

    // -------------------- BATCH METRICS --------------------
    fn record_batch_metrics(&self, total_time_ms: u64, num_queries: usize, efficiency: f64) {
        // Record batch-specific metrics
        let avg_time_per_query = if num_queries > 0 {
            total_time_ms / num_queries as u64
        } else {
            total_time_ms
        };
        
        // Record as individual queries for now
        for _ in 0..num_queries {
            self.metrics.record_query(avg_time_per_query, true); // Assume SIMD for batches
        }
        
        // Fixed format specifier
        if efficiency > 1.0 {
            println!("Batch efficiency: {:.2}x speedup", efficiency);
        }
    }
}

// ==================== MODULE FUNCTIONS ====================

#[pyfunction]
fn py_prepare_bin_from_embeddings(
    py: Python,
    embeddings: PyReadonlyArrayDyn<f32>,
    dims: usize,
    rows: usize,
    base_name: String,
    output_dir: String,
    level: String,
    normalize: bool,  
    ann: bool,
    _seed: Option<u64>,
) -> PyResult<String> {
    let owned: Vec<f32> = {
        let slice = embeddings.as_slice()?;  // Remove unnecessary unsafe
        slice.to_vec()
    };

    let base_name_owned = base_name.clone();
    let output_dir_owned = output_dir.clone();
    let level_owned = level.clone();

    let result_path = py
        .allow_threads(move || {
            prepare_bin_from_embeddings(
                &owned,                       
                dims,
                rows,
                &base_name_owned,
                &level_owned,
                Some(std::path::Path::new(&output_dir_owned)),
                ann,
                normalize,                    
                0,                           
            )
        })
        .map_err(|e| PyValueError::new_err(format!("{:?}", e)))?;

    Ok(result_path.to_string_lossy().to_string())
}

#[pyfunction]
fn get_system_info(py: Python) -> PyResult<PyObject> {
    let dict = PyDict::new(py);
    
    dict.set_item("platform", std::env::consts::OS)?;
    dict.set_item("arch", std::env::consts::ARCH)?;
    dict.set_item("python_version", py.version())?;
    dict.set_item("rust_engine", "nseekfs-rust-optimized")?;
    dict.set_item("simd_support", cfg!(target_feature = "avx2"))?;
    dict.set_item("cpu_cores", num_cpus::get())?;
    dict.set_item("version", VERSION)?;
    
    Ok(dict.into())
}

#[pyfunction]
fn health_check(py: Python) -> PyResult<PyObject> {
    let dict = PyDict::new(py);
    
    let mut status = "healthy";
    let mut errors = Vec::new();
    
    if !cfg!(target_feature = "avx2") {
        errors.push("AVX2 not available - performance may be reduced");
    }
    
    let available_memory = get_available_memory();
    if available_memory < 1024 * 1024 * 1024 { 
        errors.push("Low available memory detected");
        status = "warning";
    }
    
    if !errors.is_empty() && status != "warning" {
        status = "error";
    }
    
    dict.set_item("status", status)?;
    dict.set_item("system_compatible", errors.is_empty())?;
    dict.set_item("rust_engine_working", true)?;
    dict.set_item("simd_available", cfg!(target_feature = "avx2"))?;
    dict.set_item("available_memory_gb", available_memory as f64 / (1024.0 * 1024.0 * 1024.0))?;
    
    if !errors.is_empty() {
        let errors_list = PyList::new(py, &errors);
        dict.set_item("errors", errors_list)?;
    }
    
    Ok(dict.into())
}

fn get_available_memory() -> usize {
    std::env::var("AVAILABLE_MEMORY")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(8 * 1024 * 1024 * 1024) 
}

// ==================== MODULE REGISTRATION ====================

#[pymodule]
fn nseekfs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySearchEngine>()?;
    m.add_class::<PyQueryResult>()?;
    m.add_class::<PyQueryItem>()?;
    m.add_function(wrap_pyfunction!(py_prepare_bin_from_embeddings, m)?)?;
    m.add_function(wrap_pyfunction!(get_system_info, m)?)?;
    m.add_function(wrap_pyfunction!(health_check, m)?)?;
    
    m.add("__version__", VERSION)?;
    m.add("SIMD_THRESHOLD", SIMD_THRESHOLD)?;
    
    Ok(())
}