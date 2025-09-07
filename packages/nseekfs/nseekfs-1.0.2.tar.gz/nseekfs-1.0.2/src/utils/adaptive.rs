



use std::collections::HashMap;
use std::time::{Duration, Instant};
use log::{debug, info, warn};
use crate::utils::vector::SimilarityMetric;
use crate::utils::profiling::PerformanceMetrics;


#[derive(Debug, Clone)]
pub struct WorkloadPattern {
    pub avg_query_frequency: f64,  
    pub avg_vector_dimensions: usize,
    pub avg_k_value: usize,
    pub dominant_metric: SimilarityMetric,
    pub batch_size_preference: usize,
    pub memory_pressure: MemoryPressure,
}

#[derive(Debug, Clone)]
pub enum MemoryPressure {
    Low,    
    Medium, 
    High,   
}

#[derive(Debug, Clone)]
pub struct AdaptationConfig {
    pub use_parallel_threshold: usize,
    pub simd_threshold: usize,
    pub prefetch_distance: usize,
    pub chunk_size: usize,
    pub buffer_pool_size: usize,
    pub cache_size: usize,
}

impl Default for AdaptationConfig {
    fn default() -> Self {
        Self {
            use_parallel_threshold: 10_000,
            simd_threshold: 64,
            prefetch_distance: 64,
            chunk_size: 1000,
            buffer_pool_size: 16,
            cache_size: 1024,
        }
    }
}


pub struct AdaptiveEngine {
    config: AdaptationConfig,
    workload_history: WorkloadHistory,
    performance_predictor: PerformancePredictor,
    adaptation_cooldown: Duration,
    last_adaptation: Instant,
}

impl AdaptiveEngine {
    pub fn new() -> Self {
        Self {
            config: AdaptationConfig::default(),
            workload_history: WorkloadHistory::new(),
            performance_predictor: PerformancePredictor::new(),
            adaptation_cooldown: Duration::from_secs(30), 
            last_adaptation: Instant::now(),
        }
    }
    
    pub fn get_config(&self) -> &AdaptationConfig {
        &self.config
    }
    
    pub fn record_query(&mut self, 
                       dimensions: usize, 
                       k: usize, 
                       metric: &SimilarityMetric,
                       execution_time_ms: f64,
                       simd_used: bool) {
        
        self.workload_history.record_query(dimensions, k, metric, execution_time_ms, simd_used);
        
        
        if self.last_adaptation.elapsed() > self.adaptation_cooldown {
            self.adapt_if_needed();
        }
    }
    
    fn adapt_if_needed(&mut self) {
        let pattern = self.workload_history.analyze_pattern();
        let predicted_performance = self.performance_predictor.predict(&pattern, &self.config);
        
        if let Some(new_config) = self.optimize_config(&pattern, predicted_performance) {
            info!("Adapting configuration based on workload pattern");
            debug!("Old config: {:?}", self.config);
            debug!("New config: {:?}", new_config);
            
            self.config = new_config;
            self.last_adaptation = Instant::now();
        }
    }
    
