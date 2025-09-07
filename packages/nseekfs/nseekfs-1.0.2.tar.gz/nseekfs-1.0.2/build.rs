use std::env;

fn main() {
    println!("cargo:rerun-if-changed=src/");
    println!("cargo:rerun-if-changed=build.rs");
    
    let profile = env::var("PROFILE").unwrap_or_default();
    if profile == "release" {
        #[cfg(target_os = "linux")]
        {
            println!("cargo:rustc-link-arg=-Wl,--gc-sections");
            println!("cargo:rustc-link-arg=-Wl,--strip-all");
        }
    }
    
    #[cfg(target_os = "linux")]
    {
        println!("cargo:rustc-link-lib=pthread");
    }
    
    #[cfg(target_os = "windows")]
    {
        println!("cargo:rustc-link-lib=kernel32");
    }
    
    let target = env::var("TARGET").unwrap_or_default();
    println!("cargo:warning=Building NSeekFS for target: {}", target);
    println!("cargo:warning=Profile: {}", profile);
    
    #[cfg(feature = "simd")]
    println!("cargo:warning=SIMD optimizations enabled");
}