use std::fs::File;
use std::time::Instant;
use std::sync::Arc;
use memmap2::Mmap;

use crate::utils::vector::{SimilarityMetric, compute_similarity};
use crate::utils::simd::*;
use crate::utils::memory::*;
use crate::utils::profiling::*;

// ==================== CONSTANTS ====================
const PARALLEL_THRESHOLD: usize = 10000; 
const CHUNK_SIZE: usize = 1000; 
const PREFETCH_DISTANCE: usize = 64;
const SIMD_THRESHOLD: usize = 64;
const OPTIMAL_CHUNK_SIZE: usize = 1024; // Optimal chunk for cache locality

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
        
        let _elapsed = start.elapsed().as_secs_f64();
        
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
    
    /// Main query method with automatic algorithm selection
    pub fn query_exact(&self, query: &[f32], k: usize) -> Result<QueryResult, String> {
        let start = Instant::now();
        
        if query.len() != self.dims {
            return Err(format!("Query dimensions {} don't match index dimensions {}", query.len(), self.dims));
        }
        
        let simd_used = query.len() >= SIMD_THRESHOLD;
        let use_parallel = self.rows >= PARALLEL_THRESHOLD;
        
        let results = if use_parallel {
            self.query_parallel(query, k, &SimilarityMetric::Cosine)?
        } else if simd_used {
            self.query_simd_optimized(query, k, &SimilarityMetric::Cosine)?
        } else {
            self.query_scalar_optimized(query, k, &SimilarityMetric::Cosine)?
        };
        
        let ms = start.elapsed().as_secs_f64() * 1000.0;
        self.metrics.record_query(ms as u64, simd_used);
        
        Ok(QueryResult {
            results, 
            query_time_ms: ms, 
            method_used: if use_parallel { "parallel" } else if simd_used { "simd" } else { "scalar" }.to_string(),
            candidates_generated: self.rows, 
            simd_used
        })
    }

    /// Query with detailed timing information
    pub fn query_exact_with_detailed_timing(&self, query: &[f32], k: usize) -> Result<(Vec<(usize, f32)>, f64), String> {
        let start = Instant::now();
        
        let simd_used = query.len() >= SIMD_THRESHOLD;
        let use_parallel = self.rows >= PARALLEL_THRESHOLD;
        
        let sort_start = Instant::now();
        let results = if use_parallel {
            self.query_parallel(query, k, &SimilarityMetric::Cosine)?
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

    /// 🚀 Query exact with SIMD optimizations specifically for batch processing
    pub fn query_exact_simd_optimized(&self, query: &[f32], k: usize) -> Result<QueryResult, String> {
        let start = Instant::now();
        
        if query.len() != self.dims {
            return Err(format!("Query dimensions {} don't match index dimensions {}", query.len(), self.dims));
        }
        
        // ✨ OTIMIZAÇÃO: Cache-friendly processing
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
        
        self.select_top_k(scores, k)
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
        
        self.select_top_k(scores, k)
    }

    /// 🚀 SIMD processing with cache optimizations
    fn query_simd_cache_optimized(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        let mut scores = Vec::with_capacity(self.rows);
        
        // ✨ OTIMIZAÇÃO 1: Process in cache-friendly chunks
        for chunk_start in (0..self.rows).step_by(OPTIMAL_CHUNK_SIZE) {
            let chunk_end = (chunk_start + OPTIMAL_CHUNK_SIZE).min(self.rows);
            
            // ✨ OTIMIZAÇÃO 2: Prefetch multiple cache lines
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
    
    /// Scalar-optimized query processing
    fn query_scalar_optimized(&self, query: &[f32], k: usize, metric: &SimilarityMetric) -> Result<Vec<(usize, f32)>, String> {
        let mut scores = Vec::with_capacity(self.rows);
        
        for i in 0..self.rows {
            if let Some(v) = self.get_vector(i) {
                let score = compute_similarity(query, v, metric);
                scores.push((i, score));
            }
        }
        
        self.select_top_k(scores, k)
    }

    // ==================== BATCH PROCESSING METHODS ====================

    /// 🚀 Batch query with optimizations
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

    /// 🚀 Batch query with shared computation
    pub fn query_batch_shared_computation(&self, queries: &[&[f32]], k: usize) -> Result<Vec<QueryResult>, String> {
        let start = Instant::now();
        
        // ✨ OTIMIZAÇÃO: Pre-compute norms and prepare shared structures
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
        
        // ✨ OTIMIZAÇÃO: Shared vector processing
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

    /// 🚀 Process shared vectors
    fn process_shared_vectors(&self, normalized_queries: &[Vec<f32>], k: usize) -> Result<Vec<Vec<(usize, f32)>>, String> {
        let num_queries = normalized_queries.len();
        let mut all_scores: Vec<Vec<(usize, f32)>> = vec![Vec::with_capacity(self.rows); num_queries];
        
        // ✨ OTIMIZAÇÃO: Process all vectors against all queries simultaneously
        for i in 0..self.rows {
            if let Some(vector) = self.get_vector(i) {
                for (query_idx, query) in normalized_queries.iter().enumerate() {
                    let score = compute_similarity_simd(query, vector, &SimilarityMetric::Cosine);
                    all_scores[query_idx].push((i, score));
                }
            }
        }
        
        // ✨ OTIMIZAÇÃO: Top-K selection
        let mut final_results = Vec::with_capacity(num_queries);
        for scores in all_scores {
            let top_k_results = self.select_top_k_optimized(scores, k)?;
            final_results.push(top_k_results);
        }
        
        Ok(final_results)
    }

    // ==================== TOP-K SELECTION METHODS ====================
    
    /// Standard top-k selection
    fn select_top_k(&self, mut scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        if k >= scores.len() {
            scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            return Ok(scores);
        }
        
        // Use pdqselect for efficient k-selection
        pdqselect::select_by(&mut scores, k, |a, b| {
            b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal)
        });
        
        scores.truncate(k);
        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        Ok(scores)
    }

    /// 🚀 Optimized top-k selection for batch processing
    fn select_top_k_optimized(&self, mut scores: Vec<(usize, f32)>, k: usize) -> Result<Vec<(usize, f32)>, String> {
        if k >= scores.len() {
            scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            return Ok(scores);
        }
        
        // ✨ OTIMIZAÇÃO: Use different algorithms based on k size
        if k <= 32 {
            // For small k, partial selection sort is faster
            self.partial_sort_small_k(&mut scores, k)
        } else {
            // For larger k, use quickselect
            pdqselect::select_by(&mut scores, k, |a, b| {
                b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal)
            });
            
            scores.truncate(k);
            scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
            Ok(scores)
        }
    }
    
    /// 🚀 Partial selection sort for small k
    fn partial_sort_small_k(&self, scores: &mut [(usize, f32)], k: usize) -> Result<Vec<(usize, f32)>, String> {
        let len = scores.len();
        
        // Selection sort only for the first k elements
        for i in 0..k.min(len) {
            let mut max_idx = i;
            
            for j in (i + 1)..len {
                if scores[j].1 > scores[max_idx].1 {
                    max_idx = j;
                }
            }
            
            if max_idx != i {
                scores.swap(i, max_idx);
            }
        }
        
        Ok(scores[..k.min(len)].to_vec())
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

