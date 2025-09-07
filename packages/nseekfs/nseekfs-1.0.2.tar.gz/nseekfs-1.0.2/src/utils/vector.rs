



use std::fmt;
use std::collections::HashMap;


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum SimilarityMetric {
    Cosine,
    DotProduct,
    Euclidean,
}

impl fmt::Display for SimilarityMetric {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SimilarityMetric::Cosine => write!(f, "cosine"),
            SimilarityMetric::DotProduct => write!(f, "dot_product"),
            SimilarityMetric::Euclidean => write!(f, "euclidean"),
        }
    }
}

impl SimilarityMetric {
    pub fn from_str(s: &str) -> Result<Self, String> {
        match s.to_lowercase().as_str() {
            "cosine" | "cos" => Ok(SimilarityMetric::Cosine),
            "dot" | "dot_product" | "dotproduct" => Ok(SimilarityMetric::DotProduct),
            "euclidean" | "l2" | "euclidian" => Ok(SimilarityMetric::Euclidean),
            _ => Err(format!("Unknown similarity metric: {}", s)),
        }
    }
    
    pub fn requires_normalization(&self) -> bool {
        matches!(self, SimilarityMetric::Cosine)
    }
    
    pub fn is_distance_metric(&self) -> bool {
        matches!(self, SimilarityMetric::Euclidean)
    }
}


pub fn compute_similarity(a: &[f32], b: &[f32], metric: &SimilarityMetric) -> f32 {
    debug_assert_eq!(a.len(), b.len(), "Vector dimensions must match");
    
    match metric {
        SimilarityMetric::Cosine => cosine_similarity(a, b),
        SimilarityMetric::DotProduct => dot_product(a, b),
        SimilarityMetric::Euclidean => -euclidean_distance(a, b), 
    }
}


pub fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    let mut dot_product = 0.0;
    let mut norm_a = 0.0;
    let mut norm_b = 0.0;
    
    
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    
    for i in 0..chunks {
        let idx = i * 4;
        
        let a0 = a[idx];
        let a1 = a[idx + 1];
        let a2 = a[idx + 2];
        let a3 = a[idx + 3];
        
        let b0 = b[idx];
        let b1 = b[idx + 1];
        let b2 = b[idx + 2];
        let b3 = b[idx + 3];
        
        dot_product += a0 * b0 + a1 * b1 + a2 * b2 + a3 * b3;
        norm_a += a0 * a0 + a1 * a1 + a2 * a2 + a3 * a3;
        norm_b += b0 * b0 + b1 * b1 + b2 * b2 + b3 * b3;
    }
    
    
    for i in 0..remainder {
        let idx = chunks * 4 + i;
        dot_product += a[idx] * b[idx];
        norm_a += a[idx] * a[idx];
        norm_b += b[idx] * b[idx];
    }
    
    let norm_product = (norm_a * norm_b).sqrt();
    if norm_product == 0.0 {
        0.0
    } else {
        dot_product / norm_product
    }
}


pub fn dot_product(a: &[f32], b: &[f32]) -> f32 {
    
    let len = a.len();
    let chunks = len / 8;
    let remainder = len % 8;
    
    let mut sum = 0.0;
    
    
    for i in 0..chunks {
        let idx = i * 8;
        sum += a[idx] * b[idx] + 
               a[idx + 1] * b[idx + 1] + 
               a[idx + 2] * b[idx + 2] + 
               a[idx + 3] * b[idx + 3] +
               a[idx + 4] * b[idx + 4] + 
               a[idx + 5] * b[idx + 5] + 
               a[idx + 6] * b[idx + 6] + 
               a[idx + 7] * b[idx + 7];
    }
    
    
    for i in 0..remainder {
        let idx = chunks * 8 + i;
        sum += a[idx] * b[idx];
    }
    
    sum
}


