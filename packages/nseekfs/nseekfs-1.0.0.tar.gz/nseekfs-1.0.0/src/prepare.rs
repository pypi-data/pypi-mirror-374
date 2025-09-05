use rayon::prelude::*;
use std::fs::{OpenOptions, remove_file, rename, create_dir_all};
use std::path::{Path, PathBuf};
use wide::f32x8;
use memmap2::MmapMut;
use std::time::Instant;
use dirs;
use std::io::{self, Write};
use log::{info, warn, debug};


#[allow(unused_imports)]
use crate::ann_opt::{AnnIndex, should_use_exact_search};


const MAX_FILE_SIZE: u64 = 100 * 1024 * 1024 * 1024; 


pub fn prepare_bin_from_embeddings(
    embeddings: &[f32],
    dims: usize,
    rows: usize,
    base_name: &str,
    level: &str,
    output_dir: Option<&std::path::Path>,
    ann: bool,  
    normalize: bool,
    _seed: u64,  
) -> Result<std::path::PathBuf, String> {
    let total_start = Instant::now();
    info!("⏱️ Starting prepare_bin_from_embeddings (v1.0 - Exact Search Only)");
    io::stdout().flush().unwrap();

    
    let _original_ann_request = ann;  
    let force_ann_disabled = false;   
    
    if ann {
        info!("📄 ANN requested but disabled for v1.0 - using exact search only");
    }

    
    if dims == 0 || rows == 0 {
        return Err("Invalid dimensions: dims and rows must be > 0".into());
    }
    if embeddings.len() != dims * rows {
        return Err(format!(
            "Embedding data shape mismatch: expected {} elements ({}x{}), got {}",
            dims * rows, dims, rows, embeddings.len()
        ));
    }
    if dims < 8 {
        return Err(format!("Minimum 8 dimensions required, got {}", dims));
    }
    if dims > 10000 {
        return Err(format!("Maximum 10000 dimensions allowed, got {}", dims));
    }
    if rows > 100_000_000 {
        return Err(format!("Maximum 100M vectors allowed, got {}", rows));
    }
    if base_name.trim().is_empty() {
        return Err("Base name cannot be empty".into());
    }
    if base_name.contains('/') || base_name.contains('\\') {
        return Err("Base name cannot contain path separators".into());
    }
    match level {
        "f8" | "f16" | "f32" | "f64" => {},
        _ => return Err(format!("Invalid level '{}'. Must be f8, f16, f32, or f64", level)),
    }

    
    let sample_size = (embeddings.len()).min(10000);
    let invalid_count = embeddings[..sample_size].iter().filter(|&&x| !x.is_finite()).count();
    if invalid_count > 0 {
        let percentage = (invalid_count as f64 / sample_size as f64) * 100.0;
        if percentage > 1.0 {
            return Err(format!(
                "Too many invalid values in embeddings: {:.1}% ({}/{})",
                percentage, invalid_count, sample_size
            ));
        } else {
            warn!("Found {} invalid values in embeddings sample", invalid_count);
        }
    }

    info!("✅ Input validation passed: {} vectors × {} dims", rows, dims);

    
    let estimated_memory = dims * rows * 4; 
    let estimated_file_size = 8 + estimated_memory; 

    info!("📊 Estimated memory usage: {:.1}MB", estimated_memory as f64 / (1024.0 * 1024.0));
    info!("📊 Estimated file size: {:.1}MB", estimated_file_size as f64 / (1024.0 * 1024.0));

    if estimated_file_size as u64 > MAX_FILE_SIZE {
        return Err(format!(
            "Estimated file size too large: {:.1}GB (max: {:.1}GB)",
            estimated_file_size as f64 / (1024.0_f64.powi(3)),
            MAX_FILE_SIZE as f64 / (1024.0_f64.powi(3))
        ));
    }

    
    let step1 = Instant::now();
    let mut data = embeddings.to_vec();
    info!("⏱️ [{:.2?}] ✅ Copied embeddings to internal vector", step1.elapsed());
    io::stdout().flush().unwrap();

    if normalize {
        let t = Instant::now();
        normalize_rows_safe(&mut data, dims)?;
        info!("⏱️ [{:.2?}] ✅ Normalization completed", t.elapsed());
        io::stdout().flush().unwrap();
    }

    if level != "f32" {
        let t = Instant::now();
        quantize_in_place_safe(&mut data, level)?;
        info!("⏱️ [{:.2?}] ✅ Quantization to '{}' completed", t.elapsed(), level);
        io::stdout().flush().unwrap();
    }

    
    let output_path = resolve_bin_path_safe(output_dir, base_name, level)?;
    info!("⏱️ [{:.2?}] 📁 Binary path resolved: {:?}", total_start.elapsed(), output_path);
    io::stdout().flush().unwrap();

    
    if let Some(parent) = output_path.parent() {
        check_disk_space(parent, estimated_file_size as u64)?;
    }

    
    if force_ann_disabled {
        let ann_start = Instant::now();
        let ann_file = output_path.with_extension("ann");
        create_ann_stub_for_v1(&ann_file)?;
        info!(
            "✅ [{:.2?}] ANN stub created for v1.0: {:?}",
            ann_start.elapsed(),
            ann_file
        );
    }

    
    let bin_start = std::time::Instant::now();
    write_bin_mmap_safe(&data, dims, rows, &output_path)?;
    info!("✅ [{:.2?}] BIN file written successfully", bin_start.elapsed());
    io::stdout().flush().unwrap();

    let total_time = total_start.elapsed();
    info!("🎯 Total prepare_bin_from_embeddings time: {:.2?}", total_time);
    io::stdout().flush().unwrap();

    Ok(output_path)
}


