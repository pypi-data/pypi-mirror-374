use crate::utils::vector::SimilarityMetric;

// CPU feature detection with cross-platform support
#[derive(Debug, Clone)]
pub struct CpuFeatures {
    pub avx2: bool,
    pub fma: bool,
    pub sse42: bool,
    pub neon: bool,
}

pub fn get_cpu_features() -> CpuFeatures {
    CpuFeatures {
        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        avx2: is_x86_feature_detected!("avx2"),
        #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
        avx2: false,
        
        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        fma: is_x86_feature_detected!("fma"),
        #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
        fma: false,
        
        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        sse42: is_x86_feature_detected!("sse4.2"),
        #[cfg(not(any(target_arch = "x86", target_arch = "x86_64")))]
        sse42: false,
        
        #[cfg(target_arch = "aarch64")]
        neon: true, // NEON is standard on aarch64
        #[cfg(not(target_arch = "aarch64"))]
        neon: false,
    }
}

// SIMD engine trait
pub trait SimdEngine {
    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f32;
    fn dot_product(&self, a: &[f32], b: &[f32]) -> f32;
    fn euclidean_distance(&self, a: &[f32], b: &[f32]) -> f32;
    fn name(&self) -> &'static str;
}

// AVX2 engine for x86/x86_64
#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
pub struct Avx2Engine;

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
impl SimdEngine for Avx2Engine {
    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f32 {
        debug_assert_eq!(a.len(), b.len());
        
        if a.len() < 8 {
            return cosine_similarity_scalar(a, b);
        }
        
        unsafe { cosine_similarity_avx2(a, b) }
    }
    
    fn dot_product(&self, a: &[f32], b: &[f32]) -> f32 {
        debug_assert_eq!(a.len(), b.len());
        
        if a.len() < 8 {
            return dot_product_scalar(a, b);
        }
        
        unsafe { dot_product_avx2(a, b) }
    }
    
    fn euclidean_distance(&self, a: &[f32], b: &[f32]) -> f32 {
        debug_assert_eq!(a.len(), b.len());
        
        if a.len() < 8 {
            return euclidean_distance_scalar(a, b);
        }
        
        unsafe { euclidean_distance_avx2(a, b) }
    }
    
    fn name(&self) -> &'static str { "AVX2" }
}

// NEON engine for ARM64/Apple Silicon
#[cfg(target_arch = "aarch64")]
pub struct NeonEngine;

#[cfg(target_arch = "aarch64")]
impl SimdEngine for NeonEngine {
    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f32 {
        debug_assert_eq!(a.len(), b.len());
        
        if a.len() < 4 {
            return cosine_similarity_scalar(a, b);
        }
        
        unsafe { cosine_similarity_neon(a, b) }
    }
    
    fn dot_product(&self, a: &[f32], b: &[f32]) -> f32 {
        debug_assert_eq!(a.len(), b.len());
        
        if a.len() < 4 {
            return dot_product_scalar(a, b);
        }
        
        unsafe { dot_product_neon(a, b) }
    }
    
    fn euclidean_distance(&self, a: &[f32], b: &[f32]) -> f32 {
        debug_assert_eq!(a.len(), b.len());
        
        if a.len() < 4 {
            return euclidean_distance_scalar(a, b);
        }
        
        unsafe { euclidean_distance_neon(a, b) }
    }
    
    fn name(&self) -> &'static str { "NEON" }
}

// Scalar engine for any architecture
pub struct ScalarEngine;

impl SimdEngine for ScalarEngine {
    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f32 {
        cosine_similarity_scalar(a, b)
    }
    
    fn dot_product(&self, a: &[f32], b: &[f32]) -> f32 {
        dot_product_scalar(a, b)
    }
    
    fn euclidean_distance(&self, a: &[f32], b: &[f32]) -> f32 {
        euclidean_distance_scalar(a, b)
    }
    
    fn name(&self) -> &'static str { "Scalar" }
}

