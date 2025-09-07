use std::fs::File;
use std::time::Instant;
use std::sync::Arc;
use memmap2::Mmap;
use std::collections::BinaryHeap;
use std::cmp::Reverse;

use crate::utils::vector::{SimilarityMetric, compute_similarity};
use crate::utils::simd::*;
use crate::utils::memory::*;
use crate::utils::profiling::*;

// ==================== CONSTANTS ====================
const PARALLEL_THRESHOLD: usize = 10000; 
const CHUNK_SIZE: usize = 1000; 
const PREFETCH_DISTANCE: usize = 64;
const SIMD_THRESHOLD: usize = 16;  // Threshold baixo para ativar SIMD
const OPTIMAL_CHUNK_SIZE: usize = 1024;

// ==================== HELPER STRUCTS ====================
#[derive(PartialEq, PartialOrd)]
struct OrderedFloat(f32);

impl Eq for OrderedFloat {}

impl Ord for OrderedFloat {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.partial_cmp(other).unwrap_or(std::cmp::Ordering::Equal)
    }
}

// ==================== DATA STRUCTURES ====================

#[derive(Debug)]
pub struct QueryResult {
    pub results: Vec<(usize, f32)>,
    pub query_time_ms: f64,
    pub method_used: String,
    pub candidates_generated: usize,
    pub simd_used: bool,
}

pub struct Engine {
    pub data: Arc<Mmap>, 
    pub dims: usize,
    pub rows: usize,
    pub metrics: Arc<PerformanceMetrics>,
    
    // Buffer pools for performance
    score_buffer: ThreadLocalBuffer<f32>,
    index_buffer: ThreadLocalBuffer<usize>,
}

// ==================== CORE ENGINE IMPLEMENTATION ====================

impl Engine {
    pub fn new(bin_path: &str, _ann: bool) -> Result<Self, String> {
        let start = Instant::now();
        
        // Open and map file
        let file = File::open(bin_path)
            .map_err(|e| format!("Failed to open file: {}", e))?;
        
        let mmap = unsafe {
            Mmap::map(&file)
                .map_err(|e| format!("Failed to map file: {}", e))?
        };
        
        // Read header
        if mmap.len() < 8 {
            return Err("File too small".to_string());
        }
        
        let dims = u32::from_le_bytes([mmap[0], mmap[1], mmap[2], mmap[3]]) as usize;
        let rows = u32::from_le_bytes([mmap[4], mmap[5], mmap[6], mmap[7]]) as usize;
        
        let expected_size = 8 + rows * dims * 4;
        if mmap.len() < expected_size {
            return Err(format!("File size mismatch: expected {}, got {}", expected_size, mmap.len()));
        }
        
        Ok(Engine {
            data: Arc::new(mmap),
            dims,
            rows,
            metrics: Arc::new(PerformanceMetrics::new()),
            score_buffer: ThreadLocalBuffer::new(),
            index_buffer: ThreadLocalBuffer::new(),
        })
    }
    
    /// Get vector by index with bounds checking
    #[inline(always)]
    pub fn get_vector(&self, idx: usize) -> Option<&[f32]> {
        if idx >= self.rows { return None; }
        
        let start_byte = 8 + idx * self.dims * 4;
        let end_byte = start_byte + self.dims * 4;
        
        if end_byte > self.data.len() { return None; }
        
        let byte_slice = &self.data[start_byte..end_byte];
        let float_slice = unsafe {
            std::slice::from_raw_parts(
                byte_slice.as_ptr() as *const f32,
                self.dims
            )
        };
        
        Some(float_slice)
    }

    // ==================== SINGLE QUERY METHODS ====================
    
    /// MÉTODO PRINCIPAL: Sempre usa a versão otimizada completa
    pub fn query_exact(&self, query: &[f32], k: usize) -> Result<QueryResult, String> {
        self.query_exact_auto_optimized(query, k)
    }