fn normalize_rows_safe(data: &mut [f32], dims: usize) -> Result<(), String> {
    if data.len() % dims != 0 {
        return Err("Data length not divisible by dimensions".into());
    }

    let rows = data.len() / dims;
    info!("Normalizing {} rows with {} dimensions", rows, dims);

    data.par_chunks_mut(dims)
        .enumerate()
        .try_for_each(|(row_idx, row)| -> Result<(), String> {
            let mut sum = 0.0f32;

            if dims >= 8 {
                let chunks_8 = dims / 8;
                for i in 0..chunks_8 {
                    let start = i * 8;
                    let chunk = &row[start..start + 8];
                    let simd = f32x8::new([
                        chunk[0], chunk[1], chunk[2], chunk[3],
                        chunk[4], chunk[5], chunk[6], chunk[7],
                    ]);
                    let squared = simd * simd;
                    sum += squared.reduce_add();
                }
                for val in &row[chunks_8 * 8..] { sum += val * val; }
            } else {
                for val in row.iter() { sum += val * val; }
            }

            let norm = sum.sqrt();

            if norm == 0.0 {
                return Err(format!("Zero vector found at row {}", row_idx));
            }
            if !norm.is_finite() {
                return Err(format!("Invalid norm at row {}: {}", row_idx, norm));
            }
            if norm < 1e-10 {
                warn!("Very small norm at row {}: {}", row_idx, norm);
            }

            for val in row.iter_mut() {
                *val /= norm;
            }

            Ok(())
        })?;

    info!("Normalization completed successfully");
    Ok(())
}


fn quantize_in_place_safe(_data: &mut [f32], level: &str) -> Result<(), String> {
    match level {
        "f32" => {
            
            Ok(())
        }
        "f16" => {
            
            info!("f16 quantization requested - keeping f32 precision for v1.0");
            Ok(())
        }
        "f8" => {
            
            info!("f8 quantization requested - keeping f32 precision for v1.0");
            Ok(())
        }
        "f64" => {
            
            info!("f64 precision requested - using f32 precision for v1.0");
            Ok(())
        }
        _ => Err(format!("Unsupported quantization level: {}", level))
    }
}


fn create_ann_stub_for_v1(ann_path: &Path) -> Result<(), String> {
    if let Some(parent) = ann_path.parent() {
        if !parent.exists() {
            create_dir_all(parent)
                .map_err(|e| format!("Failed to create ANN directory {}: {}", parent.display(), e))?;
        }
    }

    std::fs::write(ann_path, b"NSEEKFS-V1-EXACT-ONLY")
        .map_err(|e| format!("Failed to write ANN stub {}: {}", ann_path.display(), e))?;

    debug!("ANN stub created for v1.0: {:?}", ann_path);
    Ok(())
}