// Engine creation with automatic detection
pub fn create_simd_engine() -> Box<dyn SimdEngine + Send + Sync> {
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if is_x86_feature_detected!("avx2") {
            Box::new(Avx2Engine)
        } else {
            Box::new(ScalarEngine)
        }
    }
    #[cfg(target_arch = "aarch64")]
    {
        Box::new(NeonEngine)
    }
    #[cfg(not(any(target_arch = "x86", target_arch = "x86_64", target_arch = "aarch64")))]
    {
        Box::new(ScalarEngine)
    }
}

pub fn compute_similarity_simd(a: &[f32], b: &[f32], metric: &SimilarityMetric) -> f32 {
    let engine = create_simd_engine();
    
    match metric {
        SimilarityMetric::Cosine => engine.cosine_similarity(a, b),
        SimilarityMetric::DotProduct => engine.dot_product(a, b),
        SimilarityMetric::Euclidean => engine.euclidean_distance(a, b),
    }
}

// =============================================================================
// AVX2 IMPLEMENTATIONS (x86/x86_64)
// =============================================================================

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2,fma")]
unsafe fn cosine_similarity_avx2(a: &[f32], b: &[f32]) -> f32 {
    use std::arch::x86_64::*;
    
    let len = a.len();
    let chunks = len / 8;
    let remainder = len % 8;
    
    let mut dot_sum = _mm256_setzero_ps();
    let mut norm_a_sum = _mm256_setzero_ps();
    let mut norm_b_sum = _mm256_setzero_ps();
    
    for i in 0..chunks {
        let idx = i * 8;
        
        let va = _mm256_loadu_ps(a.as_ptr().add(idx));
        let vb = _mm256_loadu_ps(b.as_ptr().add(idx));
        
        dot_sum = _mm256_fmadd_ps(va, vb, dot_sum);
        norm_a_sum = _mm256_fmadd_ps(va, va, norm_a_sum);
        norm_b_sum = _mm256_fmadd_ps(vb, vb, norm_b_sum);
    }
    
    let dot_product = horizontal_sum_avx2(dot_sum);
    let norm_a = horizontal_sum_avx2(norm_a_sum);
    let norm_b = horizontal_sum_avx2(norm_b_sum);
    
    // Process remainder
    let (dot_remainder, norm_a_remainder, norm_b_remainder) = if remainder > 0 {
        let start_idx = chunks * 8;
        let mut dot = 0.0f32;
        let mut na = 0.0f32;
        let mut nb = 0.0f32;
        
        for i in 0..remainder {
            let ai = a[start_idx + i];
            let bi = b[start_idx + i];
            dot += ai * bi;
            na += ai * ai;
            nb += bi * bi;
        }
        (dot, na, nb)
    } else {
        (0.0, 0.0, 0.0)
    };
    
    let final_dot = dot_product + dot_remainder;
    let final_norm_a = norm_a + norm_a_remainder;
    let final_norm_b = norm_b + norm_b_remainder;
    
    let norm_product = (final_norm_a * final_norm_b).sqrt();
    if norm_product == 0.0 {
        0.0
    } else {
        final_dot / norm_product
    }
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn dot_product_avx2(a: &[f32], b: &[f32]) -> f32 {
    use std::arch::x86_64::*;
    
    let len = a.len();
    let chunks = len / 8;
    let remainder = len % 8;
    
    let mut sum = _mm256_setzero_ps();
    
    for i in 0..chunks {
        let idx = i * 8;
        let va = _mm256_loadu_ps(a.as_ptr().add(idx));
        let vb = _mm256_loadu_ps(b.as_ptr().add(idx));
        sum = _mm256_fmadd_ps(va, vb, sum);
    }
    
    let mut result = horizontal_sum_avx2(sum);
    
    // Process remainder
    for i in 0..remainder {
        let idx = chunks * 8 + i;
        result += a[idx] * b[idx];
    }
    
    result
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
#[target_feature(enable = "avx2")]
unsafe fn euclidean_distance_avx2(a: &[f32], b: &[f32]) -> f32 {
    use std::arch::x86_64::*;
    
    let len = a.len();
    let chunks = len / 8;
    let remainder = len % 8;
    
    let mut sum = _mm256_setzero_ps();
    
    for i in 0..chunks {
        let idx = i * 8;
        let va = _mm256_loadu_ps(a.as_ptr().add(idx));
        let vb = _mm256_loadu_ps(b.as_ptr().add(idx));
        let diff = _mm256_sub_ps(va, vb);
        sum = _mm256_fmadd_ps(diff, diff, sum);
    }
    
    let mut result = horizontal_sum_avx2(sum);
    
    // Process remainder
    for i in 0..remainder {
        let idx = chunks * 8 + i;
        let diff = a[idx] - b[idx];
        result += diff * diff;
    }
    
    result.sqrt()
}

// =============================================================================
// TESTS
// =============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cosine_similarity_scalar() {
        let a = vec![1.0, 0.0, 0.0];
        let b = vec![1.0, 0.0, 0.0];
        let similarity = cosine_similarity_scalar(&a, &b);
        assert!((similarity - 1.0).abs() < 1e-6);
        
        let c = vec![0.0, 1.0, 0.0];
        let similarity = cosine_similarity_scalar(&a, &c);
        assert!((similarity - 0.0).abs() < 1e-6);
    }
    
    #[test]
    fn test_dot_product_scalar() {
        let a = vec![1.0, 2.0, 3.0];
        let b = vec![4.0, 5.0, 6.0];
        let dot = dot_product_scalar(&a, &b);
        assert!((dot - 32.0).abs() < 1e-6); // 1*4 + 2*5 + 3*6 = 32
    }
    
    #[test]
    fn test_euclidean_distance_scalar() {
        let a = vec![0.0, 0.0, 0.0];
        let b = vec![3.0, 4.0, 0.0];
        let dist = euclidean_distance_scalar(&a, &b);
        assert!((dist - 5.0).abs() < 1e-6); // sqrt(3^2 + 4^2) = 5
    }
    
    #[test]
    fn test_simd_engine_creation() {
        let engine = create_simd_engine();
        
        // Test with simple vectors
        let a = vec![1.0, 2.0, 3.0, 4.0];
        let b = vec![2.0, 3.0, 4.0, 5.0];
        
        let cosine = engine.cosine_similarity(&a, &b);
        let dot = engine.dot_product(&a, &b);
        let euclidean = engine.euclidean_distance(&a, &b);
        
        // Basic sanity checks
        assert!(cosine >= -1.0 && cosine <= 1.0);
        assert!(dot > 0.0); // All positive numbers
        assert!(euclidean >= 0.0);
    }
    
    #[test]
    fn test_simd_vs_scalar_consistency() {
        let engine = create_simd_engine();
        
        // Test vectors with different sizes
        let test_cases = vec![
            (vec![1.0, 2.0], vec![3.0, 4.0]), // Short
            (vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0], vec![2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]), // Exactly 8
            (vec![1.0; 17], vec![2.0; 17]), // > 8, not multiple
        ];
        
        for (a, b) in test_cases {
            // Compare SIMD vs scalar results
            let simd_cosine = engine.cosine_similarity(&a, &b);
            let scalar_cosine = cosine_similarity_scalar(&a, &b);
            assert!((simd_cosine - scalar_cosine).abs() < 1e-5, 
                   "Cosine SIMD vs scalar mismatch: {} vs {}", simd_cosine, scalar_cosine);
            
            let simd_dot = engine.dot_product(&a, &b);
            let scalar_dot = dot_product_scalar(&a, &b);
            assert!((simd_dot - scalar_dot).abs() < 1e-5,
                   "Dot product SIMD vs scalar mismatch: {} vs {}", simd_dot, scalar_dot);
            
            let simd_euclidean = engine.euclidean_distance(&a, &b);
            let scalar_euclidean = euclidean_distance_scalar(&a, &b);
            assert!((simd_euclidean - scalar_euclidean).abs() < 1e-5,
                   "Euclidean SIMD vs scalar mismatch: {} vs {}", simd_euclidean, scalar_euclidean);
        }
    }
    
    #[test]
    fn test_compute_similarity_simd() {
        let a = vec![1.0, 2.0, 3.0];
        let b = vec![4.0, 5.0, 6.0];
        
        // Test all three metrics
        let cosine = compute_similarity_simd(&a, &b, &SimilarityMetric::Cosine);
        let dot = compute_similarity_simd(&a, &b, &SimilarityMetric::DotProduct);
        let euclidean = compute_similarity_simd(&a, &b, &SimilarityMetric::Euclidean);
        
        assert!(cosine >= -1.0 && cosine <= 1.0);
        assert!(dot > 0.0);
        assert!(euclidean >= 0.0);
    }
    
    #[test]
    fn test_cpu_features() {
        let features = get_cpu_features();
        
        // Just verify the function works and returns valid values
        // Actual feature availability depends on the CPU
        #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
        {
            // On x86/x86_64, these are detected at runtime
            println!("AVX2: {}, FMA: {}, SSE4.2: {}", features.avx2, features.fma, features.sse42);
        }
        
        #[cfg(target_arch = "aarch64")]
        {
            // On ARM64, NEON should be available
            assert!(features.neon);
        }
        
        #[cfg(not(any(target_arch = "x86", target_arch = "x86_64", target_arch = "aarch64")))]
        {
            // Other architectures should have all SIMD features as false
            assert!(!features.avx2);
            assert!(!features.fma);
            assert!(!features.sse42);
            assert!(!features.neon);
        }
    }
    
    #[test]
    fn test_engine_names() {
        let engine = create_simd_engine();
        let name = engine.name();
        
        // Verify we get a valid engine name
        assert!(name == "AVX2" || name == "NEON" || name == "Scalar");
    }
    
    #[test]
    fn test_edge_cases() {
        let engine = create_simd_engine();
        
        // Zero vectors
        let zero = vec![0.0, 0.0, 0.0];
        let normal = vec![1.0, 2.0, 3.0];
        
        let cosine = engine.cosine_similarity(&zero, &normal);
        assert_eq!(cosine, 0.0);
        
        let dot = engine.dot_product(&zero, &normal);
        assert_eq!(dot, 0.0);
        
        let euclidean = engine.euclidean_distance(&zero, &normal);
        assert!((euclidean - (1.0 + 4.0 + 9.0_f32).sqrt()).abs() < 1e-6);
        
        // Identical vectors
        let identical = vec![1.0, 2.0, 3.0];
        let cosine_identical = engine.cosine_similarity(&identical, &identical);
        assert!((cosine_identical - 1.0).abs() < 1e-6);
        
        let euclidean_identical = engine.euclidean_distance(&identical, &identical);
        assert!((euclidean_identical - 0.0).abs() < 1e-6);
    }
}

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
unsafe fn horizontal_sum_avx2(v: std::arch::x86_64::__m256) -> f32 {
    use std::arch::x86_64::*;
    
    let hi = _mm256_extractf128_ps(v, 1);
    let lo = _mm256_castps256_ps128(v);
    let sum128 = _mm_add_ps(hi, lo);
    
    let hi64 = _mm_movehl_ps(sum128, sum128);
    let sum64 = _mm_add_ps(sum128, hi64);
    
    let hi32 = _mm_shuffle_ps(sum64, sum64, 1);
    let sum32 = _mm_add_ss(sum64, hi32);
    
    _mm_cvtss_f32(sum32)
}