pub fn euclidean_distance(a: &[f32], b: &[f32]) -> f32 {
    
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    let mut sum = 0.0;
    
    
    for i in 0..chunks {
        let idx = i * 4;
        
        let diff0 = a[idx] - b[idx];
        let diff1 = a[idx + 1] - b[idx + 1];
        let diff2 = a[idx + 2] - b[idx + 2];
        let diff3 = a[idx + 3] - b[idx + 3];
        
        sum += diff0 * diff0 + diff1 * diff1 + diff2 * diff2 + diff3 * diff3;
    }
    
    
    for i in 0..remainder {
        let idx = chunks * 4 + i;
        let diff = a[idx] - b[idx];
        sum += diff * diff;
    }
    
    sum.sqrt()
}


pub fn normalize_vector_inplace(vector: &mut [f32]) {
    let norm_squared: f32 = vector.iter().map(|&x| x * x).sum();
    let norm = norm_squared.sqrt();
    
    if norm > f32::EPSILON {
        let inv_norm = 1.0 / norm;
        for x in vector.iter_mut() {
            *x *= inv_norm;
        }
    }
}


pub fn normalize_vector(vector: &[f32]) -> Vec<f32> {
    let norm_squared: f32 = vector.iter().map(|&x| x * x).sum();
    let norm = norm_squared.sqrt();
    
    if norm > f32::EPSILON {
        let inv_norm = 1.0 / norm;
        vector.iter().map(|&x| x * inv_norm).collect()
    } else {
        vector.to_vec()
    }
}


pub fn compute_similarities_batch(queries: &[&[f32]], 
                                 vectors: &[&[f32]], 
                                 metric: &SimilarityMetric) -> Vec<Vec<f32>> {
    use rayon::prelude::*;
    
    queries.par_iter().map(|&query| {
        vectors.iter().map(|&vector| {
            compute_similarity(query, vector, metric)
        }).collect()
    }).collect()
}


pub fn normalize_vectors_batch(vectors: &mut [Vec<f32>]) {
    use rayon::prelude::*;
    
    vectors.par_iter_mut().for_each(|vector| {
        normalize_vector_inplace(vector);
    });
}


pub fn validate_vectors(vectors: &[&[f32]], expected_dims: usize) -> Result<(), String> {
    for (i, &vector) in vectors.iter().enumerate() {
        if vector.len() != expected_dims {
            return Err(format!(
                "Vector {} has {} dimensions, expected {}", 
                i, vector.len(), expected_dims
            ));
        }
        
        
        for (j, &value) in vector.iter().enumerate() {
            if !value.is_finite() {
                return Err(format!(
                    "Vector {} contains invalid value {} at position {}", 
                    i, value, j
                ));
            }
        }
    }
    
    Ok(())
}


#[derive(Debug, Clone)]
pub struct VectorStats {
    pub mean: f32,
    pub std_dev: f32,
    pub min: f32,
    pub max: f32,
    pub l2_norm: f32,
}

impl VectorStats {
    pub fn compute(vector: &[f32]) -> Self {
        if vector.is_empty() {
            return Self {
                mean: 0.0,
                std_dev: 0.0,
                min: 0.0,
                max: 0.0,
                l2_norm: 0.0,
            };
        }
        
        let sum: f32 = vector.iter().sum();
        let mean = sum / vector.len() as f32;
        
        let variance: f32 = vector.iter()
            .map(|&x| (x - mean).powi(2))
            .sum::<f32>() / vector.len() as f32;
        let std_dev = variance.sqrt();
        
        let min = vector.iter().fold(f32::INFINITY, |a, &b| a.min(b));
        let max = vector.iter().fold(f32::NEG_INFINITY, |a, &b| a.max(b));
        
        let l2_norm = vector.iter().map(|&x| x * x).sum::<f32>().sqrt();
        
        Self { mean, std_dev, min, max, l2_norm }
    }
}


pub fn compute_pairwise_distances(vectors: &[&[f32]], metric: &SimilarityMetric) -> Vec<Vec<f32>> {
    let n = vectors.len();
    let mut distances = vec![vec![0.0; n]; n];
    
    for i in 0..n {
        for j in (i + 1)..n {
            let dist = compute_similarity(vectors[i], vectors[j], metric);
            distances[i][j] = dist;
            distances[j][i] = dist; 
        }
        distances[i][i] = match metric {
            SimilarityMetric::Cosine | SimilarityMetric::DotProduct => 1.0,
            SimilarityMetric::Euclidean => 0.0,
        };
    }
    
    distances
}

