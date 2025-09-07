




use crate::utils::vector::SimilarityMetric;
use crate::utils::simd::{SimdEngine, create_simd_engine};
use rayon::prelude::*;


pub trait SpecializedAlgorithm {
    fn can_handle(&self, dimensions: usize, vectors: usize, metric: &SimilarityMetric) -> bool;
    fn compute_similarities(&self, query: &[f32], vectors: &[&[f32]], metric: &SimilarityMetric) -> Vec<f32>;
    fn name(&self) -> &'static str;
    fn expected_speedup(&self) -> f64;
}


pub struct SmallVectorAlgorithm {
    simd_engine: Box<dyn SimdEngine + Send + Sync>,
}

impl SmallVectorAlgorithm {
    pub fn new() -> Self {
        Self {
            simd_engine: create_simd_engine(),
        }
    }
}

impl SpecializedAlgorithm for SmallVectorAlgorithm {
    fn can_handle(&self, dimensions: usize, _vectors: usize, _metric: &SimilarityMetric) -> bool {
        dimensions <= 64
    }
    
    fn compute_similarities(&self, query: &[f32], vectors: &[&[f32]], metric: &SimilarityMetric) -> Vec<f32> {
        
        
        
        let mut results = Vec::with_capacity(vectors.len());
        
        
        const BATCH_SIZE: usize = 16;
        
        for chunk in vectors.chunks(BATCH_SIZE) {
            for &vector in chunk {
                let similarity = match metric {
                    SimilarityMetric::Cosine => self.simd_engine.cosine_similarity(query, vector),
                    SimilarityMetric::DotProduct => self.simd_engine.dot_product(query, vector),
                    SimilarityMetric::Euclidean => -self.simd_engine.euclidean_distance(query, vector),
                };
                results.push(similarity);
            }
        }
        
        results
    }
    
    fn name(&self) -> &'static str { "SmallVector" }
    fn expected_speedup(&self) -> f64 { 1.2 }
}


pub struct LargeVectorAlgorithm {
    simd_engine: Box<dyn SimdEngine + Send + Sync>,
}

impl LargeVectorAlgorithm {
    pub fn new() -> Self {
        Self {
            simd_engine: create_simd_engine(),
        }
    }
}

impl SpecializedAlgorithm for LargeVectorAlgorithm {
    fn can_handle(&self, dimensions: usize, vectors: usize, _metric: &SimilarityMetric) -> bool {
        dimensions > 512 && vectors > 1000
    }
    
    fn compute_similarities(&self, query: &[f32], vectors: &[&[f32]], metric: &SimilarityMetric) -> Vec<f32> {
        
        const CHUNK_SIZE: usize = 100;
        
        vectors.par_chunks(CHUNK_SIZE)
            .flat_map(|chunk| {
                chunk.iter().map(|&vector| {
                    match metric {
                        SimilarityMetric::Cosine => self.simd_engine.cosine_similarity(query, vector),
                        SimilarityMetric::DotProduct => self.simd_engine.dot_product(query, vector),
                        SimilarityMetric::Euclidean => -self.simd_engine.euclidean_distance(query, vector),
                    }
                })
            })
            .collect()
    }
    
    fn name(&self) -> &'static str { "LargeVector" }
    fn expected_speedup(&self) -> f64 { 2.5 }
}


pub struct CosineSpecializedAlgorithm {
    simd_engine: Box<dyn SimdEngine + Send + Sync>,
}

impl CosineSpecializedAlgorithm {
    pub fn new() -> Self {
        Self {
            simd_engine: create_simd_engine(),
        }
    }
    
    
    fn cosine_similarity_specialized(&self, query: &[f32], vectors: &[&[f32]]) -> Vec<f32> {
        
        let query_norm = {
            let norm_squared: f32 = query.iter().map(|&x| x * x).sum();
            norm_squared.sqrt()
        };
        
        if query_norm == 0.0 {
            return vec![0.0; vectors.len()];
        }
        
        
        let query_normalized: Vec<f32> = query.iter().map(|&x| x / query_norm).collect();
        
        vectors.par_iter().map(|&vector| {
            
            let vector_norm_squared: f32 = vector.iter().map(|&x| x * x).sum();
            let vector_norm = vector_norm_squared.sqrt();
            
            if vector_norm == 0.0 {
                return 0.0;
            }
            
            
            let dot_product: f32 = query_normalized.iter()
                .zip(vector.iter())
                .map(|(&q, &v)| q * v)
                .sum();
            
            dot_product / vector_norm
        }).collect()
    }
}