    /// IMPLEMENTAÇÃO COMPLETA com todas as otimizações
    pub fn query_exact_auto_optimized(&self, query: &[f32], k: usize) -> Result<QueryResult, String> {
        let start = Instant::now();
        
        if query.len() != self.dims {
            return Err(format!("Query dimensions {} don't match index dimensions {}", query.len(), self.dims));
        }
        
        let simd_used = query.len() >= SIMD_THRESHOLD;  
        let use_parallel = self.rows >= PARALLEL_THRESHOLD;
        let use_early_termination = k <= 50 && self.rows >= 1000;
        
        let (results, method_used) = if use_early_termination && simd_used {
            (self.query_simd_with_early_termination(query, k, &SimilarityMetric::Cosine)?, "simd_early_termination")
        } else if use_parallel && !use_early_termination {
            // Apenas para datasets muito grandes sem early termination
            (self.query_parallel(query, k, &SimilarityMetric::Cosine)?, "parallel")
        } else if simd_used {
            // SIMD normal
            (self.query_simd_optimized(query, k, &SimilarityMetric::Cosine)?, "simd")
        } else {
            // Scalar fallback
            (self.query_scalar_optimized(query, k, &SimilarityMetric::Cosine)?, "scalar")
        };
        
        let ms = start.elapsed().as_secs_f64() * 1000.0;
        self.metrics.record_query(ms as u64, simd_used);
        
        Ok(QueryResult {
            results, 
            query_time_ms: ms, 
            method_used: method_used.to_string(),
            candidates_generated: self.rows, 
            simd_used
        })
    }

    /// Query with detailed timing information
    pub fn query_exact_with_detailed_timing(&self, query: &[f32], k: usize) -> Result<(Vec<(usize, f32)>, f64), String> {
        let start = Instant::now();
        
        let simd_used = query.len() >= SIMD_THRESHOLD;
        let use_parallel = self.rows >= PARALLEL_THRESHOLD;
        let use_early_termination = k <= 50 && self.rows >= 1000;
        
        let sort_start = Instant::now();
        let results = if use_parallel && !use_early_termination {
            self.query_parallel(query, k, &SimilarityMetric::Cosine)?
        } else if simd_used && use_early_termination {
            self.query_simd_with_early_termination(query, k, &SimilarityMetric::Cosine)?
        } else if simd_used {
            self.query_simd_optimized(query, k, &SimilarityMetric::Cosine)?
        } else {
            self.query_scalar_optimized(query, k, &SimilarityMetric::Cosine)?
        };
        let sort_time = sort_start.elapsed().as_secs_f64() * 1000.0;
        
        let total_time = start.elapsed().as_secs_f64() * 1000.0;
        self.metrics.record_query(total_time as u64, simd_used);
        
        Ok((results, sort_time))
    }

    /// Query exact with SIMD optimizations specifically for batch processing
    pub fn query_exact_simd_optimized(&self, query: &[f32], k: usize) -> Result<QueryResult, String> {
        let start = Instant::now();
        
        if query.len() != self.dims {
            return Err(format!("Query dimensions {} don't match index dimensions {}", query.len(), self.dims));
        }
        
        // Cache-friendly processing
        let results = self.query_simd_cache_optimized(query, k, &SimilarityMetric::Cosine)?;
        
        let ms = start.elapsed().as_secs_f64() * 1000.0;
        self.metrics.record_query(ms as u64, true);
        
        Ok(QueryResult {
            results, 
            query_time_ms: ms, 
            method_used: "simd_optimized".to_string(),
            candidates_generated: self.rows, 
            simd_used: true
        })
    }

    // ==================== ALGORITHM IMPLEMENTATIONS ====================
    
    /// Parallel query processing for large datasets
    fn query_parallel(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        let chunk_size = CHUNK_SIZE.min(self.rows / num_cpus::get()).max(100);
        let mut scores = Vec::with_capacity(self.rows);
        
        // Process in chunks (simplified without rayon for now)
        for chunk_start in (0..self.rows).step_by(chunk_size) {
            let chunk_end = (chunk_start + chunk_size).min(self.rows);
            
            for i in chunk_start..chunk_end {
                if let Some(v) = self.get_vector(i) {
                    let score = if query.len() >= SIMD_THRESHOLD {
                        compute_similarity_simd(query, v, metric)
                    } else {
                        compute_similarity(query, v, metric)
                    };
                    scores.push((i, score));
                }
            }
        }
        
        self.select_top_k_optimized(scores, k)
    }
   
