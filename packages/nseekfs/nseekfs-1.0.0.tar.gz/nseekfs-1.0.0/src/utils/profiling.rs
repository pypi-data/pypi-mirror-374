use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

// ==================== PERFORMANCE STATISTICS ====================

#[derive(Debug, Clone)]
pub struct QueryProfile {
    pub total_time: Duration,
    pub parse_time: Duration,
    pub compute_time: Duration,
    pub simd_time: Duration,
    pub sort_time: Duration,
    pub candidates_examined: usize,
    pub simd_chunks_processed: usize,
    pub cache_hits: usize,
    pub cache_misses: usize,
}

#[derive(Debug, Clone)]
pub struct PerformanceStats {
    pub total_queries: u64,
    pub avg_query_time_ms: f64,
    pub median_query_time_ms: f64,
    pub p95_query_time_ms: f64,
    pub p99_query_time_ms: f64,
    pub simd_queries: u64,
    pub scalar_queries: u64,
    pub queries_per_second: f64,
    pub memory_usage_mb: f64,
    pub cache_hit_rate: f64,
}

#[derive(Debug, Clone)]
struct CacheStats {
    hits: u64,
    misses: u64,
    evictions: u64,
}

// ==================== PERFORMANCE METRICS ====================

#[derive(Debug)]
pub struct PerformanceMetrics {
    query_times: Arc<Mutex<Vec<u64>>>, 
    simd_usage: Arc<Mutex<HashMap<String, u64>>>,
    cache_stats: Arc<Mutex<CacheStats>>,
    batch_stats: Arc<Mutex<BatchStats>>, // ✨ NEW: Batch-specific metrics
    start_time: Instant,
}

#[derive(Debug, Clone)]
struct BatchStats {
    total_batches: u64,
    total_queries_in_batches: u64,
    avg_batch_efficiency: f64,
    max_batch_size: usize,
    avg_batch_size: f64,
}

impl PerformanceMetrics {
    pub fn new() -> Self {
        Self {
            query_times: Arc::new(Mutex::new(Vec::new())),
            simd_usage: Arc::new(Mutex::new(HashMap::new())),
            cache_stats: Arc::new(Mutex::new(CacheStats { hits: 0, misses: 0, evictions: 0 })),
            batch_stats: Arc::new(Mutex::new(BatchStats {
                total_batches: 0,
                total_queries_in_batches: 0,
                avg_batch_efficiency: 1.0,
                max_batch_size: 0,
                avg_batch_size: 1.0,
            })),
            start_time: Instant::now(),
        }
    }
    
    /// Record a single query
    pub fn record_query(&self, time_microseconds: u64, simd_used: bool) {
        // Record timing
        if let Ok(mut times) = self.query_times.try_lock() {
            times.push(time_microseconds);
            
            // Keep only recent queries to prevent unbounded growth
            if times.len() > 10_000 {
                times.drain(0..5_000);
            }
        }
        
        // Record SIMD usage
        if let Ok(mut simd_stats) = self.simd_usage.try_lock() {
            let key = if simd_used { "simd" } else { "scalar" };
            *simd_stats.entry(key.to_string()).or_insert(0) += 1;
        }
    }
    
    /// 🚀 NEW: Record batch query metrics
    pub fn record_batch_query(&self, total_time_ms: u64, num_queries: usize, efficiency: f64) {
        // Record individual query times (approximate)
        let avg_time_per_query = if num_queries > 0 {
            (total_time_ms * 1000) / num_queries as u64 // Convert to microseconds
        } else {
            total_time_ms * 1000
        };
        
        // Record each query in the batch
        for _ in 0..num_queries {
            self.record_query(avg_time_per_query, true); // Assume SIMD for batches
        }
        
        // Record batch-specific metrics
        if let Ok(mut batch_stats) = self.batch_stats.try_lock() {
            batch_stats.total_batches += 1;
            batch_stats.total_queries_in_batches += num_queries as u64;
            batch_stats.max_batch_size = batch_stats.max_batch_size.max(num_queries);
            
            // Update average batch size (running average)
            let total_queries = batch_stats.total_queries_in_batches as f64;
            let total_batches = batch_stats.total_batches as f64;
            batch_stats.avg_batch_size = total_queries / total_batches;
            
            // Update average efficiency (running average)
            let prev_avg = batch_stats.avg_batch_efficiency;
            batch_stats.avg_batch_efficiency = 
                (prev_avg * (total_batches - 1.0) + efficiency) / total_batches;
        }
    }
    
