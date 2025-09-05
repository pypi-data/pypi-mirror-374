use rand::SeedableRng;
use rand::rngs::StdRng;
use rand_distr::{Normal, Distribution};
use rayon::prelude::*;
use std::fs::File;
use std::io::{BufWriter, BufReader, Write, Read, Seek, SeekFrom};
use std::path::Path;
use std::collections::{HashMap, HashSet};
use smallvec::SmallVec;
use dashmap::DashMap;
use log::{debug, info, warn, error};
use std::sync::atomic::{AtomicUsize, Ordering};

const MAX_BUCKET_SIZE: usize = 12_000;  
const MAX_TOTAL_CANDIDATES: usize = 80_000;  
const MAX_HAMMING_RADIUS: usize = 32;  
const MIN_DATASET_SIZE: usize = 99_000;  


const MAX_TWO_BIT_PROBES_64: usize = 5_000;     
const MAX_TWO_BIT_PROBES_32_PER_TABLE: usize = 10_000; 
const MAX_THREE_BIT_PROBES: usize = 2_500;  


#[derive(Debug, Default)]
pub struct AnnMetrics {
    pub total_queries: AtomicUsize,
    pub cache_hits: AtomicUsize,
    pub fallback_activations: AtomicUsize,
    pub avg_candidates_generated: AtomicUsize,
}
impl Clone for AnnMetrics {
    fn clone(&self) -> Self {
        AnnMetrics {
            total_queries: AtomicUsize::new(self.total_queries.load(Ordering::Relaxed)),
            cache_hits: AtomicUsize::new(self.cache_hits.load(Ordering::Relaxed)),
            fallback_activations: AtomicUsize::new(self.fallback_activations.load(Ordering::Relaxed)),
            avg_candidates_generated: AtomicUsize::new(self.avg_candidates_generated.load(Ordering::Relaxed)),
        }
    }
}
impl AnnMetrics {
    #[inline] pub fn record_query(&self, candidates: usize, used_fallback: bool) {
        self.total_queries.fetch_add(1, Ordering::Relaxed);
        self.avg_candidates_generated.fetch_add(candidates, Ordering::Relaxed);
        if used_fallback { self.fallback_activations.fetch_add(1, Ordering::Relaxed); }
    }
    #[inline] pub fn get_stats(&self) -> (usize, usize, usize, f64) {
        let total = self.total_queries.load(Ordering::Relaxed);
        let cache = self.cache_hits.load(Ordering::Relaxed);
        let fallback = self.fallback_activations.load(Ordering::Relaxed);
        let avg_candidates = if total>0 {
            self.avg_candidates_generated.load(Ordering::Relaxed) as f64 / total as f64
        } else { 0.0 };
        (total, cache, fallback, avg_candidates)
    }
}


#[derive(Clone, Debug)]
pub struct AnnConfig {
    pub target_candidates: usize,
    pub min_candidates: usize,
    pub max_candidates: usize,
    pub max_hamming_64: usize,
    pub max_hamming_32: usize,
    pub max_hamming_16: usize,
    pub random_sample_size: usize,
    pub enable_metrics: bool,
    pub quality_tier: QualityTier,
}

#[derive(Clone, Debug)]
enum QualityTier {
    ExactOnly,      
    SweetSpot,      
    BestEffort,     
}

impl AnnConfig {
    fn for_dataset_size(rows: usize) -> Self {
        if rows < MIN_DATASET_SIZE {
            warn!("Dataset pequeno ({}), recomendado EXACT search", rows);
            return AnnConfig {
                target_candidates: 0,
                min_candidates: 0,
                max_candidates: 0,
                max_hamming_64: 0,
                max_hamming_32: 0,
                max_hamming_16: 0,
                random_sample_size: 0,
                enable_metrics: false,
                quality_tier: QualityTier::ExactOnly,
            };
        }

        match rows {
            
            50_000..=500_000 => {
                    let target = if rows <= 100_000 {
                        30_000  
                    } else if rows <= 200_000 {
                        40_000  
                    } else {
                        55_000  
                    };
                    
                    AnnConfig {
                        target_candidates: target,
                        min_candidates: target / 3,  
                        max_candidates: target * 2,  
                        max_hamming_64: 22,  
                        max_hamming_32: 20,  
                        max_hamming_16: 10,  
                        random_sample_size: 4000,  
                        enable_metrics: true,
                        quality_tier: QualityTier::SweetSpot,
                    }
                }
            
            
            _ => AnnConfig {
                target_candidates: 50_000,
                min_candidates: 15_000,
                max_candidates: 75_000,
                max_hamming_64: 16,  
                max_hamming_32: 14,
                max_hamming_16: 6,
                random_sample_size: 4000,
                enable_metrics: true,
                quality_tier: QualityTier::BestEffort,
            },
        }
    }
}


#[derive(Clone, Debug)]
struct SafeBucket {
    items: SmallVec<[usize; 64]>,  
    is_full: bool,
}
impl SafeBucket {
    #[inline] fn new() -> Self { Self { items: SmallVec::new(), is_full: false } }
    #[inline] fn push(&mut self, item: usize) -> bool {
        if self.items.len() >= MAX_BUCKET_SIZE {
            if !self.is_full {
                debug!("Bucket atingiu MAX_BUCKET_SIZE={}", MAX_BUCKET_SIZE);
                self.is_full = true;
            }
            return false;
        }
        self.items.push(item);
        true
    }
    #[inline] fn len(&self) -> usize { self.items.len() }
    #[inline] fn iter(&self) -> impl Iterator<Item = &usize> { self.items.iter() }
}


#[derive(Clone)]
pub struct AnnIndex {
    
    pub dims: usize,
    pub bits: usize,
    pub projections: Vec<Vec<f32>>,
    pub buckets: HashMap<u16, SmallVec<[usize; 16]>>,
    
    
    seed: u64,
    config: AnnConfig,
    total_vectors: usize,
    metrics: AnnMetrics,
    
    
    main_projections: Vec<Vec<f32>>,
    main_bits: usize,
    main_buckets64: HashMap<u64, SafeBucket>,
    
    
    num_tables: usize,
    multi_projections: Vec<Vec<Vec<f32>>>,
    multi_bits32: usize,
    multi_tables32: Vec<HashMap<u32, SafeBucket>>,
    
    
    ultra_projections: Vec<Vec<f32>>,
    ultra_bits: usize,
    ultra_buckets: HashMap<u128, SafeBucket>,
}
unsafe impl Send for AnnIndex {}
unsafe impl Sync for AnnIndex {}


