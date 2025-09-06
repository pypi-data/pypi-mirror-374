#!/usr/bin/env python3
"""
Comprehensive Performance Test: Original vs Optimized vs Ultra-Optimized vinormx
"""

import time
import statistics
from typing import List, Dict, Any
from vinormx import TTSnorm as OriginalTTSnorm
from vinormx_optimized import OptimizedVinormx
from vinormx_ultra_optimized import UltraOptimizedVinormx

def comprehensive_performance_test():
    """Comprehensive performance test comparing all versions"""
    print("🏁 COMPREHENSIVE PERFORMANCE TEST")
    print("=" * 80)
    print("Testing: Original vs Optimized vs Ultra-Optimized vinormx")
    print("=" * 80)
    
    # Test texts with various complexities
    test_texts = [
        # Simple texts
        "ANTQ là gì?",
        "Ngày 25/12/2023",
        "Email: test@example.com",
        "Phone: 0123456789",
        
        # Medium texts
        "Ngày 25/12/2023, tôi đã gặp anh ấy tại văn phòng ANTQ. Email: test@example.com",
        "Thông tin liên hệ: Phone: 0123456789, Email: contact@example.com, Website: https://www.example.com",
        "Lịch trình: Ngày 15/03/2024: Họp lúc 09:00, Ngày 20/03/2024: Họp lúc 14:30",
        
        # Complex texts
        " ".join([f"Ngày {i:02d}/{(i%12)+1:02d}/2024" for i in range(1, 31)]),
        " ".join([f"user{i}@example.com" for i in range(1, 101)]),
        " ".join([f"0{123456789 + i}" for i in range(50)]),
        
        # Very complex text
        " ".join([f"ANTQ là gì? Ngày {i:02d}/{(i%12)+1:02d}/2024, tôi đã gặp anh ấy tại văn phòng ANTQ. Email: user{i}@example.com, Phone: 0{123456789 + i}, Website: https://www.example{i}.com" for i in range(1, 21)]),
    ]
    
    iterations = 3
    
    # Test configurations
    configs = [
        ("Original", "Original vinormx", lambda: test_original(test_texts, iterations)),
        ("Optimized", "Optimized vinormx (basic)", 
         lambda: test_optimized(test_texts, iterations, enable_caching=True, chunk_size=1000)),
        ("Ultra-Optimized", "Ultra-optimized vinormx (advanced)", 
         lambda: test_ultra_optimized(test_texts, iterations, enable_caching=True, chunk_size=1000, enable_pattern_filtering=True)),
    ]
    
    results = {}
    
    for config_name, description, test_func in configs:
        print(f"\n📊 Testing: {description}")
        print("-" * 60)
        
        try:
            result = test_func()
            results[config_name] = result
            
            print(f"   Average time: {result['avg_time']:.4f}s")
            print(f"   Min time: {result['min_time']:.4f}s")
            print(f"   Max time: {result['max_time']:.4f}s")
            print(f"   Std dev: {result['std_dev']:.4f}s")
            print(f"   Total time: {result['total_time']:.4f}s")
            
            if 'stats' in result:
                stats = result['stats']
                print(f"   Cache hit rate: {stats['cache_hit_rate']:.2%}")
                print(f"   Texts per second: {stats['texts_per_second']:.2f}")
                if 'pattern_filter_hit_rate' in stats:
                    print(f"   Pattern filter hit rate: {stats['pattern_filter_hit_rate']:.2%}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[config_name] = None
    
    # Analysis
    print("\n" + "=" * 80)
    print("📈 PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    # Sort by average time
    valid_results = {k: v for k, v in results.items() if v is not None}
    sorted_results = sorted(valid_results.items(), key=lambda x: x[1]['avg_time'])
    
    print("\n🏆 Performance Ranking (Fastest to Slowest):")
    for i, (config_name, result) in enumerate(sorted_results, 1):
        print(f"{i:2d}. {config_name:20s} - {result['avg_time']:.4f}s")
    
    # Calculate improvements
    if 'Original' in valid_results:
        original_time = valid_results['Original']['avg_time']
        
        print(f"\n💡 OPTIMIZATION RESULTS:")
        print(f"   Original time: {original_time:.4f}s")
        
        for config_name, result in valid_results.items():
            if config_name != 'Original':
                improvement = ((original_time - result['avg_time']) / original_time) * 100
                speedup = original_time / result['avg_time']
                print(f"   {config_name:20s}: {result['avg_time']:.4f}s ({improvement:+.1f}% improvement, {speedup:.2f}x speedup)")
    
    # Efficiency analysis
    print(f"\n📊 EFFICIENCY METRICS:")
    total_chars = sum(len(text) for text in test_texts)
    print(f"   Total characters processed: {total_chars:,}")
    
    for config_name, result in valid_results.items():
        if result:
            chars_per_second = total_chars / result['avg_time']
            print(f"   {config_name:20s}: {chars_per_second:,.0f} chars/sec")
    
    return results

def test_original(test_texts: List[str], iterations: int) -> Dict[str, float]:
    """Test original vinormx"""
    times = []
    for i in range(iterations):
        start_time = time.time()
        for text in test_texts:
            OriginalTTSnorm(text)
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"   Iteration {i+1}: {times[-1]:.4f}s")
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'total_time': sum(times)
    }

