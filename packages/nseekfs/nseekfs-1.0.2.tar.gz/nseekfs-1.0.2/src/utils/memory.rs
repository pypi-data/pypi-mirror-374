



use std::cell::RefCell;
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};


thread_local! {
    static SCORE_BUFFER: RefCell<Vec<f32>> = RefCell::new(Vec::new());
    static INDEX_BUFFER: RefCell<Vec<usize>> = RefCell::new(Vec::new());
    static TEMP_VECTOR_BUFFER: RefCell<Vec<f32>> = RefCell::new(Vec::new());
}


pub struct BufferPool<T> {
    buffers: Arc<Mutex<VecDeque<Vec<T>>>>,
    max_size: usize,
}

impl<T: Clone + Default> BufferPool<T> {
    pub fn new(max_size: usize) -> Self {
        Self {
            buffers: Arc::new(Mutex::new(VecDeque::new())),
            max_size,
        }
    }
    
    pub fn get_buffer(&self, min_capacity: usize) -> Vec<T> {
        if let Ok(mut buffers) = self.buffers.try_lock() {
            if let Some(mut buffer) = buffers.pop_front() {
                if buffer.capacity() >= min_capacity {
                    buffer.clear();
                    return buffer;
                }
            }
        }
        
        Vec::with_capacity(min_capacity)
    }
    
    pub fn return_buffer(&self, buffer: Vec<T>) {
        if let Ok(mut buffers) = self.buffers.try_lock() {
            if buffers.len() < self.max_size {
                buffers.push_back(buffer);
            }
        }
    }
}


pub struct ThreadLocalBuffer<T> {
    _phantom: std::marker::PhantomData<T>,
}

impl<T> ThreadLocalBuffer<T> {
    pub fn new() -> Self {
        Self {
            _phantom: std::marker::PhantomData,
        }
    }
}

impl ThreadLocalBuffer<f32> {
    pub fn with_score_buffer<F, R>(&self, min_capacity: usize, f: F) -> R
    where
        F: FnOnce(&mut Vec<f32>) -> R,
    {
        SCORE_BUFFER.with(|buffer| {
            let mut buffer = buffer.borrow_mut();
            let current_capacity = buffer.capacity();
            if current_capacity < min_capacity {
                buffer.reserve(min_capacity - current_capacity);
            }
            buffer.clear();
            f(&mut buffer)
        })
    }
    
    pub fn with_temp_vector<F, R>(&self, min_capacity: usize, f: F) -> R
    where
        F: FnOnce(&mut Vec<f32>) -> R,
    {
        TEMP_VECTOR_BUFFER.with(|buffer| {
            let mut buffer = buffer.borrow_mut();
            let current_capacity = buffer.capacity();
            if current_capacity < min_capacity {
                buffer.reserve(min_capacity - current_capacity);
            }
            buffer.clear();
            f(&mut buffer)
        })
    }
}

impl ThreadLocalBuffer<usize> {
    pub fn with_index_buffer<F, R>(&self, min_capacity: usize, f: F) -> R
    where
        F: FnOnce(&mut Vec<usize>) -> R,
    {
        INDEX_BUFFER.with(|buffer| {
            let mut buffer = buffer.borrow_mut();
            let current_capacity = buffer.capacity();
            if current_capacity < min_capacity {
                buffer.reserve(min_capacity - current_capacity);
            }
            buffer.clear();
            f(&mut buffer)
        })
    }
}


#[repr(align(64))] 
pub struct CacheAligned<T>(pub T);


pub struct VectorPool {
    small_pool: BufferPool<f32>,  
    medium_pool: BufferPool<f32>, 
    large_pool: BufferPool<f32>,  
}

impl VectorPool {
    pub fn new() -> Self {
        Self {
            small_pool: BufferPool::new(16),
            medium_pool: BufferPool::new(8),
            large_pool: BufferPool::new(4),
        }
    }
    
    pub fn get_vector(&self, size: usize) -> Vec<f32> {
        match size {
            0..=256 => self.small_pool.get_buffer(size),
            257..=1024 => self.medium_pool.get_buffer(size),
            _ => self.large_pool.get_buffer(size),
        }
    }
    
    pub fn return_vector(&self, vector: Vec<f32>) {
        let capacity = vector.capacity();
        match capacity {
            0..=256 => self.small_pool.return_buffer(vector),
            257..=1024 => self.medium_pool.return_buffer(vector),
            _ => self.large_pool.return_buffer(vector),
        }
    }
}


pub struct MemoryTracker {
    peak_usage: Arc<Mutex<usize>>,
    current_usage: Arc<Mutex<usize>>,
}

impl MemoryTracker {
    pub fn new() -> Self {
        Self {
            peak_usage: Arc::new(Mutex::new(0)),
            current_usage: Arc::new(Mutex::new(0)),
        }
    }
    
    pub fn allocate(&self, size: usize) {
        if let (Ok(mut current), Ok(mut peak)) = (
            self.current_usage.try_lock(),
            self.peak_usage.try_lock(),
        ) {
            *current += size;
            if *current > *peak {
                *peak = *current;
            }
        }
    }
    