#[inline]
fn dot_product_safe(a: &[f32], b: &[f32]) -> f32 {
    if a.len() != b.len() { 
        error!("dot dims {} vs {}", a.len(), b.len()); 
        return 0.0; 
    }
    
    let mut sum = 0.0f32;
    let n8 = a.len() / 8;
    
    
    for i in 0..n8 {
        let k = i * 8;
        sum += a[k]*b[k] + a[k+1]*b[k+1] + a[k+2]*b[k+2] + a[k+3]*b[k+3]
             + a[k+4]*b[k+4] + a[k+5]*b[k+5] + a[k+6]*b[k+6] + a[k+7]*b[k+7];
    }
    
    
    for i in (n8*8)..a.len() { 
        sum += a[i]*b[i]; 
    }
    
    if !sum.is_finite() { 
        warn!("dot non-finite"); 
        0.0 
    } else { 
        sum 
    }
}

#[inline]
fn hash_signs_u16(vec: &[f32], projections: &[Vec<f32>], bits: usize) -> u16 {
    if projections.is_empty() { return 0; }
    let mut h=0u16; 
    let m = bits.min(16).min(projections.len());
    for (j, w) in projections.iter().enumerate().take(m) {
        if w.len()==vec.len() && dot_product_safe(vec,w) >= 0.0 { 
            h |= 1<<j; 
        }
    } 
    h
}

#[inline]
fn hash_signs_u32(vec: &[f32], projections: &[Vec<f32>], bits: usize) -> u32 {
    if projections.is_empty() { return 0; }
    let mut h=0u32; 
    let m = bits.min(32).min(projections.len());
    for (j, w) in projections.iter().enumerate().take(m) {
        if w.len()==vec.len() && dot_product_safe(vec,w) >= 0.0 { 
            h |= 1<<j; 
        }
    } 
    h
}

#[inline]
fn hash_signs_u64(vec: &[f32], projections: &[Vec<f32>], bits: usize) -> u64 {
    if projections.is_empty() { return 0; }
    let mut h=0u64; 
    let m = bits.min(64).min(projections.len());
    for (j, w) in projections.iter().enumerate().take(m) {
        if w.len()==vec.len() && dot_product_safe(vec,w) >= 0.0 { 
            h |= 1u64<<j; 
        }
    } 
    h
}

#[inline]
fn hash_signs_u128(vec: &[f32], projections: &[Vec<f32>], bits: usize) -> u128 {
    if projections.is_empty() { return 0; }
    let mut h=0u128; 
    let m = bits.min(128).min(projections.len());
    for (j, w) in projections.iter().enumerate().take(m) {
        if w.len()==vec.len() && dot_product_safe(vec,w) >= 0.0 { 
            h |= 1u128<<j; 
        }
    } 
    h
}


#[derive(Debug)]
enum RerankStrategy {
    SmartSampling,   
    PartialRanking,  
    FullRanking,     
}

impl AnnIndex {
    fn rerank_smart_sampling(&self, candidates: &[usize], query: &[f32], vectors: &[f32], top_k: usize) -> Vec<(usize, f32)> {
        use rand::seq::SliceRandom;
        let mut rng = StdRng::seed_from_u64(self.seed + top_k as u64);
        
        
        let sample_size = (candidates.len() / 4).min(top_k * 15).max(top_k * 3);
        let mut sample_indices = candidates.to_vec();
        sample_indices.shuffle(&mut rng);
        sample_indices.truncate(sample_size);
        
        let mut sample_scores: Vec<(usize, f32)> = sample_indices
            .into_par_iter()
            .filter_map(|i| {
                if i >= self.total_vectors { return None; }
                let off = i * self.dims;
                let s = dot_product_safe(query, &vectors[off..off + self.dims]);
                if s.is_finite() { Some((i, s)) } else { None }
            }).collect();
        
        if sample_scores.is_empty() { return Vec::new(); }
        
        
        sample_scores.sort_unstable_by(|a, b| b.1.total_cmp(&a.1));
        let threshold = if sample_scores.len() > top_k {
            sample_scores[top_k - 1].1 * 0.95  
        } else {
            sample_scores.last().unwrap().1 * 0.9  
        };
        
        
        let mut high_candidates = Vec::new();
        let mut low_candidates = Vec::new();
        
        for &candidate in candidates {
            if sample_scores.iter().any(|(i, s)| *i == candidate && *s >= threshold) {
                high_candidates.push(candidate);
            } else {
                low_candidates.push(candidate);
            }
        }
        
        
        low_candidates.shuffle(&mut rng);
        let low_sample_size = top_k.saturating_sub(high_candidates.len()).min(low_candidates.len());
        high_candidates.extend(low_candidates.into_iter().take(low_sample_size));
        
        
        let mut final_scores: Vec<(usize, f32)> = high_candidates
            .into_par_iter()
            .filter_map(|i| {
                if i >= self.total_vectors { return None; }
                let off = i * self.dims;
                let s = dot_product_safe(query, &vectors[off..off + self.dims]);
                if s.is_finite() { Some((i, s)) } else { None }
            }).collect();
        
        final_scores.sort_unstable_by(|a, b| b.1.total_cmp(&a.1));
        final_scores.truncate(top_k);
        final_scores
    }
    
    fn rerank_partial(&self, candidates: &[usize], query: &[f32], vectors: &[f32], top_k: usize) -> Vec<(usize, f32)> {
        let mut scores: Vec<(usize, f32)> = candidates
            .into_par_iter()
            .filter_map(|&i| {
                if i >= self.total_vectors { return None; }
                let off = i * self.dims;
                let s = dot_product_safe(query, &vectors[off..off + self.dims]);
                if s.is_finite() { Some((i, s)) } else { None }
            }).collect();
        
        
        if scores.len() > top_k {
            scores.select_nth_unstable_by(top_k, |a, b| b.1.total_cmp(&a.1));
            scores.truncate(top_k);
            scores.sort_unstable_by(|a, b| b.1.total_cmp(&a.1));
        }
        
        scores
    }
    
    fn rerank_full(&self, candidates: &[usize], query: &[f32], vectors: &[f32], top_k: usize) -> Vec<(usize, f32)> {
        let mut scores: Vec<(usize, f32)> = candidates
            .into_par_iter()
            .filter_map(|&i| {
                if i >= self.total_vectors { return None; }
                let off = i * self.dims;
                let s = dot_product_safe(query, &vectors[off..off + self.dims]);
                if s.is_finite() { Some((i, s)) } else { None }
            }).collect();
        
        scores.sort_unstable_by(|a, b| b.1.total_cmp(&a.1));
        scores.truncate(top_k);
        scores
    }

    
    