def test_optimized(test_texts: List[str], iterations: int, **kwargs) -> Dict[str, float]:
    """Test optimized vinormx"""
    optimized = OptimizedVinormx(**kwargs)
    times = []
    for i in range(iterations):
        start_time = time.time()
        for text in test_texts:
            optimized.normalize(text)
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"   Iteration {i+1}: {times[-1]:.4f}s")
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'total_time': sum(times),
        'stats': optimized.get_performance_stats()
    }

def test_ultra_optimized(test_texts: List[str], iterations: int, **kwargs) -> Dict[str, float]:
    """Test ultra-optimized vinormx"""
    ultra_optimized = UltraOptimizedVinormx(**kwargs)
    times = []
    for i in range(iterations):
        start_time = time.time()
        for text in test_texts:
            ultra_optimized.normalize(text)
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"   Iteration {i+1}: {times[-1]:.4f}s")
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'total_time': sum(times),
        'stats': ultra_optimized.get_performance_stats()
    }

def test_memory_efficiency():
    """Test memory efficiency of different versions"""
    print("\n🧠 MEMORY EFFICIENCY TEST")
    print("-" * 40)
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test with repeated processing
        test_text = "ANTQ là gì? Ngày 25/12/2023, tôi đã gặp anh ấy tại văn phòng ANTQ. Email: test@example.com"
        
        # Test original
        print("Testing Original vinormx memory usage...")
        for _ in range(100):
            OriginalTTSnorm(test_text)
        original_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test optimized
        print("Testing Optimized vinormx memory usage...")
        optimized = OptimizedVinormx(enable_caching=True, cache_size=100)
        for _ in range(100):
            optimized.normalize(test_text)
        optimized_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test ultra-optimized
        print("Testing Ultra-Optimized vinormx memory usage...")
        ultra_optimized = UltraOptimizedVinormx(enable_caching=True, cache_size=100, enable_pattern_filtering=True)
        for _ in range(100):
            ultra_optimized.normalize(test_text)
        ultra_optimized_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"   Initial memory: {initial_memory:.1f} MB")
        print(f"   Original memory: {original_memory:.1f} MB (+{original_memory - initial_memory:.1f} MB)")
        print(f"   Optimized memory: {optimized_memory:.1f} MB (+{optimized_memory - initial_memory:.1f} MB)")
        print(f"   Ultra-optimized memory: {ultra_optimized_memory:.1f} MB (+{ultra_optimized_memory - initial_memory:.1f} MB)")
        
        return {
            'initial_memory': initial_memory,
            'original_memory': original_memory,
            'optimized_memory': optimized_memory,
            'ultra_optimized_memory': ultra_optimized_memory
        }
        
    except ImportError:
        print("   ⚠️  psutil not available - skipping memory test")
        return None

def main():
    """Main comprehensive performance test"""
    # Run comprehensive test
    results = comprehensive_performance_test()
    
    # Test memory efficiency
    memory_results = test_memory_efficiency()
    
    print("\n✅ Comprehensive performance test completed!")
    
    # Summary
    print("\n📋 SUMMARY:")
    print("   - Original vinormx: Baseline performance")
    print("   - Optimized vinormx: Enhanced with caching and chunking")
    print("   - Ultra-optimized vinormx: Maximum performance with advanced optimizations")
    print("   - Check results above for specific improvements and recommendations")
    
    return results, memory_results

if __name__ == "__main__":
    main()