    /// Record cache statistics
    pub fn record_cache_hit(&self) {
        if let Ok(mut cache) = self.cache_stats.try_lock() {
            cache.hits += 1;
        }
    }
    
    pub fn record_cache_miss(&self) {
        if let Ok(mut cache) = self.cache_stats.try_lock() {
            cache.misses += 1;
        }
    }
    
    /// Get comprehensive performance statistics
    pub fn get_stats(&self) -> PerformanceStats {
        let times = self.query_times.lock().unwrap().clone();
        let simd_stats = self.simd_usage.lock().unwrap().clone();
        let cache_stats = self.cache_stats.lock().unwrap().clone();
        
        if times.is_empty() {
            return PerformanceStats {
                total_queries: 0,
                avg_query_time_ms: 0.0,
                median_query_time_ms: 0.0,
                p95_query_time_ms: 0.0,
                p99_query_time_ms: 0.0,
                simd_queries: 0,
                scalar_queries: 0,
                queries_per_second: 0.0,
                memory_usage_mb: 0.0,
                cache_hit_rate: 0.0,
            };
        }
        
        let mut sorted_times = times.clone();
        sorted_times.sort_unstable();
        
        let total_queries = times.len() as u64;
        let avg_time_us = times.iter().sum::<u64>() as f64 / times.len() as f64;
        let median_time_us = sorted_times[sorted_times.len() / 2] as f64;
        let p95_time_us = sorted_times[(sorted_times.len() as f64 * 0.95) as usize] as f64;
        let p99_time_us = sorted_times[(sorted_times.len() as f64 * 0.99) as usize] as f64;
        
        let simd_queries = simd_stats.get("simd").unwrap_or(&0).clone();
        let scalar_queries = simd_stats.get("scalar").unwrap_or(&0).clone();
        
        let elapsed_seconds = self.start_time.elapsed().as_secs_f64();
        let qps = if elapsed_seconds > 0.0 { total_queries as f64 / elapsed_seconds } else { 0.0 };
        
        let cache_total = cache_stats.hits + cache_stats.misses;
        let cache_hit_rate = if cache_total > 0 {
            cache_stats.hits as f64 / cache_total as f64
        } else {
            0.0
        };
        
        PerformanceStats {
            total_queries,
            avg_query_time_ms: avg_time_us / 1000.0,
            median_query_time_ms: median_time_us / 1000.0,
            p95_query_time_ms: p95_time_us / 1000.0,
            p99_query_time_ms: p99_time_us / 1000.0,
            simd_queries,
            scalar_queries,
            queries_per_second: qps,
            memory_usage_mb: get_current_memory_usage_mb(),
            cache_hit_rate,
        }
    }
    
    /// Reset all metrics
    pub fn reset(&self) {
        if let Ok(mut times) = self.query_times.try_lock() {
            times.clear();
        }
        if let Ok(mut simd_stats) = self.simd_usage.try_lock() {
            simd_stats.clear();
        }
        if let Ok(mut cache_stats) = self.cache_stats.try_lock() {
            *cache_stats = CacheStats { hits: 0, misses: 0, evictions: 0 };
        }
        if let Ok(mut batch_stats) = self.batch_stats.try_lock() {
            *batch_stats = BatchStats {
                total_batches: 0,
                total_queries_in_batches: 0,
                avg_batch_efficiency: 1.0,
                max_batch_size: 0,
                avg_batch_size: 1.0,
            };
        }
    }

    /// 🚀 NEW: Get batch-specific statistics
    pub fn get_batch_stats(&self) -> Option<BatchStats> {
        self.batch_stats.lock().ok().map(|stats| stats.clone())
    }
}

