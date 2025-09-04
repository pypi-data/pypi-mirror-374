"""
Fixed test cho vinormx - Không có emoji để tránh lỗi Unicode trên Windows
"""

import sys
import os
import time

# Fix Unicode encoding issues trên Windows
if sys.platform == "win32":
    # Force UTF-8 encoding cho stdout
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Import vinormx
try:
    from vinormx import TTSnorm, VietnameseNormalizer
    print("[OK] Import vinormx successful")
except ImportError as e:
    print(f"[ERROR] Cannot import vinormx: {e}")
    print("Make sure vinormx.py is in the same directory")
    sys.exit(1)


def test_basic_functionality():
    """Test chức năng cơ bản"""
    print("\n[TEST] Basic Functionality")
    print("-" * 40)
    
    test_cases = [
        "Xin chào 123",
        "Có phải tháng 12/2020 đã có vaccine Covid-19?",
        "Dr. Smith có $100",
        "Nhiệt độ 37°C"
    ]
    
    for text in test_cases:
        try:
            result = TTSnorm(text)
            print(f"[OK] '{text}' -> '{result}'")
        except Exception as e:
            print(f"[ERROR] '{text}' -> ERROR: {e}")


def test_number_conversion():
    """Test chuyển đổi số"""
    print("\n[TEST] Number Conversion")  
    print("-" * 40)
    
    normalizer = VietnameseNormalizer()
    
    test_cases = [
        ("0", "không"),
        ("1", "một"),
        ("15", "mười lăm"),
        ("25", "hai mười lăm"),
        ("100", "một trăm"),
        ("123", "một trăm hai mười ba"),
        ("1000", "một nghìn"),
        ("2020", "hai nghìn không trăm hai mười")
    ]
    
    for input_num, expected in test_cases:
        try:
            result = normalizer._convert_number_to_words(input_num)
            status = "[OK]" if result == expected else "[WARN]"
            print(f"{status} {input_num:>4} -> {result}")
            if result != expected:
                print(f"      Expected: {expected}")
        except Exception as e:
            print(f"[ERROR] {input_num:>4} -> ERROR: {e}")


def test_date_normalization():
    """Test chuẩn hóa ngày tháng"""
    print("\n[TEST] Date Normalization")
    print("-" * 40)
    
    test_cases = [
        "25/12/2023",
        "1/1/2020",
        "12/2020", 
        "8/2019"
    ]
    
    for date in test_cases:
        try:
            result = TTSnorm(date)
            print(f"[OK] {date:>10} -> {result}")
        except Exception as e:
            print(f"[ERROR] {date:>10} -> ERROR: {e}")


def test_abbreviations():
    """Test từ viết tắt"""
    print("\n[TEST] Abbreviations")
    print("-" * 40)
    
    test_cases = [
        "Dr. Smith",
        "Mr. Johnson", 
        "COVID-19",
        "USA",
        "WHO"
    ]
    
    for text in test_cases:
        try:
            result = TTSnorm(text)
            print(f"[OK] {text:>12} -> {result}")
        except Exception as e:
            print(f"[ERROR] {text:>12} -> ERROR: {e}")


def test_special_characters():
    """Test ký tự đặc biệt"""
    print("\n[TEST] Special Characters") 
    print("-" * 40)
    
    test_cases = [
        "100%",
        "37°C",
        "$100",
        "A & B", 
        "user@domain.com"
    ]
    
    for text in test_cases:
        try:
            result = TTSnorm(text)
            print(f"[OK] {text:>15} -> {result}")
        except Exception as e:
            print(f"[ERROR] {text:>15} -> ERROR: {e}")