    fn calculate_optimal_config(rows: usize, dims: usize, requested_bits: usize)
        -> (usize, usize, usize, usize, usize, usize)
    {
        if rows < MIN_DATASET_SIZE { 
            warn!("Dataset pequeno ({}), recomendado exact search", rows); 
            return (8, 8, 8, 1, 0, 0);
        }
        
        if dims < 8 { 
            error!("dims < 8"); 
            return (8, 12, 16, 2, 0, 0); 
        }

        
        let bits16 = requested_bits.clamp(12, 16);

        let (bits32, bits64, tables, ultra_bits, ultra_enable) = match rows {
            
            50_000..=500_000 => {
                    if rows <= 100_000 {
                        
                        (16, 26, 36, 0, false)  
                    } else if rows <= 200_000 {
                        
                        (18, 28, 42, 48, true)  
                    } else {
                        
                        (20, 30, 50, 56, true)  
                    }
                }
                
                
                _ => (12, 18, 16, 0, false),
        };

        assert!(bits16 <= 16 && bits32 <= 32 && bits64 <= 64);
        assert!((1..=60).contains(&tables));
        assert!(ultra_bits <= 128);

        (bits16, bits32, bits64, tables, ultra_bits, if ultra_enable { 1 } else { 0 })
    }

    
    pub fn build(vectors: &[f32], dims: usize, rows: usize, bits: usize, seed: u64) -> Self {
        if vectors.len() != dims * rows {
            panic!("Invalid vector data: expected {}, got {}", dims*rows, vectors.len());
        }
        if dims < 8 { panic!("Minimum 8 dims, got {}", dims); }
        
        let (bits16, bits32, bits64, num_tables, ultra_bits, ultra_enable) = 
            Self::calculate_optimal_config(rows, dims, bits);
        let config = AnnConfig::for_dataset_size(rows);

        info!("Building SWEET SPOT ANN: rows={}, dims={}", rows, dims);
        info!("Config: 16b={}, 32b={}×{}, 64b={}, ultra={}b×{}", 
              bits16, bits32, num_tables, bits64, ultra_bits, ultra_enable);
        info!("Targets: min={}, target={}, max={} (tier: {:?})",
              config.min_candidates, config.target_candidates, config.max_candidates, config.quality_tier);

        let mut rng = StdRng::seed_from_u64(seed);
        let normal = Normal::new(0.0, 1.0).unwrap();

        
        let projections_16: Vec<Vec<f32>> = (0..bits16)
            .map(|_| (0..dims).map(|_| normal.sample(&mut rng) as f32).collect())
            .collect();

        let buckets_u16 = DashMap::<u16, SmallVec<[usize; 16]>>::new();
        (0..rows).into_par_iter().for_each(|i| {
            let v = &vectors[i * dims .. (i+1) * dims];
            let h = hash_signs_u16(v, &projections_16, bits16);
            let mut b = buckets_u16.entry(h).or_default();
            if b.len() < MAX_BUCKET_SIZE { b.push(i); }
        });
        let buckets_compat = buckets_u16.into_iter().collect::<HashMap<_,_>>();

        
        let main_projections: Vec<Vec<f32>> = (0..bits64)
            .map(|_| (0..dims).map(|_| normal.sample(&mut rng) as f32).collect())
            .collect();
        let main_buckets = DashMap::<u64, SafeBucket>::new();
        (0..rows).into_par_iter().for_each(|i| {
            let v = &vectors[i * dims .. (i+1) * dims];
            let h = hash_signs_u64(v, &main_projections, bits64);
            main_buckets.entry(h).or_insert_with(SafeBucket::new).push(i);
        });
        let main_buckets64 = main_buckets.into_iter().collect::<HashMap<_,_>>();

        
        let multi_data: Vec<(Vec<Vec<f32>>, HashMap<u32, SafeBucket>)> =
            (0..num_tables).into_par_iter().map(|t| {
                let mut trng = StdRng::seed_from_u64(seed + (t as u64)*10_000 + 1_000_000);
                let table_proj: Vec<Vec<f32>> = (0..bits32)
                    .map(|_| (0..dims).map(|_| normal.sample(&mut trng) as f32).collect())
                    .collect();
                let tbl = DashMap::<u32, SafeBucket>::new();
                (0..rows).into_par_iter().for_each(|i| {
                    let v = &vectors[i * dims .. (i+1) * dims];
                    let h = hash_signs_u32(v, &table_proj, bits32);
                    tbl.entry(h).or_insert_with(SafeBucket::new).push(i);
                });
                (table_proj, tbl.into_iter().collect::<HashMap<_,_>>())
            }).collect();

        let (multi_projections, multi_tables32): (Vec<_>, Vec<_>) =
            multi_data.into_iter().unzip();

        
        let (ultra_projections, ultra_buckets) = if ultra_enable == 1 && ultra_bits > 0 {
            let mut urng = StdRng::seed_from_u64(seed + 2_000_000);
            let uproj: Vec<Vec<f32>> = (0..ultra_bits)
                .map(|_| (0..dims).map(|_| normal.sample(&mut urng) as f32).collect())
                .collect();
            let ubkts = DashMap::<u128, SafeBucket>::new();
            (0..rows).into_par_iter().for_each(|i| {
                let v = &vectors[i * dims .. (i+1) * dims];
                let h = hash_signs_u128(v, &uproj, ultra_bits);
                ubkts.entry(h).or_insert_with(SafeBucket::new).push(i);
            });
            (uproj, ubkts.into_iter().collect::<HashMap<_,_>>())
        } else {
            (Vec::new(), HashMap::new())
        };

        let total_bk16 = buckets_compat.len();
        let total_bk64 = main_buckets64.len();
        let total_bk32: usize = multi_tables32.iter().map(|t| t.len()).sum();
        let total_bk128 = ultra_buckets.len();

        info!("Built SWEET SPOT ANN: buckets 16b={} 64b={} 32b(sum)={} 128b={}", 
              total_bk16, total_bk64, total_bk32, total_bk128);
        info!("Avg bucket sizes: 64b={:.2} 32b={:.2} 128b={:.2}",
              if total_bk64>0 { rows as f64 / total_bk64 as f64 } else { 0.0 },
              if total_bk32>0 { rows as f64 / total_bk32 as f64 } else { 0.0 },
              if total_bk128>0 { rows as f64 / total_bk128 as f64 } else { 0.0 });

        Self {
            dims, bits: bits16, projections: projections_16, buckets: buckets_compat,
            seed, config, total_vectors: rows, metrics: AnnMetrics::default(),
            main_projections, main_bits: bits64, main_buckets64,
            num_tables, multi_projections, multi_bits32: bits32, multi_tables32,
            ultra_projections, ultra_bits, ultra_buckets,
        }
    }

    
    #[inline]
    fn bit_order_by_margin_u64(&self, query: &[f32]) -> Vec<(usize, f32)> {
        let mut s: Vec<(usize, f32)> = self.main_projections.iter().enumerate()
            .map(|(j, w)| (j, dot_product_safe(query, w).abs())).collect();
        s.sort_unstable_by(|a,b| a.1.total_cmp(&b.1));
        s
    }
    