// ==================== QUERY PROFILER ====================

pub struct QueryProfiler {
    start_time: Instant,
    checkpoints: Vec<(String, Instant)>,
}

impl QueryProfiler {
    pub fn new() -> Self {
        Self {
            start_time: Instant::now(),
            checkpoints: Vec::new(),
        }
    }
    
    pub fn checkpoint(&mut self, name: &str) {
        self.checkpoints.push((name.to_string(), Instant::now()));
    }
    
    pub fn finish(self) -> QueryProfile {
        let total_time = self.start_time.elapsed();
        
        let mut parse_time = Duration::new(0, 0);
        let mut compute_time = Duration::new(0, 0);
        let mut simd_time = Duration::new(0, 0);
        let mut sort_time = Duration::new(0, 0);
        
        let mut prev_time = self.start_time;
        for (name, checkpoint_time) in self.checkpoints {
            let duration = checkpoint_time.duration_since(prev_time);
            
            match name.as_str() {
                "parse_complete" => parse_time = duration,
                "compute_complete" => compute_time = duration,
                "simd_complete" => simd_time = duration,
                "sort_complete" => sort_time = duration,
                _ => {}
            }
            
            prev_time = checkpoint_time;
        }
        
        QueryProfile {
            total_time,
            parse_time,
            compute_time,
            simd_time,
            sort_time,
            candidates_examined: 0, // Would need to be passed in
            simd_chunks_processed: 0,
            cache_hits: 0,
            cache_misses: 0,
        }
    }
}

// ==================== UTILITY FUNCTIONS ====================

fn get_current_memory_usage_mb() -> f64 {
    // Linux-specific memory usage
    #[cfg(target_os = "linux")]
    {
        if let Ok(contents) = std::fs::read_to_string("/proc/self/status") {
            for line in contents.lines() {
                if line.starts_with("VmRSS:") {
                    if let Some(kb_str) = line.split_whitespace().nth(1) {
                        if let Ok(kb) = kb_str.parse::<f64>() {
                            return kb / 1024.0; // Convert KB to MB
                        }
                    }
                }
            }
        }
    }
    
    // Fallback for other platforms
    0.0
}

// ==================== TESTS ====================

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    
    #[test]
    fn test_performance_metrics() {
        let metrics = PerformanceMetrics::new();
        
        metrics.record_query(1000, true);  // 1ms, SIMD
        metrics.record_query(2000, false); // 2ms, scalar
        metrics.record_query(1500, true);  // 1.5ms, SIMD
        
        let stats = metrics.get_stats();
        assert_eq!(stats.total_queries, 3);
        assert_eq!(stats.simd_queries, 2);
        assert_eq!(stats.scalar_queries, 1);
        assert!((stats.avg_query_time_ms - 1.5).abs() < 0.1);
    }
    
    #[test]
    fn test_batch_metrics() {
        let metrics = PerformanceMetrics::new();
        
        // Record a batch of 10 queries taking 50ms total (5x efficiency)
        metrics.record_batch_query(50, 10, 5.0);
        
        let batch_stats = metrics.get_batch_stats().unwrap();
        assert_eq!(batch_stats.total_batches, 1);
        assert_eq!(batch_stats.total_queries_in_batches, 10);
        assert_eq!(batch_stats.max_batch_size, 10);
        assert!((batch_stats.avg_batch_efficiency - 5.0).abs() < 0.1);
    }
    
    #[test]
    fn test_query_profiler() {
        let mut profiler = QueryProfiler::new();
        
        thread::sleep(Duration::from_millis(1));
        profiler.checkpoint("parse_complete");
        
        thread::sleep(Duration::from_millis(2));
        profiler.checkpoint("compute_complete");
        
        let profile = profiler.finish();
        assert!(profile.total_time.as_millis() >= 3);
        assert!(profile.parse_time.as_millis() >= 1);
        assert!(profile.compute_time.as_millis() >= 2);
    }
}