pub fn find_centroid(vectors: &[&[f32]]) -> Vec<f32> {
    if vectors.is_empty() {
        return Vec::new();
    }
    
    let dims = vectors[0].len();
    let mut centroid = vec![0.0; dims];
    
    for &vector in vectors {
        for (i, &value) in vector.iter().enumerate() {
            centroid[i] += value;
        }
    }
    
    let n = vectors.len() as f32;
    for value in &mut centroid {
        *value /= n;
    }
    
    centroid
}

pub fn compute_variance(vectors: &[&[f32]]) -> f32 {
    if vectors.len() < 2 {
        return 0.0;
    }
    
    let centroid = find_centroid(vectors);
    let mut total_variance = 0.0;
    
    for &vector in vectors {
        let distance = euclidean_distance(vector, &centroid);
        total_variance += distance * distance;
    }
    
    total_variance / vectors.len() as f32
}


pub fn compute_silhouette_coefficient(vectors: &[&[f32]], 
                                    labels: &[usize], 
                                    metric: &SimilarityMetric) -> Vec<f32> {
    let n = vectors.len();
    let mut silhouettes = vec![0.0; n];
    
    for i in 0..n {
        let cluster_i = labels[i];
        
        
        let mut intra_distances = Vec::new();
        for j in 0..n {
            if i != j && labels[j] == cluster_i {
                let dist = match metric {
                    SimilarityMetric::Euclidean => euclidean_distance(vectors[i], vectors[j]),
                    _ => 1.0 - compute_similarity(vectors[i], vectors[j], metric),
                };
                intra_distances.push(dist);
            }
        }
        
        let a_i = if intra_distances.is_empty() {
            0.0
        } else {
            intra_distances.iter().sum::<f32>() / intra_distances.len() as f32
        };
        
        
        let mut cluster_distances = HashMap::new();
        for j in 0..n {
            if labels[j] != cluster_i {
                let dist = match metric {
                    SimilarityMetric::Euclidean => euclidean_distance(vectors[i], vectors[j]),
                    _ => 1.0 - compute_similarity(vectors[i], vectors[j], metric),
                };
                cluster_distances.entry(labels[j])
                    .and_modify(|distances: &mut Vec<f32>| distances.push(dist))
                    .or_insert_with(|| vec![dist]);
            }
        }
        
        let b_i = cluster_distances.values()
            .map(|distances| distances.iter().sum::<f32>() / distances.len() as f32)
            .min_by(|a, b| a.partial_cmp(b).unwrap())
            .unwrap_or(0.0);
        
        
        silhouettes[i] = if a_i.max(b_i) > 0.0 {
            (b_i - a_i) / a_i.max(b_i)
        } else {
            0.0
        };
    }
    
    silhouettes
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_cosine_similarity() {
        let a = vec![1.0, 0.0, 0.0];
        let b = vec![1.0, 0.0, 0.0];
        let similarity = cosine_similarity(&a, &b);
        assert!((similarity - 1.0).abs() < 1e-6);
        
        let c = vec![0.0, 1.0, 0.0];
        let similarity = cosine_similarity(&a, &c);
        assert!((similarity - 0.0).abs() < 1e-6);
    }
    
    #[test]
    fn test_dot_product() {
        let a = vec![1.0, 2.0, 3.0];
        let b = vec![4.0, 5.0, 6.0];
        let dot = dot_product(&a, &b);
        assert!((dot - 32.0).abs() < 1e-6); 
    }
    
    #[test]
    fn test_euclidean_distance() {
        let a = vec![0.0, 0.0, 0.0];
        let b = vec![3.0, 4.0, 0.0];
        let dist = euclidean_distance(&a, &b);
        assert!((dist - 5.0).abs() < 1e-6); 
    }
    
    #[test]
    fn test_normalize_vector() {
        let vector = vec![3.0, 4.0, 0.0];
        let normalized = normalize_vector(&vector);
        let norm = normalized.iter().map(|&x| x * x).sum::<f32>().sqrt();
        assert!((norm - 1.0).abs() < 1e-6);
    }
}