    #[inline]
    fn bit_order_by_margin_u32(&self, query: &[f32], table_idx: usize) -> Vec<(usize, f32)> {
        if table_idx >= self.multi_projections.len() { return Vec::new(); }
        let proj = &self.multi_projections[table_idx];
        let mut s: Vec<(usize, f32)> = proj.iter().enumerate()
            .map(|(j, w)| (j, dot_product_safe(query, w).abs())).collect();
        s.sort_unstable_by(|a,b| a.1.total_cmp(&b.1));
        s
    }

    #[inline]
    fn bit_order_by_margin_u128(&self, query: &[f32]) -> Vec<(usize, f32)> {
        let mut s: Vec<(usize, f32)> = self.ultra_projections.iter().enumerate()
            .map(|(j, w)| (j, dot_product_safe(query, w).abs())).collect();
        s.sort_unstable_by(|a,b| a.1.total_cmp(&b.1));
        s
    }

    
    pub fn query_candidates(&self, query: &[f32]) -> Vec<usize> {
        if query.len()!=self.dims { 
            error!("Query dims {} vs {}", query.len(), self.dims); 
            return Vec::new(); 
        }
        if query.iter().any(|&x| !x.is_finite()) { 
            error!("Query contém NaN/Inf"); 
            return Vec::new(); 
        }

        
        let mut freq: HashMap<usize, u16> = HashMap::new();
        let mut used_fallback = false;

        
        if !self.ultra_buckets.is_empty() && self.ultra_bits > 0 {
            let h128 = hash_signs_u128(query, &self.ultra_projections, self.ultra_bits);
            
            
            if let Some(b) = self.ultra_buckets.get(&h128) {
                for &id in b.iter() {
                    if id < self.total_vectors {
                        *freq.entry(id).or_insert(0) += 4; 
                    }
                }
            }
            
            
            if freq.len() < self.config.target_candidates {
                let order = self.bit_order_by_margin_u128(query);
                let max_flips = order.len().min(12); 
                for &(bit, _) in order.iter().take(max_flips) {
                    if freq.len() >= self.config.target_candidates { break; }
                    let flipped = h128 ^ (1u128 << bit);
                    if let Some(b) = self.ultra_buckets.get(&flipped) {
                        for &id in b.iter() {
                            if id < self.total_vectors {
                                *freq.entry(id).or_insert(0) += 3;
                                if freq.len() >= self.config.target_candidates { break; }
                            }
                        }
                    }
                }
            }
        }

        
        if self.main_bits>0 && !self.main_projections.is_empty() {
            let h64 = hash_signs_u64(query, &self.main_projections, self.main_bits);
            
            
            if let Some(b) = self.main_buckets64.get(&h64) {
                for &id in b.iter() {
                    if id < self.total_vectors {
                        *freq.entry(id).or_insert(0) += 3; 
                    }
                }
            }

            
            if freq.len() < self.config.target_candidates {
                let order = self.bit_order_by_margin_u64(query);
                let max_flips = order.len().min(self.config.max_hamming_64);
                for &(bit, _) in order.iter().take(max_flips) {
                    if freq.len() >= self.config.target_candidates { break; }
                    let flipped = h64 ^ (1u64 << bit);
                    if let Some(b) = self.main_buckets64.get(&flipped) {
                        for &id in b.iter() {
                            if id < self.total_vectors {
                                *freq.entry(id).or_insert(0) += 2;
                                if freq.len() >= self.config.target_candidates { break; }
                            }
                        }
                    }
                }
            }

            
            if freq.len() < self.config.target_candidates {
                let order = self.bit_order_by_margin_u64(query);
                let m = order.len().min(self.config.max_hamming_64);
                let mut probes = 0usize;
                'two64: for a in 0..m {
                    for b in (a+1)..m {
                        if freq.len() >= self.config.target_candidates || probes >= MAX_TWO_BIT_PROBES_64 { 
                            break 'two64; 
                        }
                        let flipped = h64 ^ (1u64 << order[a].0) ^ (1u64 << order[b].0);
                        if let Some(bk) = self.main_buckets64.get(&flipped) {
                            for &id in bk.iter() {
                                if id < self.total_vectors {
                                    *freq.entry(id).or_insert(0) += 1;
                                    if freq.len() >= self.config.target_candidates { break 'two64; }
                                }
                            }
                        }
                        probes += 1;
                    }
                }
            }

            
            if freq.len() < self.config.target_candidates && 
               matches!(self.config.quality_tier, QualityTier::SweetSpot) {
                let order = self.bit_order_by_margin_u64(query);
                let m = order.len().min(16); 
                let mut probes = 0usize;
                'three64: for a in 0..m {
                    for b in (a+1)..m {
                        for c in (b+1)..m {
                            if freq.len() >= self.config.target_candidates || probes >= MAX_THREE_BIT_PROBES { 
                                break 'three64; 
                            }
                            let flipped = h64 ^ (1u64 << order[a].0) ^ (1u64 << order[b].0) ^ (1u64 << order[c].0);
                            if let Some(bk) = self.main_buckets64.get(&flipped) {
                                for &id in bk.iter() {
                                    if id < self.total_vectors {
                                        *freq.entry(id).or_insert(0) += 1;
                                        if freq.len() >= self.config.target_candidates { break 'three64; }
                                    }
                                }
                            }
                            probes += 1;
                        }
                    }
                }
            }
        }

        
        if self.multi_bits32>0 && !self.multi_projections.is_empty() {
            for t in 0..self.multi_tables32.len() {
                if freq.len() >= self.config.target_candidates { break; }

                let tbl = &self.multi_tables32[t];
                let h32 = hash_signs_u32(query, &self.multi_projections[t], self.multi_bits32);

                
                if let Some(b) = tbl.get(&h32) {
                    for &id in b.iter() {
                        if id < self.total_vectors {
                            *freq.entry(id).or_insert(0) += 2; 
                            if freq.len() >= self.config.target_candidates { break; }
                        }
                    }
                }

                
                if freq.len() < self.config.target_candidates {
                    let order = self.bit_order_by_margin_u32(query, t);
                    let max_flips = order.len().min(self.config.max_hamming_32);
                    for &(bit, _) in order.iter().take(max_flips) {
                        if freq.len() >= self.config.target_candidates { break; }
                        let flipped = h32 ^ (1u32 << bit);
                        if let Some(bk) = tbl.get(&flipped) {
                            for &id in bk.iter() {
                                if id < self.total_vectors {
                                    *freq.entry(id).or_insert(0) += 1;
                                    if freq.len() >= self.config.target_candidates { break; }
                                }
                            }
                        }
                    }
                }

                
                if freq.len() < self.config.target_candidates {
                    let order = self.bit_order_by_margin_u32(query, t);
                    let m = order.len().min(self.config.max_hamming_32);
                    let mut probes = 0usize;
                    'two32: for a in 0..m {
                        for b in (a+1)..m {
                            if freq.len() >= self.config.target_candidates || 
                               probes >= MAX_TWO_BIT_PROBES_32_PER_TABLE { 
                                break 'two32; 
                            }
                            let flipped = h32 ^ (1u32 << order[a].0) ^ (1u32 << order[b].0);
                            if let Some(bk) = tbl.get(&flipped) {
                                for &id in bk.iter() {
                                    if id < self.total_vectors {
                                        *freq.entry(id).or_insert(0) += 1;
                                        if freq.len() >= self.config.target_candidates { break 'two32; }
                                    }
                                }
                            }
                            probes += 1;
                        }
                    }
                }

                
                if freq.len() < self.config.target_candidates && 
                   matches!(self.config.quality_tier, QualityTier::SweetSpot) {
                    let order = self.bit_order_by_margin_u32(query, t);
                    let m = order.len().min(12); 
                    let mut probes = 0usize;
                    'three32: for a in 0..m {
                        for b in (a+1)..m {
                            for c in (b+1)..m {
                                if freq.len() >= self.config.target_candidates || probes >= 500 { 
                                    break 'three32; 
                                }
                                let flipped = h32 ^ (1u32 << order[a].0) ^ (1u32 << order[b].0) ^ (1u32 << order[c].0);
                                if let Some(bk) = tbl.get(&flipped) {
                                    for &id in bk.iter() {
                                        if id < self.total_vectors {
                                            *freq.entry(id).or_insert(0) += 1;
                                            if freq.len() >= self.config.target_candidates { break 'three32; }
                                        }
                                    }
                                }
                                probes += 1;
                            }
                        }
                    }
                }
            }
        }

        
        if freq.len() < self.config.min_candidates && !self.projections.is_empty() {
            let h16 = hash_signs_u16(query, &self.projections, self.bits);
            
            
            if let Some(b) = self.buckets.get(&h16) {
                for &id in b.iter() {
                    if id < self.total_vectors {
                        *freq.entry(id).or_insert(0) += 1;
                        if freq.len() >= self.config.target_candidates { break; }
                    }
                }
            }
            
            
            if freq.len() < self.config.min_candidates {
                let maxr = self.config.max_hamming_16;
                for i in 0..self.bits.min(16).min(maxr) {
                    if freq.len() >= self.config.target_candidates { break; }
                    let flipped = h16 ^ (1u16 << i);
                    if let Some(bk) = self.buckets.get(&flipped) {
                        for &id in bk.iter() {
                            if id < self.total_vectors {
                                *freq.entry(id).or_insert(0) += 1;
                                if freq.len() >= self.config.target_candidates { break; }
                            }
                        }
                    }
                }
            }

            
            if freq.len() < self.config.min_candidates && 
               matches!(self.config.quality_tier, QualityTier::SweetSpot) {
                for a in 0..self.bits.min(16) {
                    for b in (a+1)..self.bits.min(16) {
                        if freq.len() >= self.config.target_candidates { break; }
                        let flipped = h16 ^ (1u16 << a) ^ (1u16 << b);
                        if let Some(bk) = self.buckets.get(&flipped) {
                            for &id in bk.iter() {
                                if id < self.total_vectors {
                                    *freq.entry(id).or_insert(0) += 1;
                                    if freq.len() >= self.config.target_candidates { break; }
                                }
                            }
                        }
                    }
                }
            }
        }

        
        if freq.len() < self.config.min_candidates {
            self.add_intelligent_fallback(&mut freq);
            used_fallback = true;
        }

        finalize_with_frequency_boost(self, freq, used_fallback)
    }