    /// SIMD-optimized query processing
    fn query_simd_optimized(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        let mut scores = Vec::with_capacity(self.rows);
        
        // Process with prefetching for better cache performance
        for chunk_start in (0..self.rows).step_by(PREFETCH_DISTANCE) {
            let chunk_end = (chunk_start + PREFETCH_DISTANCE).min(self.rows);
            
            for i in chunk_start..chunk_end {
                // Prefetch next vector
                if i + 1 < self.rows {
                    self.prefetch_vector(i + 1);
                }
                
                if let Some(v) = self.get_vector(i) {
                    let score = compute_similarity_simd(query, v, metric);
                    scores.push((i, score));
                }
            }
        }
        
        self.select_top_k_optimized(scores, k)
    }

    /// SIMD processing with cache optimizations
    fn query_simd_cache_optimized(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        let mut scores = Vec::with_capacity(self.rows);
        
        // Process in cache-friendly chunks
        for chunk_start in (0..self.rows).step_by(OPTIMAL_CHUNK_SIZE) {
            let chunk_end = (chunk_start + OPTIMAL_CHUNK_SIZE).min(self.rows);
            
            // Prefetch multiple cache lines
            for i in chunk_start..chunk_end {
                if i + 8 < self.rows { // Prefetch ahead
                    self.prefetch_vector(i + 8);
                }
                
                if let Some(v) = self.get_vector(i) {
                    let score = compute_similarity_simd(query, v, metric);
                    scores.push((i, score));
                }
            }
        }
        
        self.select_top_k_optimized(scores, k)
    }

    fn query_simd_with_early_termination(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        // Para k grande, usar método normal
        if k > 100 || k >= self.rows / 10 {
            return self.query_simd_cache_optimized(query, k, metric);
        }
        
        // Min-heap para manter os top-k durante processamento
        let mut best_scores = BinaryHeap::with_capacity(k + 1);
        let mut min_score_threshold = f32::NEG_INFINITY;
        let mut skipped_count = 0;
        
        // Process in smaller chunks para early termination mais agressivo
        let chunk_size = 512;  // Chunks menores para early termination mais frequente
        
        for chunk_start in (0..self.rows).step_by(chunk_size) {
            let chunk_end = (chunk_start + chunk_size).min(self.rows);
            
            for i in chunk_start..chunk_end {
                if let Some(v) = self.get_vector(i) {
                    let score = compute_similarity_simd(query, v, metric);
                    
                    // EARLY TERMINATION AGRESSIVO: Skip se score muito baixo
                    if best_scores.len() == k && score <= min_score_threshold {
                        skipped_count += 1;
                        continue;
                    }
                    
                    // Update heap
                    if best_scores.len() < k {
                        best_scores.push(Reverse((OrderedFloat(score), i)));
                        
                        // Update threshold quando heap fica cheio
                        if best_scores.len() == k {
                            if let Some(&Reverse((ref min_heap_score, _))) = best_scores.peek() {
                                min_score_threshold = min_heap_score.0;
                            }
                        }
                    } else if score > min_score_threshold {
                        // Remove pior e adiciona novo
                        best_scores.pop();
                        best_scores.push(Reverse((OrderedFloat(score), i)));
                        
                        // Update threshold
                        if let Some(&Reverse((ref min_heap_score, _))) = best_scores.peek() {
                            min_score_threshold = min_heap_score.0;
                        }
                    }
                }
            }
            
            // EARLY STOPPING mais agressivo
            if best_scores.len() == k && skipped_count > chunk_size / 2 {
                // Se estamos a skip mais de metade dos vectores, podemos parar
                let processed_so_far = chunk_end;
                let remaining = self.rows - processed_so_far;
                
                // Para mais de 75% do dataset processado, pode parar
                if processed_so_far > (self.rows * 3) / 4 {
                    break;
                }
                
                // Se threshold está muito alto, pode parar
                if min_score_threshold > 0.8 && remaining < self.rows / 4 {
                    break;
                }
            }
        }
        
        // Convert heap to final result
        let mut result: Vec<_> = best_scores.into_iter()
            .map(|Reverse((OrderedFloat(score), idx))| (idx, score))
            .collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        Ok(result)
    }
    