fn write_bin_mmap_safe(
    data: &[f32],
    dims: usize,
    rows: usize,
    path: &Path
) -> Result<(), String> {
    
    if let Some(parent) = path.parent() {
        create_dir_all(parent).map_err(|e| {
            format!("Failed to create directory {}: {}", parent.display(), e)
        })?;
    }

    
    let tmp_path = path.with_extension("tmp");
    if tmp_path.exists() { remove_file(&tmp_path).ok(); }
    if path.exists()     { remove_file(path).ok(); }

    
    let header_size = 8; 
    let data_bytes_len = data.len() * std::mem::size_of::<f32>();
    let total_size = header_size + data_bytes_len;

    info!("Creating binary file ({} bytes): {:?}", total_size, path);

    
    let file = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(true)
        .open(&tmp_path)
        .map_err(|e| format!("Failed to create temp file {}: {}", tmp_path.display(), e))?;

    file.set_len(total_size as u64).map_err(|e| format!("Failed to set file length: {}", e))?;

    let mut mmap = unsafe {
        MmapMut::map_mut(&file).map_err(|e| format!("Failed to memory map file: {}", e))?
    };

    
    let dims_bytes = (dims as u32).to_le_bytes();
    let rows_bytes = (rows as u32).to_le_bytes();
    mmap[0..4].copy_from_slice(&dims_bytes);
    mmap[4..8].copy_from_slice(&rows_bytes);

    
    let data_offset = header_size;
    unsafe {
        let data_ptr = data.as_ptr() as *const u8;
        let data_slice = std::slice::from_raw_parts(data_ptr, data_bytes_len);
        mmap[data_offset..data_offset + data_bytes_len].copy_from_slice(data_slice);
    }

    
    mmap.flush().map_err(|e| format!("Failed to flush memory map: {}", e))?;
    drop(mmap);

    
    let actual_size = std::fs::metadata(&tmp_path)
        .map_err(|e| format!("Failed to get file metadata: {}", e))?
        .len() as usize;
    if actual_size != total_size {
        remove_file(&tmp_path).ok();
        return Err(format!("File size verification failed: expected {}, got {}", total_size, actual_size));
    }

    
    rename(&tmp_path, path).map_err(|e| format!("Failed to move temp file to final location: {}", e))?;

    info!("Binary file written and verified successfully: {:?} ({:.2}MB)", 
        path, actual_size as f64 / (1024.0 * 1024.0));
    Ok(())
}


pub fn resolve_bin_path_safe(
    output_dir: Option<&Path>,
    base_name: &str,
    level: &str,
) -> Result<PathBuf, String> {
    if base_name.trim().is_empty() {
        return Err("Base name cannot be empty".into());
    }
    if base_name.contains('/') || base_name.contains('\\') || base_name.contains("..") {
        return Err("Base name contains invalid characters".into());
    }

    match level {
        "f8" | "f16" | "f32" | "f64" => {},
        _ => return Err(format!("Invalid level for path: {}", level)),
    }

    let final_path: PathBuf = match output_dir {
        Some(dir) => {
            if !dir.exists() {
                debug!("Output directory doesn't exist, will create: {:?}", dir);
            } else if !dir.is_dir() {
                return Err(format!("Output path is not a directory: {:?}", dir));
            }
            dir.join(format!("{}_{}.bin", base_name, level))
        }
        None => {
            let home = dirs::home_dir().ok_or("Failed to get home directory")?;
            let nseek_dir = home.join(".nseek").join("indexes");
            nseek_dir.join(format!("{}_{}.bin", base_name, level))
        }
    };

    
    if let Some(parent) = final_path.parent() {
        if !parent.exists() {
            create_dir_all(parent).map_err(|e| {
                format!("Failed to create directory {}: {}", parent.display(), e)
            })?;
        }
    }

    Ok(final_path)
}


fn check_disk_space(path: &Path, required_bytes: u64) -> Result<(), String> {
    if !path.exists() {
        debug!("Directory doesn't exist yet: {:?}", path);
        return Ok(()); 
    }
    let test_file = path.join(".nseek_space_test");
    match std::fs::File::create(&test_file) {
        Ok(_) => {
            let _ = std::fs::remove_file(&test_file);
            if required_bytes > 10 * 1024 * 1024 * 1024 {
                warn!(
                    "Large file creation: {:.1}GB - ensure sufficient disk space",
                    required_bytes as f64 / (1024.0_f64.powi(3))
                );
            }
            Ok(())
        }
        Err(e) => Err(format!("Cannot write to directory {}: {}", path.display(), e))
    }
}