// =============================================================================
// NEON IMPLEMENTATIONS (ARM64/Apple Silicon)
// =============================================================================

#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "neon")]
unsafe fn cosine_similarity_neon(a: &[f32], b: &[f32]) -> f32 {
    use std::arch::aarch64::*;
    
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    let mut dot_sum = vdupq_n_f32(0.0);
    let mut norm_a_sum = vdupq_n_f32(0.0);
    let mut norm_b_sum = vdupq_n_f32(0.0);
    
    for i in 0..chunks {
        let idx = i * 4;
        
        let va = vld1q_f32(a.as_ptr().add(idx));
        let vb = vld1q_f32(b.as_ptr().add(idx));
        
        dot_sum = vfmaq_f32(dot_sum, va, vb);
        norm_a_sum = vfmaq_f32(norm_a_sum, va, va);
        norm_b_sum = vfmaq_f32(norm_b_sum, vb, vb);
    }
    
    let dot_product = vaddvq_f32(dot_sum);
    let norm_a = vaddvq_f32(norm_a_sum);
    let norm_b = vaddvq_f32(norm_b_sum);
    
    // Process remainder
    let (dot_remainder, norm_a_remainder, norm_b_remainder) = if remainder > 0 {
        let start_idx = chunks * 4;
        let mut dot = 0.0f32;
        let mut na = 0.0f32;
        let mut nb = 0.0f32;
        
        for i in 0..remainder {
            let ai = a[start_idx + i];
            let bi = b[start_idx + i];
            dot += ai * bi;
            na += ai * ai;
            nb += bi * bi;
        }
        (dot, na, nb)
    } else {
        (0.0, 0.0, 0.0)
    };
    
    let final_dot = dot_product + dot_remainder;
    let final_norm_a = norm_a + norm_a_remainder;
    let final_norm_b = norm_b + norm_b_remainder;
    
    let norm_product = (final_norm_a * final_norm_b).sqrt();
    if norm_product == 0.0 {
        0.0
    } else {
        final_dot / norm_product
    }
}