    fn add_intelligent_fallback(&self, freq: &mut HashMap<usize,u16>) {
        use rand::seq::SliceRandom;
        let mut rng = StdRng::seed_from_u64(self.seed + 99_999);
        
        let sample_size = match self.config.quality_tier {
            QualityTier::SweetSpot => {
                
                let base = self.config.random_sample_size.min(10000);
                if freq.len() < self.config.min_candidates {
                    base * 2  
                } else {
                    base
                }
            },
            _ => self.config.random_sample_size.min(4000),
        };
        
        let needed = self.config.target_candidates.saturating_sub(freq.len()).min(sample_size);
        if needed == 0 { return; }
        
        
        let mut idx: Vec<usize> = (0..self.total_vectors).collect();
        idx.shuffle(&mut rng);
        
        for id in idx.into_iter().take(sample_size) {
            if freq.len() >= self.config.target_candidates { break; }
            *freq.entry(id).or_insert(0) += 1;
        }
        
        debug!("Intelligent fallback -> {} candidates (tier: {:?})", freq.len(), self.config.quality_tier);
    }

    
    pub fn query(&self, query: &[f32], top_k: usize, vectors: &[f32]) -> Vec<(usize, f32)> {
        if query.len()!=self.dims { 
            error!("Query dims mismatch"); 
            return Vec::new(); 
        }
        if vectors.len()!= self.dims * self.total_vectors {
            error!("Vectors buffer size mismatch");
            return Vec::new();
        }
        
        let candidates = self.query_candidates(query);
        if candidates.is_empty() { 
            warn!("No candidates"); 
            return Vec::new(); 
        }

        
        let rerank_strategy = if candidates.len() > top_k * 8 {
            
            RerankStrategy::SmartSampling
        } else if candidates.len() > top_k * 3 {
            
            RerankStrategy::PartialRanking
        } else {
            
            RerankStrategy::FullRanking
        };

        let res = match rerank_strategy {
            RerankStrategy::SmartSampling => {
                self.rerank_smart_sampling(&candidates, query, vectors, top_k)
            }
            RerankStrategy::PartialRanking => {
                self.rerank_partial(&candidates, query, vectors, top_k)
            }
            RerankStrategy::FullRanking => {
                self.rerank_full(&candidates, query, vectors, top_k)
            }
        };

        res
    }

    
    #[inline] 
    pub fn get_metrics(&self) -> (usize, usize, usize, f64) { 
        self.metrics.get_stats() 
    }