    fn optimize_config(&self, pattern: &WorkloadPattern, current_performance: f64) -> Option<AdaptationConfig> {
        let mut new_config = self.config.clone();
        let mut improved = false;
        
        
        let optimal_parallel_threshold = match pattern.avg_vector_dimensions {
            0..=128 => 20_000,    
            129..=512 => 10_000,  
            513..=1024 => 5_000,  
            _ => 2_000,           
        };
        
        if new_config.use_parallel_threshold != optimal_parallel_threshold {
            new_config.use_parallel_threshold = optimal_parallel_threshold;
            improved = true;
        }
        
        
        let optimal_chunk_size = match pattern.avg_query_frequency {
            f if f > 100.0 => 500,   
            f if f > 50.0 => 1000,   
            f if f > 10.0 => 2000,   
            _ => 5000,               
        };
        
        if new_config.chunk_size != optimal_chunk_size {
            new_config.chunk_size = optimal_chunk_size;
            improved = true;
        }
        
        
        let optimal_simd_threshold = match pattern.dominant_metric {
            SimilarityMetric::Cosine => 32,     
            SimilarityMetric::DotProduct => 64, 
            SimilarityMetric::Euclidean => 96,  
        };
        
        if new_config.simd_threshold != optimal_simd_threshold {
            new_config.simd_threshold = optimal_simd_threshold;
            improved = true;
        }
        
        
        let optimal_buffer_pool_size = match pattern.memory_pressure {
            MemoryPressure::Low => 32,    
            MemoryPressure::Medium => 16, 
            MemoryPressure::High => 8,    
        };
        
        if new_config.buffer_pool_size != optimal_buffer_pool_size {
            new_config.buffer_pool_size = optimal_buffer_pool_size;
            improved = true;
        }
        
        if improved {
            Some(new_config)
        } else {
            None
        }
    }
}


struct WorkloadHistory {
    queries: Vec<QueryRecord>,
    max_history_size: usize,
}

#[derive(Debug, Clone)]
struct QueryRecord {
    timestamp: Instant,
    dimensions: usize,
    k: usize,
    metric: SimilarityMetric,
    execution_time_ms: f64,
    simd_used: bool,
}

impl WorkloadHistory {
    fn new() -> Self {
        Self {
            queries: Vec::new(),
            max_history_size: 10_000,
        }
    }
    
    fn record_query(&mut self, 
                   dimensions: usize, 
                   k: usize, 
                   metric: &SimilarityMetric,
                   execution_time_ms: f64,
                   simd_used: bool) {
        
        self.queries.push(QueryRecord {
            timestamp: Instant::now(),
            dimensions,
            k,
            metric: metric.clone(),
            execution_time_ms,
            simd_used,
        });
        
        
        if self.queries.len() > self.max_history_size {
            self.queries.drain(0..self.max_history_size / 2);
        }
    }
    
    fn analyze_pattern(&self) -> WorkloadPattern {
        if self.queries.is_empty() {
            return WorkloadPattern {
                avg_query_frequency: 0.0,
                avg_vector_dimensions: 512,
                avg_k_value: 10,
                dominant_metric: SimilarityMetric::Cosine,
                batch_size_preference: 1,
                memory_pressure: MemoryPressure::Low,
            };
        }
        
        let recent_queries: Vec<_> = self.queries.iter()
            .rev()
            .take(1000) 
            .collect();
        
        
        let time_span = if recent_queries.len() > 1 {
            recent_queries.first().unwrap().timestamp.duration_since(
                recent_queries.last().unwrap().timestamp
            ).as_secs_f64()
        } else {
            1.0
        };
        
        let avg_query_frequency = if time_span > 0.0 {
            recent_queries.len() as f64 / time_span
        } else {
            0.0
        };
        
        
        let avg_vector_dimensions = recent_queries.iter()
            .map(|q| q.dimensions)
            .sum::<usize>() / recent_queries.len().max(1);
        
        
        let avg_k_value = recent_queries.iter()
            .map(|q| q.k)
            .sum::<usize>() / recent_queries.len().max(1);
        
        
        let mut metric_counts = HashMap::new();
        for query in &recent_queries {
            *metric_counts.entry(query.metric.clone()).or_insert(0) += 1;
        }
        
        let dominant_metric = metric_counts.into_iter()
            .max_by_key(|(_, count)| *count)
            .map(|(metric, _)| metric)
            .unwrap_or(SimilarityMetric::Cosine);
        
        
        let memory_pressure = detect_memory_pressure();
        
        WorkloadPattern {
            avg_query_frequency,
            avg_vector_dimensions,
            avg_k_value,
            dominant_metric,
            batch_size_preference: 1, 
            memory_pressure,
        }
    }
}