#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "neon")]
unsafe fn dot_product_neon(a: &[f32], b: &[f32]) -> f32 {
    use std::arch::aarch64::*;
    
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    let mut sum = vdupq_n_f32(0.0);
    
    for i in 0..chunks {
        let idx = i * 4;
        let va = vld1q_f32(a.as_ptr().add(idx));
        let vb = vld1q_f32(b.as_ptr().add(idx));
        sum = vfmaq_f32(sum, va, vb);
    }
    
    let mut result = vaddvq_f32(sum);
    
    // Process remainder
    for i in 0..remainder {
        let idx = chunks * 4 + i;
        result += a[idx] * b[idx];
    }
    
    result
}

#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "neon")]
unsafe fn euclidean_distance_neon(a: &[f32], b: &[f32]) -> f32 {
    use std::arch::aarch64::*;
    
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    let mut sum = vdupq_n_f32(0.0);
    
    for i in 0..chunks {
        let idx = i * 4;
        let va = vld1q_f32(a.as_ptr().add(idx));
        let vb = vld1q_f32(b.as_ptr().add(idx));
        let diff = vsubq_f32(va, vb);
        sum = vfmaq_f32(sum, diff, diff);
    }
    
    let mut result = vaddvq_f32(sum);
    
    // Process remainder
    for i in 0..remainder {
        let idx = chunks * 4 + i;
        let diff = a[idx] - b[idx];
        result += diff * diff;
    }
    
    result.sqrt()
}

