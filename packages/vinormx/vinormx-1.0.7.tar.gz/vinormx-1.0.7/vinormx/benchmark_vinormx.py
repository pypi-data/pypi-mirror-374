#!/usr/bin/env python3
"""
Comprehensive Benchmark for vinormx Performance
Tests various text types and lengths to identify performance bottlenecks
"""

import time
import random
import string
from vinormx import TTSnorm
import statistics

class VinormxBenchmark:
    def __init__(self):
        self.results = {}
        
    def generate_long_paragraph(self, length=1000):
        """Generate a long paragraph with mixed content"""
        words = [
            "ngày", "tháng", "năm", "giờ", "phút", "giây", "tuần", "tháng",
            "năm", "thế kỷ", "thiên niên kỷ", "thập kỷ", "thập niên",
            "ANTQ", "VNPT", "FPT", "Viettel", "Mobifone", "Vinaphone",
            "email", "website", "phone", "address", "street", "office",
            "COVID-19", "SARS-CoV-2", "vaccine", "quarantine", "lockdown",
            "economy", "politics", "sports", "football", "basketball",
            "technology", "artificial intelligence", "machine learning",
            "blockchain", "cryptocurrency", "bitcoin", "ethereum",
            "government", "ministry", "department", "agency", "organization",
            "company", "corporation", "enterprise", "business", "industry",
            "education", "university", "college", "school", "student",
            "healthcare", "hospital", "clinic", "doctor", "nurse",
            "transportation", "airport", "station", "bus", "train",
            "entertainment", "movie", "music", "game", "sport",
            "food", "restaurant", "hotel", "travel", "tourism"
        ]
        
        # Generate paragraph with mixed content
        paragraph = []
        for i in range(length):
            if i % 10 == 0:  # Add numbers
                paragraph.append(str(random.randint(1, 9999)))
            elif i % 15 == 0:  # Add dates
                paragraph.append(f"{random.randint(1, 31):02d}/{random.randint(1, 12):02d}/{random.randint(2000, 2024)}")
            elif i % 20 == 0:  # Add times
                paragraph.append(f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}")
            elif i % 25 == 0:  # Add phone numbers
                paragraph.append(f"0{random.randint(100000000, 999999999)}")
            elif i % 30 == 0:  # Add emails
                paragraph.append(f"user{random.randint(1, 1000)}@example.com")
            elif i % 35 == 0:  # Add websites
                paragraph.append(f"https://www.example{random.randint(1, 100)}.com")
            elif i % 40 == 0:  # Add measurements
                paragraph.append(f"{random.randint(1, 100)}km")
            elif i % 45 == 0:  # Add currency
                paragraph.append(f"{random.randint(1, 1000000)} VND")
            else:  # Add regular words
                paragraph.append(random.choice(words))
        
        return " ".join(paragraph)
    
    def generate_technical_text(self, length=500):
        """Generate technical text with lots of numbers and symbols"""
        tech_words = [
            "CPU", "GPU", "RAM", "SSD", "HDD", "USB", "HDMI", "WiFi", "Bluetooth",
            "API", "SDK", "SDK", "framework", "library", "database", "server",
            "client", "protocol", "algorithm", "function", "variable", "class",
            "object", "method", "property", "attribute", "parameter", "argument",
            "return", "value", "type", "string", "integer", "float", "boolean",
            "array", "list", "dictionary", "tuple", "set", "enum", "interface",
            "abstract", "concrete", "inheritance", "polymorphism", "encapsulation",
            "abstraction", "composition", "aggregation", "association", "dependency"
        ]
        
        text = []
        for i in range(length):
            if i % 8 == 0:  # Add version numbers
                text.append(f"v{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}")
            elif i % 12 == 0:  # Add percentages
                text.append(f"{random.randint(0, 100)}%")
            elif i % 16 == 0:  # Add coordinates
                text.append(f"({random.randint(-90, 90)}, {random.randint(-180, 180)})")
            elif i % 20 == 0:  # Add file sizes
                text.append(f"{random.randint(1, 1000)}MB")
            elif i % 24 == 0:  # Add IP addresses
                text.append(f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}")
            else:
                text.append(random.choice(tech_words))
        
        return " ".join(text)
    
    def generate_mixed_content(self, length=800):
        """Generate mixed content with various text types"""
        content = []
        
        # Add some long paragraphs
        content.append(self.generate_long_paragraph(200))
        content.append("\n\n")
        
        # Add technical text
        content.append(self.generate_technical_text(150))
        content.append("\n\n")
        
        # Add some structured data
        content.append("Thông tin liên hệ:")
        content.append("Email: contact@example.com")
        content.append("Phone: 0123456789")
        content.append("Address: 123 Đường ABC, Quận 1, TP.HCM")
        content.append("Website: https://www.example.com")
        content.append("\n")
        
        # Add some dates and times
        content.append("Lịch trình:")
        content.append("Ngày 15/03/2024: Họp lúc 09:00")
        content.append("Ngày 20/03/2024: Họp lúc 14:30")
        content.append("Ngày 25/03/2024: Họp lúc 16:00")
        content.append("\n")
        
        # Add some measurements
        content.append("Thông số kỹ thuật:")
        content.append("Chiều dài: 150cm")
        content.append("Chiều rộng: 80cm")
        content.append("Chiều cao: 200cm")
        content.append("Trọng lượng: 50kg")
        content.append("\n")
        
        # Add some currency
        content.append("Bảng giá:")
        content.append("Sản phẩm A: 1,000,000 VND")
        content.append("Sản phẩm B: 2,500,000 VND")
        content.append("Sản phẩm C: 5,000,000 VND")
        
        return " ".join(content)
    
    def benchmark_single_text(self, text, iterations=10):
        """Benchmark a single text multiple times"""
        times = []
        for _ in range(iterations):
            start_time = time.time()
            result = TTSnorm(text)
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            'text_length': len(text),
            'iterations': iterations,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'total_time': sum(times)
        }
    
    def run_comprehensive_benchmark(self):
        """Run comprehensive benchmark with various text types and lengths"""
        print("🚀 Starting Comprehensive vinormx Benchmark")
        print("=" * 60)
        
        # Test cases
        test_cases = [
            ("Short Text", "ANTQ là gì?"),
            ("Medium Text", "Ngày 25/12/2023, tôi đã gặp anh ấy tại văn phòng ANTQ."),
            ("Long Paragraph", self.generate_long_paragraph(500)),
            ("Very Long Paragraph", self.generate_long_paragraph(1000)),
            ("Technical Text", self.generate_technical_text(300)),
            ("Mixed Content", self.generate_mixed_content(600)),
            ("Date Heavy", " ".join([f"Ngày {i:02d}/{(i%12)+1:02d}/2024" for i in range(1, 31)])),
            ("Number Heavy", " ".join([str(i) for i in range(1, 201)])),
            ("Email Heavy", " ".join([f"user{i}@example.com" for i in range(1, 101)])),
            ("Phone Heavy", " ".join([f"0{random.randint(100000000, 999999999)}" for _ in range(50)])),
        ]
        
        results = {}
        
        for name, text in test_cases:
            print(f"\n📊 Testing: {name}")
            print(f"   Text length: {len(text)} characters")
            
            # Run benchmark
            result = self.benchmark_single_text(text, iterations=5)
            results[name] = result
            
            print(f"   Average time: {result['avg_time']:.4f}s")
            print(f"   Min time: {result['min_time']:.4f}s")
            print(f"   Max time: {result['max_time']:.4f}s")
            print(f"   Std dev: {result['std_dev']:.4f}s")
            print(f"   Total time: {result['total_time']:.4f}s")
        
        # Analysis
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Sort by average time
        sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_time'], reverse=True)
        
        print("\n🏆 Slowest to Fastest:")
        for i, (name, result) in enumerate(sorted_results, 1):
            print(f"{i:2d}. {name:20s} - {result['avg_time']:.4f}s ({result['text_length']} chars)")
        
        # Performance insights
        print("\n🔍 PERFORMANCE INSIGHTS:")
        
        # Text length vs time correlation
        lengths = [r['text_length'] for r in results.values()]
        times = [r['avg_time'] for r in results.values()]
        
        if len(lengths) > 1:
            correlation = self.calculate_correlation(lengths, times)
            print(f"   Text length vs time correlation: {correlation:.3f}")
        
        # Identify bottlenecks
        slowest = sorted_results[0]
        print(f"   Slowest test: {slowest[0]} ({slowest[1]['avg_time']:.4f}s)")
        
        # Performance recommendations
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        
        if slowest[1]['avg_time'] > 1.0:
            print("   ⚠️  Performance is slow (>1s) - consider optimization")
        
        if slowest[1]['text_length'] > 1000:
            print("   📝 Long text processing is slow - consider chunking")
        
        if slowest[1]['std_dev'] > slowest[1]['avg_time'] * 0.5:
            print("   📊 High variance in processing time - consider caching")
        
        # Memory usage estimation
        total_chars = sum(r['text_length'] for r in results.values())
        total_time = sum(r['total_time'] for r in results.values())
        chars_per_second = total_chars / total_time if total_time > 0 else 0
        
        print(f"\n📊 THROUGHPUT:")
        print(f"   Total characters processed: {total_chars:,}")
        print(f"   Total processing time: {total_time:.4f}s")
        print(f"   Characters per second: {chars_per_second:,.0f}")
        
        return results
    
    def calculate_correlation(self, x, y):
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator

def main():
    benchmark = VinormxBenchmark()
    results = benchmark.run_comprehensive_benchmark()
    
    print("\n✅ Benchmark completed!")
    print("   Check the results above for performance insights and optimization opportunities.")

if __name__ == "__main__":
    main()
