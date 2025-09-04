# 🚀 Cài đặt nhanh Vinorm cho Windows 64-bit

**Giải quyết lỗi WinError 193 trong 3 bước!**

## 📥 Bước 1: Download files

Download các files sau và đặt vào thư mục project của bạn:

- `vinorm_windows.py` (file chính)
- `test_vinorm_windows.py` (optional - để test)

## 🧪 Bước 2: Test thử

Mở Command Prompt/PowerShell và chạy:

```bash
python test_vinorm_windows.py
```

Nếu thấy output như này nghĩa là hoạt động tốt:

```
🧪 VINORM WINDOWS COMPATIBILITY TEST
============================================================

Environment Info:
Python version: 3.x.x
Platform: win32
OS: nt

🔄 Running Basic Tests...
```

## ✅ Bước 3: Sử dụng

**Thay thế import cũ:**

```python
# Cũ (gây lỗi WinError 193)
from vinorm import TTSnorm

# Mới (hoạt động trên Windows)
from vinorm_windows import TTSnorm
```

**Test ngay:**

```python
from vinorm_windows import TTSnorm

text = "Có phải tháng 12/2020 đã có vaccine phòng ngừa Covid-19?"
result = TTSnorm(text)
print(result)
# Output: có phải tháng mười hai năm hai nghìn không trăm hai mười đã có vaccine phòng ngừa covid mười chín .
```

## 🎯 Nếu gặp vấn đề

### ImportError

```bash
# Đảm bảo file vinorm_windows.py ở đúng thư mục
ls vinorm_windows.py
# hoặc trên Windows:
dir vinorm_windows.py
```

### Python version

```bash
# Cần Python 3.6+
python --version
```

### Test lỗi

```bash
# Chạy test chi tiết
python -c "from vinorm_windows import TTSnorm; print('✅ Works!'); print(TTSnorm('test 123'))"
```

## 📚 API tương thích 100%

Tất cả functions và parameters giống hệt vinorm gốc:

```python
TTSnorm(text, punc=False, unknown=True, lower=True, rule=False)
```

**Ví dụ:**

```python
from vinorm_windows import TTSnorm

# Các tùy chọn giống hệt vinorm gốc
text = "Dr. Smith có $100 ngày 25/12/2023"

print(TTSnorm(text))                    # Default
print(TTSnorm(text, punc=True))         # Giữ dấu câu
print(TTSnorm(text, lower=False))       # Giữ chữ hoa
print(TTSnorm(text, unknown=False))     # Xử lý từ lạ
print(TTSnorm(text, rule=True))         # Chỉ dùng regex
```

---

**🎉 Xong! Không còn WinError 193 nữa!**

_Nếu cần hỗ trợ thêm, check file README.md để biết chi tiết._