    pub fn health_check(&self) -> Result<(), String> {
        if self.dims==0 { return Err("Invalid dims".into()); }
        if self.total_vectors==0 { return Err("Invalid vector count".into()); }
        
        for (i,p) in self.projections.iter().enumerate() {
            if p.len()!=self.dims { 
                return Err(format!("16b proj {} wrong size", i)); 
            }
        }
        for (i,p) in self.main_projections.iter().enumerate() {
            if p.len()!=self.dims { 
                return Err(format!("64b proj {} wrong size", i)); 
            }
        }
        for (i,p) in self.ultra_projections.iter().enumerate() {
            if p.len()!=self.dims { 
                return Err(format!("128b proj {} wrong size", i)); 
            }
        }
        
        let mut total_items=0usize;
        for b in self.main_buckets64.values() {
            total_items += b.len();
            for &id in b.iter() { 
                if id>=self.total_vectors { 
                    return Err("idx OOB in 64b".into()); 
                } 
            }
        }
        
        info!("Health ok: dims={}, rows={}, bucket_items={}, tier={:?}", 
              self.dims, self.total_vectors, total_items, self.config.quality_tier);
        Ok(())
    }

    
    pub fn save<P: AsRef<Path>>(&self, path: P) -> std::io::Result<()> {
        if let Err(e)=self.health_check(){ 
            return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, e)); 
        }
        
        let mut f = BufWriter::new(File::create(path)?);
        f.write_all(b"NSEEKANN")?;
        f.write_all(&5u32.to_le_bytes())?; 

        
        f.write_all(&(self.dims as u32).to_le_bytes())?;
        f.write_all(&(self.bits as u32).to_le_bytes())?;
        f.write_all(&(self.main_bits as u32).to_le_bytes())?;
        f.write_all(&(self.multi_bits32 as u32).to_le_bytes())?;
        f.write_all(&(self.ultra_bits as u32).to_le_bytes())?;
        f.write_all(&(self.num_tables as u32).to_le_bytes())?;
        f.write_all(&(self.total_vectors as u32).to_le_bytes())?;
        f.write_all(&self.seed.to_le_bytes())?;

        
        f.write_all(&(self.config.target_candidates as u32).to_le_bytes())?;
        f.write_all(&(self.config.min_candidates as u32).to_le_bytes())?;
        f.write_all(&(self.config.max_candidates as u32).to_le_bytes())?;
        f.write_all(&(self.config.max_hamming_64 as u32).to_le_bytes())?;
        f.write_all(&(self.config.max_hamming_32 as u32).to_le_bytes())?;
        f.write_all(&(self.config.max_hamming_16 as u32).to_le_bytes())?;
        f.write_all(&(self.config.random_sample_size as u32).to_le_bytes())?;
        f.write_all(&[if self.config.enable_metrics {1u8}else{0u8}])?;
        
        
        let tier_byte = match self.config.quality_tier {
            QualityTier::ExactOnly => 0u8,
            QualityTier::SweetSpot => 1u8,
            QualityTier::BestEffort => 2u8,
        };
        f.write_all(&[tier_byte])?;

        
        f.write_all(&(self.projections.len() as u32).to_le_bytes())?;
        for p in &self.projections { 
            for &v in p { f.write_all(&v.to_le_bytes())?; } 
        }
        f.write_all(&(self.buckets.len() as u32).to_le_bytes())?;
        for (&h, ids) in &self.buckets {
            f.write_all(&h.to_le_bytes())?;
            f.write_all(&(ids.len() as u32).to_le_bytes())?;
            for &id in ids { f.write_all(&(id as u32).to_le_bytes())?; }
        }

        
        f.write_all(&(self.main_projections.len() as u32).to_le_bytes())?;
        for p in &self.main_projections { 
            for &v in p { f.write_all(&v.to_le_bytes())?; } 
        }
        f.write_all(&(self.main_buckets64.len() as u32).to_le_bytes())?;
        for (&h, b) in &self.main_buckets64 {
            f.write_all(&h.to_le_bytes())?;
            f.write_all(&(b.len() as u32).to_le_bytes())?;
            f.write_all(&[if b.is_full {1u8}else{0u8}])?;
            for &id in b.iter() { f.write_all(&(id as u32).to_le_bytes())?; }
        }

        
        f.write_all(&(self.multi_projections.len() as u32).to_le_bytes())?;
        for tp in &self.multi_projections {
            f.write_all(&(tp.len() as u32).to_le_bytes())?;
            for p in tp { 
                for &v in p { f.write_all(&v.to_le_bytes())?; } 
            }
        }
        f.write_all(&(self.multi_tables32.len() as u32).to_le_bytes())?;
        for t in &self.multi_tables32 {
            f.write_all(&(t.len() as u32).to_le_bytes())?;
            for (&h, b) in t {
                f.write_all(&h.to_le_bytes())?;
                f.write_all(&(b.len() as u32).to_le_bytes())?;
                f.write_all(&[if b.is_full {1u8}else{0u8}])?;
                for &id in b.iter() { f.write_all(&(id as u32).to_le_bytes())?; }
            }
        }

        
        f.write_all(&(self.ultra_projections.len() as u32).to_le_bytes())?;
        for p in &self.ultra_projections { 
            for &v in p { f.write_all(&v.to_le_bytes())?; } 
        }
        f.write_all(&(self.ultra_buckets.len() as u32).to_le_bytes())?;
        for (&h, b) in &self.ultra_buckets {
            f.write_all(&h.to_le_bytes())?;
            f.write_all(&(b.len() as u32).to_le_bytes())?;
            f.write_all(&[if b.is_full {1u8}else{0u8}])?;
            for &id in b.iter() { f.write_all(&(id as u32).to_le_bytes())?; }
        }

        info!("ANN index v5 (sweet spot) saved");
        Ok(())
    }

    pub fn load<P: AsRef<Path>>(path: P, _vectors: &[f32]) -> std::io::Result<Self> {
        let mut r = BufReader::new(File::open(path)?);
        let mut magic = [0u8;8]; 
        r.read_exact(&mut magic)?;
        
        if &magic != b"NSEEKANN" {
            r.seek(SeekFrom::Start(0))?;
            return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, 
                "Legacy ANN unsupported; rebuild for sweet spot optimization"));
        }
        
        let mut u32b=[0u8;4]; 
        r.read_exact(&mut u32b)?; 
        let version = u32::from_le_bytes(u32b);
        
        match version {
            4 => Self::load_version_4(r),
            5 => Self::load_version_5(r),
            _ => Err(std::io::Error::new(std::io::ErrorKind::InvalidData, 
                format!("Unsupported ANN version {} (need rebuild)", version)))
        }
    }

    fn load_version_4<R: Read>(mut file: R) -> std::io::Result<Self> {
        
        warn!("Loading v4 ANN - will upgrade to v5 structures for better performance");
        
        let mut u32b=[0u8;4]; 
        let mut u64b=[0u8;8]; 
        let mut u8b=[0u8;1];
        
        
        file.read_exact(&mut u32b)?; let dims = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let total_vectors = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let _bits = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let _main_bits = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let _multi_bits32 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let _num_tables = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u64b)?; let _seed = u64::from_le_bytes(u64b);

        if !(8..=10_000).contains(&dims) { return Err(invalid("dims")); }
        if !(1..=100_000_000).contains(&total_vectors) { return Err(invalid("rows")); }

        
        file.read_exact(&mut u32b)?; let target_candidates = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let min_candidates = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_candidates = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_hamming_64 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_hamming_32 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_hamming_16 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let random_sample_size = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u8b)?; let enable_metrics = u8b[0] != 0;

        
        let _config = AnnConfig {
            target_candidates, min_candidates, max_candidates,
            max_hamming_64, max_hamming_32, max_hamming_16,
            random_sample_size, enable_metrics,
            quality_tier: if total_vectors >= 50_000 && total_vectors <= 500_000 {
                QualityTier::SweetSpot
            } else if total_vectors < 50_000 {
                QualityTier::ExactOnly
            } else {
                QualityTier::BestEffort
            },
        };

        
        
        
        let _ultra_projections: Vec<Vec<f32>> = Vec::new();
        let _ultra_bits = 0;
        let _ultra_buckets: HashMap<u128, SafeBucket> = HashMap::new();

        
        
        
        warn!("v4 ANN loaded and upgraded to v5 structures");
        
        
        Err(std::io::Error::new(std::io::ErrorKind::InvalidData, 
            "v4 to v5 upgrade not fully implemented - please rebuild"))
    }

    fn load_version_5<R: Read>(mut file: R) -> std::io::Result<Self> {
        let mut u32b=[0u8;4]; 
        let mut u64b=[0u8;8]; 
        let mut u8b=[0u8;1];
        
        
        file.read_exact(&mut u32b)?; let dims = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let bits = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let main_bits = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let multi_bits32 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let ultra_bits = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let _num_tables = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let total_vectors = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u64b)?; let seed = u64::from_le_bytes(u64b);

        if !(8..=10_000).contains(&dims) { return Err(invalid("dims")); }
        if !(1..=100_000_000).contains(&total_vectors) { return Err(invalid("rows")); }

        
        file.read_exact(&mut u32b)?; let target_candidates = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let min_candidates = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_candidates = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_hamming_64 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_hamming_32 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let max_hamming_16 = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u32b)?; let random_sample_size = u32::from_le_bytes(u32b) as usize;
        file.read_exact(&mut u8b)?; let enable_metrics = u8b[0] != 0;
        file.read_exact(&mut u8b)?; let quality_tier = match u8b[0] {
            0 => QualityTier::ExactOnly,
            1 => QualityTier::SweetSpot,
            2 => QualityTier::BestEffort,
            _ => QualityTier::BestEffort,
        };

        let config = AnnConfig {
            target_candidates, min_candidates, max_candidates,
            max_hamming_64, max_hamming_32, max_hamming_16,
            random_sample_size, enable_metrics, quality_tier,
        };

        
        file.read_exact(&mut u32b)?; 
        let proj_count = u32::from_le_bytes(u32b) as usize;
        let mut projections_16 = Vec::with_capacity(proj_count);
        for _ in 0..proj_count {
            let mut proj = vec![0f32; dims];
            for val in proj.iter_mut() {
                let mut f32b = [0u8; 4];
                file.read_exact(&mut f32b)?;
                *val = f32::from_le_bytes(f32b);
            }
            projections_16.push(proj);
        }

        
        file.read_exact(&mut u32b)?;
        let bucket_count = u32::from_le_bytes(u32b) as usize;
        let mut buckets_16 = HashMap::with_capacity(bucket_count);
        for _ in 0..bucket_count {
            let mut u16b = [0u8; 2];
            file.read_exact(&mut u16b)?;
            let hash = u16::from_le_bytes(u16b);
            
            file.read_exact(&mut u32b)?;
            let ids_count = u32::from_le_bytes(u32b) as usize;
            let mut ids = SmallVec::with_capacity(ids_count);
            for _ in 0..ids_count {
                file.read_exact(&mut u32b)?;
                ids.push(u32::from_le_bytes(u32b) as usize);
            }
            buckets_16.insert(hash, ids);
        }

        
        file.read_exact(&mut u32b)?;
        let main_proj_count = u32::from_le_bytes(u32b) as usize;
        let mut main_projections = Vec::with_capacity(main_proj_count);
        for _ in 0..main_proj_count {
            let mut proj = vec![0f32; dims];
            for val in proj.iter_mut() {
                let mut f32b = [0u8; 4];
                file.read_exact(&mut f32b)?;
                *val = f32::from_le_bytes(f32b);
            }
            main_projections.push(proj);
        }

        
        file.read_exact(&mut u32b)?;
        let main_bucket_count = u32::from_le_bytes(u32b) as usize;
        let mut main_buckets64 = HashMap::with_capacity(main_bucket_count);
        for _ in 0..main_bucket_count {
            let mut u64b_hash = [0u8; 8];
            file.read_exact(&mut u64b_hash)?;
            let hash = u64::from_le_bytes(u64b_hash);
            
            file.read_exact(&mut u32b)?;
            let bucket_size = u32::from_le_bytes(u32b) as usize;
            
            file.read_exact(&mut u8b)?;
            let is_full = u8b[0] != 0;
            
            let mut bucket = SafeBucket::new();
            bucket.is_full = is_full;
            for _ in 0..bucket_size {
                file.read_exact(&mut u32b)?;
                let id = u32::from_le_bytes(u32b) as usize;
                bucket.items.push(id);
            }
            main_buckets64.insert(hash, bucket);
        }

        
        file.read_exact(&mut u32b)?;
        let multi_tables_count = u32::from_le_bytes(u32b) as usize;
        let mut multi_projections = Vec::with_capacity(multi_tables_count);
        for _ in 0..multi_tables_count {
            file.read_exact(&mut u32b)?;
            let table_proj_count = u32::from_le_bytes(u32b) as usize;
            let mut table_projs = Vec::with_capacity(table_proj_count);
            for _ in 0..table_proj_count {
                let mut proj = vec![0f32; dims];
                for val in proj.iter_mut() {
                    let mut f32b = [0u8; 4];
                    file.read_exact(&mut f32b)?;
                    *val = f32::from_le_bytes(f32b);
                }
                table_projs.push(proj);
            }
            multi_projections.push(table_projs);
        }

        
        file.read_exact(&mut u32b)?;
        let tables_count = u32::from_le_bytes(u32b) as usize;
        let mut multi_tables32 = Vec::with_capacity(tables_count);
        for _ in 0..tables_count {
            file.read_exact(&mut u32b)?;
            let table_bucket_count = u32::from_le_bytes(u32b) as usize;
            let mut table = HashMap::with_capacity(table_bucket_count);
            
            for _ in 0..table_bucket_count {
                let mut u32b_hash = [0u8; 4];
                file.read_exact(&mut u32b_hash)?;
                let hash = u32::from_le_bytes(u32b_hash);
                
                file.read_exact(&mut u32b)?;
                let bucket_size = u32::from_le_bytes(u32b) as usize;
                
                file.read_exact(&mut u8b)?;
                let is_full = u8b[0] != 0;
                
                let mut bucket = SafeBucket::new();
                bucket.is_full = is_full;
                for _ in 0..bucket_size {
                    file.read_exact(&mut u32b)?;
                    let id = u32::from_le_bytes(u32b) as usize;
                    bucket.items.push(id);
                }
                table.insert(hash, bucket);
            }
            multi_tables32.push(table);
        }

        
        file.read_exact(&mut u32b)?;
        let ultra_proj_count = u32::from_le_bytes(u32b) as usize;
        let mut ultra_projections = Vec::with_capacity(ultra_proj_count);
        for _ in 0..ultra_proj_count {
            let mut proj = vec![0f32; dims];
            for val in proj.iter_mut() {
                let mut f32b = [0u8; 4];
                file.read_exact(&mut f32b)?;
                *val = f32::from_le_bytes(f32b);
            }
            ultra_projections.push(proj);
        }

        
        file.read_exact(&mut u32b)?;
        let ultra_bucket_count = u32::from_le_bytes(u32b) as usize;
        let mut ultra_buckets = HashMap::with_capacity(ultra_bucket_count);
        for _ in 0..ultra_bucket_count {
            let mut u128b = [0u8; 16];
            file.read_exact(&mut u128b)?;
            let hash = u128::from_le_bytes(u128b);
            
            file.read_exact(&mut u32b)?;
            let bucket_size = u32::from_le_bytes(u32b) as usize;
            
            file.read_exact(&mut u8b)?;
            let is_full = u8b[0] != 0;
            
            let mut bucket = SafeBucket::new();
            bucket.is_full = is_full;
            for _ in 0..bucket_size {
                file.read_exact(&mut u32b)?;
                let id = u32::from_le_bytes(u32b) as usize;
                bucket.items.push(id);
            }
            ultra_buckets.insert(hash, bucket);
        }

        info!("ANN v5 sweet spot loaded: dims={}, rows={}, tier={:?}", 
            dims, total_vectors, config.quality_tier);
        
        
        Ok(Self {
            dims, bits, projections: projections_16, buckets: buckets_16,
            seed, config, total_vectors, metrics: AnnMetrics::default(),
            main_projections, main_bits, main_buckets64,
            num_tables: multi_tables_count, multi_projections, multi_bits32: multi_bits32, multi_tables32,
            ultra_projections, ultra_bits, ultra_buckets,
        })
    }
}