    /// Scalar-optimized query processing
    fn query_scalar_optimized(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        let mut scores = Vec::with_capacity(self.rows);
        
        for i in 0..self.rows {
            if let Some(v) = self.get_vector(i) {
                let score = compute_similarity(query, v, metric);
                scores.push((i, score));
            }
        }
        
        self.select_top_k_optimized(scores, k)
    }

    // ==================== BATCH PROCESSING METHODS ====================

    /// Batch query with optimizations
    pub fn query_batch_optimized(&self, queries: &[&[f32]], k: usize) -> Result<Vec<QueryResult>, String> {
        if queries.is_empty() {
            return Ok(Vec::new());
        }
        
        // Verify dimensions
        for query in queries {
            if query.len() != self.dims {
                return Err(format!("Query dimensions {} don't match index dimensions {}", query.len(), self.dims));
            }
        }
        
        // Process sequentially for now (can be improved with rayon later)
        let mut results = Vec::with_capacity(queries.len());
        for query in queries {
            let result = if query.len() >= SIMD_THRESHOLD {
                self.query_exact_simd_optimized(query, k)?
            } else {
                self.query_exact(query, k)?
            };
            results.push(result);
        }
        
        Ok(results)
    }

    /// Batch query with shared computation
    pub fn query_batch_shared_computation(&self, queries: &[&[f32]], k: usize) -> Result<Vec<QueryResult>, String> {
        let start = Instant::now();
        
        // Pre-compute norms and prepare shared structures
        let normalized_queries: Vec<Vec<f32>> = queries
            .iter()
            .map(|query| {
                let norm = query.iter().map(|x| x * x).sum::<f32>().sqrt();
                if norm > 0.0 {
                    query.iter().map(|x| x / norm).collect()
                } else {
                    query.to_vec()
                }
            })
            .collect();
        
        // Shared vector processing
        let all_results = self.process_shared_vectors(&normalized_queries, k)?;
        
        let total_time = start.elapsed().as_secs_f64() * 1000.0;
        let avg_time_per_query = total_time / queries.len() as f64;
        
        // Build QueryResults
        let query_results: Vec<QueryResult> = all_results
            .into_iter()
            .map(|results| QueryResult {
                results,
                query_time_ms: avg_time_per_query,
                method_used: "batch_shared".to_string(),
                candidates_generated: self.rows,
                simd_used: self.dims >= SIMD_THRESHOLD,
            })
            .collect();
        
        Ok(query_results)
    }

    /// Process shared vectors
    fn process_shared_vectors(&self, normalized_queries: &[Vec<f32>], k: usize) -> Result<Vec<Vec<(usize, f32)>>, String> {
        let num_queries = normalized_queries.len();
        let mut all_scores: Vec<Vec<(usize, f32)>> = vec![Vec::with_capacity(self.rows); num_queries];
        
        // Process all vectors against all queries simultaneously
        for i in 0..self.rows {
            if let Some(vector) = self.get_vector(i) {
                for (query_idx, query) in normalized_queries.iter().enumerate() {
                    let score = compute_similarity_simd(query, vector, &SimilarityMetric::Cosine);
                    all_scores[query_idx].push((i, score));
                }
            }
        }
        
        // Top-K selection
        let mut final_results = Vec::with_capacity(num_queries);
        for scores in all_scores {
            let top_k_results = self.select_top_k_optimized(scores, k)?;
            final_results.push(top_k_results);
        }
        
        Ok(final_results)
    }

    // ==================== TOP-K SELECTION METHODS ====================
    
    /// Função principal que substitui select_top_k antigo
    pub fn select_top_k(&self, scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        self.select_top_k_optimized(scores, k)
    }

    /// Heap-based top-k selection - O(n log k) em vez de O(n log n)
    pub fn select_top_k_optimized(&self, scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        if k == 0 {
            return Ok(Vec::new());
        }
        
        if k >= scores.len() {
            // Se k >= n, só precisamos ordenar tudo
            let mut sorted_scores = scores;
            sorted_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            return Ok(sorted_scores);
        }
        
        // Escolher algoritmo baseado no tamanho de k
        if k <= 32 {
            // Para k pequeno: selection sort parcial é mais rápido
            self.partial_sort_small_k(scores, k)
        } else if k <= scores.len() / 4 {
            // Para k médio: usar min-heap O(n log k)
            self.heap_based_selection(scores, k)
        } else {
            // Para k grande: quickselect + sort parcial
            self.quickselect_based_selection(scores, k)
        }
    }
    