impl SpecializedAlgorithm for CosineSpecializedAlgorithm {
    fn can_handle(&self, _dimensions: usize, vectors: usize, metric: &SimilarityMetric) -> bool {
        matches!(metric, SimilarityMetric::Cosine) && vectors > 500
    }
    
    fn compute_similarities(&self, query: &[f32], vectors: &[&[f32]], metric: &SimilarityMetric) -> Vec<f32> {
        match metric {
            SimilarityMetric::Cosine => self.cosine_similarity_specialized(query, vectors),
            _ => {
                
                vectors.iter().map(|&vector| {
                    match metric {
                        SimilarityMetric::DotProduct => self.simd_engine.dot_product(query, vector),
                        SimilarityMetric::Euclidean => -self.simd_engine.euclidean_distance(query, vector),
                        _ => 0.0,
                    }
                }).collect()
            }
        }
    }
    
    fn name(&self) -> &'static str { "CosineSpecialized" }
    fn expected_speedup(&self) -> f64 { 1.8 }
}


pub struct BatchOptimizedAlgorithm {
    simd_engine: Box<dyn SimdEngine + Send + Sync>,
}

impl BatchOptimizedAlgorithm {
    pub fn new() -> Self {
        Self {
            simd_engine: create_simd_engine(),
        }
    }
    
    pub fn compute_batch_similarities(&self, 
                                    queries: &[&[f32]], 
                                    vectors: &[&[f32]], 
                                    metric: &SimilarityMetric) -> Vec<Vec<f32>> {
        
        queries.par_iter().map(|&query| {
            self.compute_similarities(query, vectors, metric)
        }).collect()
    }
}

impl SpecializedAlgorithm for BatchOptimizedAlgorithm {
    fn can_handle(&self, _dimensions: usize, vectors: usize, _metric: &SimilarityMetric) -> bool {
        vectors > 10000 
    }
    
    fn compute_similarities(&self, query: &[f32], vectors: &[&[f32]], metric: &SimilarityMetric) -> Vec<f32> {
        
        const LARGE_CHUNK_SIZE: usize = 2000;
        
        vectors.par_chunks(LARGE_CHUNK_SIZE)
            .flat_map(|chunk| {
                
                chunk.iter().enumerate().map(|(i, &vector)| {
                    
                    if i + 1 < chunk.len() {
                        #[cfg(target_arch = "x86_64")]
                        unsafe {
                            std::arch::x86_64::_mm_prefetch(
                                chunk[i + 1].as_ptr() as *const i8,
                                std::arch::x86_64::_MM_HINT_T0
                            );
                        }
                    }
                    
                    match metric {
                        SimilarityMetric::Cosine => self.simd_engine.cosine_similarity(query, vector),
                        SimilarityMetric::DotProduct => self.simd_engine.dot_product(query, vector),
                        SimilarityMetric::Euclidean => -self.simd_engine.euclidean_distance(query, vector),
                    }
                })
            })
            .collect()
    }
    
    fn name(&self) -> &'static str { "BatchOptimized" }
    fn expected_speedup(&self) -> f64 { 3.0 }
}


pub struct AlgorithmSelector {
    algorithms: Vec<Box<dyn SpecializedAlgorithm + Send + Sync>>,
}

impl AlgorithmSelector {
    pub fn new() -> Self {
        let algorithms: Vec<Box<dyn SpecializedAlgorithm + Send + Sync>> = vec![
            Box::new(SmallVectorAlgorithm::new()),
            Box::new(LargeVectorAlgorithm::new()),
            Box::new(CosineSpecializedAlgorithm::new()),
            Box::new(BatchOptimizedAlgorithm::new()),
        ];
        
        Self { algorithms }
    }
    