    pub fn deallocate(&self, size: usize) {
        if let Ok(mut current) = self.current_usage.try_lock() {
            *current = current.saturating_sub(size);
        }
    }
    
    
    pub fn get_current_usage(&self) -> usize {
        match self.current_usage.lock() {
            Ok(guard) => *guard,
            Err(poisoned) => {
                
                let guard = poisoned.into_inner();
                *guard
            }
        }
    }
    
    
    pub fn get_peak_usage(&self) -> usize {
        match self.peak_usage.lock() {
            Ok(guard) => *guard,
            Err(poisoned) => {
                let guard = poisoned.into_inner();
                *guard
            }
        }
    }
    
    pub fn reset(&self) {
        if let (Ok(mut current), Ok(mut peak)) = (
            self.current_usage.try_lock(),
            self.peak_usage.try_lock(),
        ) {
            *current = 0;
            *peak = 0;
        }
    }
}


pub struct PreallocatedBuffers {
    pub query_buffer: Vec<f32>,
    pub score_buffer: Vec<f32>,
    pub index_buffer: Vec<usize>,
    pub temp_buffer: Vec<f32>,
}

impl PreallocatedBuffers {
    pub fn new(max_dims: usize, max_vectors: usize) -> Self {
        Self {
            query_buffer: Vec::with_capacity(max_dims),
            score_buffer: Vec::with_capacity(max_vectors),
            index_buffer: Vec::with_capacity(max_vectors),
            temp_buffer: Vec::with_capacity(max_dims * 2),
        }
    }
    
    pub fn reset(&mut self) {
        self.query_buffer.clear();
        self.score_buffer.clear();
        self.index_buffer.clear();
        self.temp_buffer.clear();
    }
    
    pub fn resize_if_needed(&mut self, dims: usize, vectors: usize) {
        if self.query_buffer.capacity() < dims {
            self.query_buffer.reserve(dims - self.query_buffer.capacity());
        }
        if self.score_buffer.capacity() < vectors {
            self.score_buffer.reserve(vectors - self.score_buffer.capacity());
        }
        if self.index_buffer.capacity() < vectors {
            self.index_buffer.reserve(vectors - self.index_buffer.capacity());
        }
        if self.temp_buffer.capacity() < dims * 2 {
            self.temp_buffer.reserve(dims * 2 - self.temp_buffer.capacity());
        }
    }
}


#[repr(align(64))]
pub struct AlignedVector<T> {
    data: Vec<T>,
}

impl<T> AlignedVector<T> {
    pub fn new() -> Self {
        Self { data: Vec::new() }
    }
    
    pub fn with_capacity(capacity: usize) -> Self {
        Self { data: Vec::with_capacity(capacity) }
    }
    
    pub fn as_slice(&self) -> &[T] {
        &self.data
    }
    
    pub fn as_mut_slice(&mut self) -> &mut [T] {
        &mut self.data
    }
    
    pub fn push(&mut self, value: T) {
        self.data.push(value);
    }
    
    pub fn len(&self) -> usize {
        self.data.len()
    }
    
    pub fn clear(&mut self) {
        self.data.clear();
    }
}


pub struct AlignedVectorPool<T> {
    pool: BufferPool<T>,
}

impl<T: Clone + Default> AlignedVectorPool<T> {
    pub fn new() -> Self {
        Self { pool: BufferPool::new(8) }
    }
    
    pub fn get_aligned_vector(&self, capacity: usize) -> AlignedVector<T> {
        let buffer = self.pool.get_buffer(capacity);
        AlignedVector { data: buffer }
    }
    
    pub fn return_aligned_vector(&self, mut vector: AlignedVector<T>) {
        vector.clear();
        self.pool.return_buffer(vector.data);
    }
}


lazy_static::lazy_static! {
    pub static ref GLOBAL_VECTOR_POOL: VectorPool = VectorPool::new();
    pub static ref GLOBAL_MEMORY_TRACKER: MemoryTracker = MemoryTracker::new();
}


pub struct SpecializedBuffers {
    
    pub similarity_buffer: BufferPool<f32>,
    pub index_buffer: BufferPool<usize>,
    
    
    pub simd_temp_buffer: BufferPool<f32>,
    pub alignment_buffer: BufferPool<f32>,
    
    
    pub sort_pairs_buffer: BufferPool<(usize, f32)>,
    pub sort_indices_buffer: BufferPool<usize>,
}

impl SpecializedBuffers {
    pub fn new() -> Self {
        Self {
            similarity_buffer: BufferPool::new(8),
            index_buffer: BufferPool::new(8),
            simd_temp_buffer: BufferPool::new(4),
            alignment_buffer: BufferPool::new(4),
            sort_pairs_buffer: BufferPool::new(4),
            sort_indices_buffer: BufferPool::new(4),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_buffer_pool() {
        let pool = BufferPool::<f32>::new(2);
        
        let buffer1 = pool.get_buffer(100);
        assert!(buffer1.capacity() >= 100);
        
        pool.return_buffer(buffer1);
        
        let buffer2 = pool.get_buffer(50);
        assert!(buffer2.capacity() >= 50);
    }
    
    #[test]
    fn test_aligned_vector() {
        let mut vec = AlignedVector::<f32>::with_capacity(64);
        vec.push(1.0);
        vec.push(2.0);
        
        assert_eq!(vec.len(), 2);
        assert_eq!(vec.as_slice()[0], 1.0);

        
        assert!(std::mem::align_of::<AlignedVector<f32>>() >= 64);
    }
}