struct PerformancePredictor {
    models: HashMap<String, PredictionModel>,
}

#[derive(Debug, Clone)]
struct PredictionModel {
    coefficients: Vec<f64>,
    intercept: f64,
    accuracy: f64,
}

impl PerformancePredictor {
    fn new() -> Self {
        let mut models = HashMap::new();
        
        
        models.insert("query_time".to_string(), PredictionModel {
            coefficients: vec![0.001, 0.00001], 
            intercept: 0.5,
            accuracy: 0.8,
        });
        
        Self { models }
    }
    
    fn predict(&self, pattern: &WorkloadPattern, config: &AdaptationConfig) -> f64 {
        if let Some(model) = self.models.get("query_time") {
            let features = vec![
                pattern.avg_vector_dimensions as f64,
                pattern.avg_k_value as f64,
            ];
            
            let prediction = model.intercept + 
                features.iter()
                    .zip(model.coefficients.iter())
                    .map(|(feature, coef)| feature * coef)
                    .sum::<f64>();
            
            prediction.max(0.1) 
        } else {
            1.0 
        }
    }
    
    fn update_model(&mut self, pattern: &WorkloadPattern, actual_performance: f64) {
        
        
        
        if let Some(model) = self.models.get_mut("query_time") {
            let features = vec![
                pattern.avg_vector_dimensions as f64,
                pattern.avg_k_value as f64,
            ];
            
            let predicted = model.intercept + 
                features.iter()
                    .zip(model.coefficients.iter())
                    .map(|(feature, coef)| feature * coef)
                    .sum::<f64>();
            
            let error = actual_performance - predicted;
            let learning_rate = 0.01;
            
            
            model.intercept += learning_rate * error;
            
            
            for (i, feature) in features.iter().enumerate() {
                model.coefficients[i] += learning_rate * error * feature * 0.001;
            }
        }
    }
}


fn detect_memory_pressure() -> MemoryPressure {
    
    #[cfg(target_os = "linux")]
    {
        if let Ok(meminfo) = std::fs::read_to_string("/proc/meminfo") {
            let mut mem_total = 0u64;
            let mut mem_available = 0u64;
            
            for line in meminfo.lines() {
                if line.starts_with("MemTotal:") {
                    if let Some(kb_str) = line.split_whitespace().nth(1) {
                        mem_total = kb_str.parse().unwrap_or(0);
                    }
                } else if line.starts_with("MemAvailable:") {
                    if let Some(kb_str) = line.split_whitespace().nth(1) {
                        mem_available = kb_str.parse().unwrap_or(0);
                    }
                }
            }
            
            if mem_total > 0 {
                let usage_ratio = 1.0 - (mem_available as f64 / mem_total as f64);
                return match usage_ratio {
                    r if r < 0.5 => MemoryPressure::Low,
                    r if r < 0.8 => MemoryPressure::Medium,
                    _ => MemoryPressure::High,
                };
            }
        }
    }
    
    MemoryPressure::Low 
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_adaptive_engine() {
        let mut engine = AdaptiveEngine::new();
        
        
        for _ in 0..100 {
            engine.record_query(
                1024,  
                10,    
                &SimilarityMetric::Cosine,
                15.0,  
                true   
            );
        }
        
        let config = engine.get_config();
        
        assert!(config.use_parallel_threshold <= 5000);
    }
    
    #[test]
    fn test_workload_pattern_analysis() {
        let mut history = WorkloadHistory::new();
        
        
        for i in 0..50 {
            history.record_query(
                256,
                5,
                &SimilarityMetric::DotProduct,
                2.0,
                true
            );
        }
        
        let pattern = history.analyze_pattern();
        assert_eq!(pattern.avg_vector_dimensions, 256);
        assert_eq!(pattern.avg_k_value, 5);
        assert!(matches!(pattern.dominant_metric, SimilarityMetric::DotProduct));
    }
}