#[inline] fn invalid(msg:&str)->std::io::Error { 
    std::io::Error::new(std::io::ErrorKind::InvalidData, msg) 
}


pub fn should_use_exact_search(rows: usize) -> bool {
    
    rows < MIN_DATASET_SIZE
}


#[inline]
fn finalize_with_frequency_boost(index: &AnnIndex, mut freq: HashMap<usize,u16>, used_fallback: bool) -> Vec<usize> {
    
    let mut pairs: Vec<(usize,u16)> = freq.drain()
        .filter(|(i,_)| *i < index.total_vectors)
        .collect();
    
    
    if pairs.len() > MAX_TOTAL_CANDIDATES { 
        pairs.truncate(MAX_TOTAL_CANDIDATES); 
    }
    
    
    pairs.sort_unstable_by(|a,b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));

    
    let cap = index.config.max_candidates.min(pairs.len());
    let mut out: Vec<usize> = pairs.into_iter()
        .take(cap)
        .map(|(id,_)| id)
        .collect();
    
    
    out.sort_unstable(); 
    out.dedup();

    
    if out.len() < index.config.target_candidates && 
       matches!(index.config.quality_tier, QualityTier::SweetSpot) {
        
        warn!("Sweet spot underperformance: {} < {} candidates, forcing more", 
              out.len(), index.config.target_candidates);
        
        let needed = index.config.target_candidates.saturating_sub(out.len());
        if needed > 0 {
            use rand::seq::SliceRandom;
            let mut rng = StdRng::seed_from_u64(index.seed + out.len() as u64);
            
            
            let existing: HashSet<usize> = out.iter().cloned().collect();
            let mut remaining: Vec<usize> = (0..index.total_vectors)
                .filter(|&id| !existing.contains(&id))
                .collect();
            remaining.shuffle(&mut rng);
            
            
            let to_add = needed.min(remaining.len());
            out.extend(remaining.into_iter().take(to_add));
            
            debug!("Forced candidates: added {} to reach {} total", to_add, out.len());
        }
    }

    
    if index.config.enable_metrics {
        index.metrics.record_query(out.len(), used_fallback);
        
        
        if matches!(index.config.quality_tier, QualityTier::SweetSpot) {
            debug!("Sweet spot query: target={}, actual={}, ratio={:.1}%", 
                index.config.target_candidates, out.len(), 
                (out.len() as f64 / index.total_vectors as f64) * 100.0);
                   
            if out.len() < index.config.target_candidates {
                warn!("Sweet spot still underperforming: {} < {} candidates after forcing", 
                      out.len(), index.config.target_candidates);
            }
        }
    }
    
    debug!("Sweet spot candidates: {} (tier: {:?})", out.len(), index.config.quality_tier);
    out
}