    pub fn select_best_algorithm(&self, 
                                dimensions: usize, 
                                vectors: usize, 
                                metric: &SimilarityMetric) -> Option<&(dyn SpecializedAlgorithm + Send + Sync)> {
        
        
        let mut candidates: Vec<_> = self.algorithms.iter()
            .filter(|alg| alg.can_handle(dimensions, vectors, metric))
            .collect();
        
        if candidates.is_empty() {
            return None;
        }
        
        
        candidates.sort_by(|a, b| b.expected_speedup().partial_cmp(&a.expected_speedup()).unwrap());
        
        
        candidates.first().map(|alg| alg.as_ref())
    }
    
    pub fn compute_with_best_algorithm(&self,
                                     query: &[f32],
                                     vectors: &[&[f32]], 
                                     metric: &SimilarityMetric) -> (Vec<f32>, &'static str) {
        
        if let Some(algorithm) = self.select_best_algorithm(query.len(), vectors.len(), metric) {
            let results = algorithm.compute_similarities(query, vectors, metric);
            (results, algorithm.name())
        } else {
            
            let default_algorithm = SmallVectorAlgorithm::new();
            let results = default_algorithm.compute_similarities(query, vectors, metric);
            (results, "Default")
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_small_vector_algorithm() {
        let algorithm = SmallVectorAlgorithm::new();
        
        
        assert!(algorithm.can_handle(32, 1000, &SimilarityMetric::Cosine));
        assert!(!algorithm.can_handle(128, 1000, &SimilarityMetric::Cosine));
        
        let query = vec![1.0, 0.0, 0.0, 0.0];
        let vector1 = vec![1.0, 0.0, 0.0, 0.0];
        let vector2 = vec![0.0, 1.0, 0.0, 0.0];
        let vectors = vec![vector1.as_slice(), vector2.as_slice()];
        
        let results = algorithm.compute_similarities(&query, &vectors, &SimilarityMetric::Cosine);
        assert_eq!(results.len(), 2);
        assert!((results[0] - 1.0).abs() < 1e-6); 
        assert!(results[0] > results[1]); 
    }
    
    #[test]
    fn test_algorithm_selector() {
        let selector = AlgorithmSelector::new();
        
        
        let algorithm = selector.select_best_algorithm(32, 1000, &SimilarityMetric::Cosine);
        assert!(algorithm.is_some());
        
        
        let algorithm = selector.select_best_algorithm(1024, 10000, &SimilarityMetric::Cosine);
        assert!(algorithm.is_some());
        
        
        let query = vec![1.0; 64];
        let vector1 = vec![1.0; 64];
        let vector2 = vec![0.5; 64];
        let vectors = vec![vector1.as_slice(), vector2.as_slice()];
        
        let (results, algorithm_name) = selector.compute_with_best_algorithm(
            &query, &vectors, &SimilarityMetric::Cosine
        );
        
        assert_eq!(results.len(), 2);
        assert!(!algorithm_name.is_empty());
    }
    
    #[test]
    fn test_cosine_specialized_algorithm() {
        let algorithm = CosineSpecializedAlgorithm::new();
        
        assert!(algorithm.can_handle(256, 1000, &SimilarityMetric::Cosine));
        assert!(!algorithm.can_handle(256, 100, &SimilarityMetric::Cosine));
        assert!(!algorithm.can_handle(256, 1000, &SimilarityMetric::DotProduct));
        
        let query = vec![1.0, 0.0, 0.0];
        let vector1 = vec![1.0, 0.0, 0.0];
        let vector2 = vec![0.0, 1.0, 0.0];
        let vectors = vec![vector1.as_slice(), vector2.as_slice()];
        
        let results = algorithm.compute_similarities(&query, &vectors, &SimilarityMetric::Cosine);
        assert_eq!(results.len(), 2);
        assert!((results[0] - 1.0).abs() < 1e-6);
        assert!((results[1] - 0.0).abs() < 1e-6);
    }
}