    /// Min-heap approach para k médio - O(n log k)
    fn heap_based_selection(&self, scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        // Min-heap para manter apenas os top-k scores
        let mut heap = BinaryHeap::with_capacity(k + 1);
        
        for (idx, score) in scores {
            if heap.len() < k {
                // Heap ainda não está cheio
                heap.push(Reverse((OrderedFloat(score), idx)));
            } else {
                // Heap está cheio, verificar se novo score é melhor que o pior
                if let Some(&Reverse((ref min_score, _))) = heap.peek() {
                    if score > min_score.0 {
                        heap.pop(); // Remove o pior
                        heap.push(Reverse((OrderedFloat(score), idx))); // Adiciona o novo
                    }
                }
            }
        }
        
        // Converter heap para vector ordenado (melhor para pior)
        let mut result: Vec<_> = heap.into_iter()
            .map(|Reverse((OrderedFloat(score), idx))| (idx, score))
            .collect();
        
        // Ordenar resultado final (melhor primeiro)
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        Ok(result)
    }
    
    /// Selection sort parcial para k muito pequeno - O(k * n)
    fn partial_sort_small_k(&self, mut scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        let len = scores.len();
        let k = k.min(len);
        
        // Selection sort apenas para os primeiros k elementos
        for i in 0..k {
            let mut max_idx = i;
            
            // Encontrar o máximo no resto do array
            for j in (i + 1)..len {
                if scores[j].1 > scores[max_idx].1 {
                    max_idx = j;
                }
            }
            
            // Swap se necessário
            if max_idx != i {
                scores.swap(i, max_idx);
            }
        }
        
        // Retornar apenas os k primeiros (já ordenados)
        Ok(scores[..k].to_vec())
    }
    
    /// Quickselect para k grande - O(n) + O(k log k)
    fn quickselect_based_selection(&self, mut scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        let scores_len = scores.len();
        
        if scores_len == 0 {
            return Ok(Vec::new());
        }
        
        if scores_len <= k {
            // Se temos menos scores que k, retornar todos ordenados
            scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            return Ok(scores);
        }
        
        self.quickselect(&mut scores, 0, scores_len - 1, k - 1);
        
        // Ordenar apenas os primeiros k elementos
        scores[..k].sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        Ok(scores[..k].to_vec())
    }
    
    /// Quickselect implementation
    fn quickselect(&self, scores: &mut [(usize, f32)], left: usize, right: usize, k: usize) {
        if left >= right {
            return;
        }
        
        let pivot_index = self.partition(scores, left, right);
        
        if pivot_index == k {
            return; // Found!
        } else if pivot_index > k {
            if pivot_index > 0 {
                self.quickselect(scores, left, pivot_index - 1, k);
            }
        } else {
            self.quickselect(scores, pivot_index + 1, right, k);
        }
    }
    
    /// Partition for quickselect (arrange around pivot)
    fn partition(&self, scores: &mut [(usize, f32)], left: usize, right: usize) -> usize {
        let pivot_value = scores[right].1;
        let mut i = left;
        
        for j in left..right {
            // Comparar em ordem descendente (maior primeiro)
            if scores[j].1 > pivot_value {
                scores.swap(i, j);
                i += 1;
            }
        }
        
        scores.swap(i, right);
        i
    }

    // ==================== UTILITY METHODS ====================
    
    /// Prefetch vector for better cache performance
    #[inline(always)]
    fn prefetch_vector(&self, idx: usize) {
        if idx < self.rows {
            let start_byte = 8 + idx * self.dims * 4;
            unsafe {
                #[cfg(target_arch = "x86_64")]
                {
                    std::arch::x86_64::_mm_prefetch(
                        self.data.as_ptr().add(start_byte) as *const i8,
                        std::arch::x86_64::_MM_HINT_T0
                    );
                }
            }
        }
    }
    
    /// Legacy batch query method for compatibility
    pub fn query_batch(&self, queries: &[&[f32]], k: usize) -> Result<Vec<QueryResult>, String> {
        self.query_batch_optimized(queries, k)
    }
}