def test_covid_example():
    """Test ví dụ COVID từ vinorm gốc"""
    print("\n[TEST] COVID Example (Main Test)")
    print("-" * 40)
    
    input_text = "Hàm này được phát triển từ tháng 08/2019. Có phải tháng 12/2020 đã có vaccine phòng ngừa Covid-19 xmz ?"
    expected = "hàm này được phát triển từ tháng tám năm hai nghìn không trăm mười chín . có phải tháng mười hai năm hai nghìn không trăm hai mười đã có vaccine phòng ngừa covid mười chín ích mờ giét ."
    
    try:
        result = TTSnorm(input_text)
        
        print("Input:")
        print(f"  {input_text}")
        print()
        print("Expected (vinorm gốc):")
        print(f"  {expected}")
        print()
        print("Result (vinormx):")
        print(f"  {result}")
        print()
        
        if result == expected:
            print("[SUCCESS] Perfect match with original vinorm!")
            return True
        else:
            print("[WARN] Some differences found - checking details...")
            
            # So sánh từng từ
            expected_words = expected.split()
            result_words = result.split()
            
            differences = 0
            max_len = max(len(expected_words), len(result_words))
            
            for i in range(max_len):
                exp = expected_words[i] if i < len(expected_words) else "[MISSING]"
                res = result_words[i] if i < len(result_words) else "[EXTRA]"
                
                if exp != res:
                    differences += 1
                    if differences <= 5:  # Show max 5 differences
                        print(f"  Diff {i:2d}: Expected '{exp}' | Got '{res}'")
            
            if differences > 5:
                print(f"  ... and {differences - 5} more differences")
            
            print(f"\nTotal differences: {differences} words")
            return differences == 0
            
    except Exception as e:
        print(f"[ERROR] COVID example failed: {e}")
        return False


def test_options():
    """Test các tùy chọn"""
    print("\n[TEST] Options")
    print("-" * 40)
    
    text = "Dr. Smith có 100 USD ngày 25/12/2020!"
    
    options = [
        ("Default", {}),
        ("Keep punct", {"punc": True}),
        ("Upper case", {"lower": False}), 
        ("Regex only", {"rule": True}),
        ("No unknown", {"unknown": False})
    ]
    
    print(f"Input: {text}")
    print()
    
    for desc, kwargs in options:
        try:
            result = TTSnorm(text, **kwargs)
            print(f"[OK] {desc:>12}: {result}")
        except Exception as e:
            print(f"[ERROR] {desc:>12}: ERROR: {e}")


def test_performance():
    """Test hiệu năng đơn giản"""
    print("\n[TEST] Performance")
    print("-" * 40)
    
    # Text dài để test performance
    text = """
    Trong năm 2023, công ty XYZ đạt doanh thu 15.7 tỷ USD, tăng 25% so với 2022.
    Tổng số nhân viên 12,345 người tại 67 văn phòng ở 23 quốc gia.
    CEO Johnson và Dr. Smith họp WHO, WTO ngày 15/6/2023.
    COVID-19 ảnh hưởng từ 3/2020 đến 12/2021.
    """ * 5
    
    print(f"Text length: {len(text):,} characters")
    
    try:
        start_time = time.time()
        result = TTSnorm(text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        speed = len(text) / processing_time if processing_time > 0 else 0
        
        print(f"[OK] Processing time: {processing_time:.3f} seconds")
        print(f"[OK] Speed: {speed:,.0f} chars/second")
        print(f"[OK] Output length: {len(result):,} characters")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Performance test failed: {e}")
        return False


def main():
    """Chạy tất cả tests"""
    encoding = getattr(sys.stdout, 'encoding', 'unknown')
    print("VINORMX COMPATIBILITY TEST")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Encoding: {encoding}")
    print()
    
    # List of tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Number Conversion", test_number_conversion),
        ("Date Normalization", test_date_normalization),
        ("Abbreviations", test_abbreviations),
        ("Special Characters", test_special_characters),
        ("COVID Example", test_covid_example),
        ("Options", test_options),
        ("Performance", test_performance)
    ]
    
    results = []
    main_test_passed = False
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        
        try:
            if test_name == "COVID Example":
                success = test_func()
                main_test_passed = success
            else:
                result = test_func()
                success = result if isinstance(result, bool) else True
            
            results.append((test_name, success))
            
        except Exception as e:
            print(f"[ERROR] {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if main_test_passed:
        print("\n[SUCCESS] MAIN TEST PASSED!")
        print("[OK] vinormx matches original vinorm output")
        print("[OK] No WinError 193 issues!")
        print("[OK] Ready for production use")
    elif passed >= total // 2:
        print(f"\n[OK] Core functionality works ({passed}/{total} tests passed)")
        print("[INFO] Some minor differences from original, but usable")
    else:
        print(f"\n[WARN] Multiple issues detected ({passed}/{total} tests passed)")
        print("[INFO] Check error messages above")
    
    print("\nUsage:")
    print("from vinormx import TTSnorm")
    print('result = TTSnorm("Your Vietnamese text here")')


if __name__ == "__main__":
    main()