// =============================================================================
// SCALAR FALLBACK IMPLEMENTATIONS
// =============================================================================

pub fn cosine_similarity_scalar(a: &[f32], b: &[f32]) -> f32 {
    let mut dot_product = 0.0;
    let mut norm_a = 0.0;
    let mut norm_b = 0.0;
    
    // Unroll loop for better performance
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
    
    // Process remainder
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

pub fn dot_product_scalar(a: &[f32], b: &[f32]) -> f32 {
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    let mut result = 0.0;
    
    // Unrolled loop
    for i in 0..chunks {
        let idx = i * 4;
        result += a[idx] * b[idx] 
                + a[idx + 1] * b[idx + 1] 
                + a[idx + 2] * b[idx + 2] 
                + a[idx + 3] * b[idx + 3];
    }
    
    // Process remainder
    for i in 0..remainder {
        let idx = chunks * 4 + i;
        result += a[idx] * b[idx];
    }
    
    result
}

pub fn euclidean_distance_scalar(a: &[f32], b: &[f32]) -> f32 {
    let len = a.len();
    let chunks = len / 4;
    let remainder = len % 4;
    
    let mut result = 0.0;
    
    // Unrolled loop
    for i in 0..chunks {
        let idx = i * 4;
        
        let d0 = a[idx] - b[idx];
        let d1 = a[idx + 1] - b[idx + 1];
        let d2 = a[idx + 2] - b[idx + 2];
        let d3 = a[idx + 3] - b[idx + 3];
        
        result += d0 * d0 + d1 * d1 + d2 * d2 + d3 * d3;
    }
    
    // Process remainder
    for i in 0..remainder {
        let idx = chunks * 4 + i;
        let diff = a[idx] - b[idx];
        result += diff * diff;
    }
    
    result.sqrt()
}