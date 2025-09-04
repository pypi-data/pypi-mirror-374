# Vinorm compatible for Windows 64-bit

Vietnamese Text Normalization System - Pure Python Implementation

## Giới thiệu

Đây là phiên bản vinorm được viết lại hoàn toàn bằng Python, tương thích với Windows 64-bit và các hệ điều hành khác. Phiên bản này giải quyết lỗi **WinError 193** mà nhiều người gặp phải khi sử dụng vinorm gốc trên Windows.

### Tại sao cần phiên bản này?

Vinorm gốc sử dụng một file thực thi C++ được compile cho Linux, không thể chạy trên Windows. Phiên bản này:

- ✅ **100% Pure Python** - không cần file thực thi C++
- ✅ **Cross-platform** - chạy trên Windows, macOS, Linux
- ✅ **Không dependencies** - chỉ sử dụng thư viện chuẩn Python
- ✅ **API tương thích** - drop-in replacement cho vinorm gốc
- ✅ **Performance tốt** - tối ưu hóa cho tốc độ xử lý

## Cài đặt

### Cách 1: Cài đặt trực tiếp từ file

```bash
pip install vinormx
```

### Cách 2: Cài đặt từ source code

1. Download file `vinormx.py`
2. Đặt vào thư mục project của bạn
3. Import và sử dụng:

```python
from vinormx import TTSnorm

text = "Hàm này được phát triển từ 8/2019. Có phải tháng 12/2020 đã có vaccine phòng ngừa Covid-19 xmz ?"
normalized = TTSnorm(text)
print(normalized)
```

## Sử dụng

### Cách sử dụng cơ bản

```python
from vinormx import TTSnorm

# Chuẩn hóa văn bản cơ bản
text = "Tôi có 100 USD và 2.5 triệu VND ngày 25/12/2023"
result = TTSnorm(text)
print(result)
# Output: tôi có một trăm usd và hai phẩy năm triệu vnd ngày hai mười lăm tháng mười hai năm hai nghìn không trăm hai mười ba .
```

### Các tùy chọn nâng cao

```python
# Giữ nguyên dấu câu
TTSnorm(text, punc=True)

# Giữ nguyên chữ hoa
TTSnorm(text, lower=False)

# Xử lý từ không xác định (spell out)
TTSnorm(text, unknown=False)

# Chỉ sử dụng regex (không dùng từ điển)
TTSnorm(text, rule=True)
```

### Ví dụ chi tiết

```python
from vinormx import TTSnorm

test_cases = [
    "Dr. Smith vs Mr. Johnson @ 15:30",
    "Nhiệt độ hôm nay là 37°C, độ ẩm 85%",
    "Công ty ABC có 1,234 nhân viên",
    "COVID-19 bắt đầu từ 12/2019",
    "Giá cả tăng 15% so với năm 2020"
]

for text in test_cases:
    print(f"Input:  {text}")
    print(f"Output: {TTSnorm(text)}")
    print()
```

## Tính năng

### ✅ Chuẩn hóa số

- Số nguyên: `123` → `một trăm hai mười ba`
- Số thập phân: `12.5` → `mười hai phẩy năm`
- Năm: `2023` → `hai nghìn không trăm hai mười ba`

### ✅ Chuẩn hóa ngày tháng

- `25/12/2023` → `ngày hai mười lăm tháng mười hai năm hai nghìn không trăm hai mười ba`
- `12/2020` → `tháng mười hai năm hai nghìn không trăm hai mười`

### ✅ Chuẩn hóa từ viết tắt

- `Dr.` → `bác sĩ`
- `COVID-19` → `covid mười chín`
- `USA` → `hoa kỳ`
- `WHO` → `tổ chức y tế thế giới`

### ✅ Chuẩn hóa ký tự đặc biệt

- `&` → `và`
- `%` → `phần trăm`
- `@` → `a còng`
- `°C` → `độ c`
- `$` → `đô la`

### ✅ Xử lý từ không xác định

- `xmz` → `ích em giét` (spell out từng ký tự)

## So sánh với vinorm gốc

| Tính năng             | Vinorm gốc        | Vinorm X            |
| --------------------- | ----------------- | ------------------- |
| Hỗ trợ Windows 64-bit | ❌ (WinError 193) | ✅                  |
| Dependencies          | C++ executable    | Pure Python         |
| Cross-platform        | ❌                | ✅                  |
| Performance           | Rất nhanh         | Nhanh               |
| API compatibility     | -                 | ✅ 100% tương thích |

## API Reference

### `TTSnorm(text, punc=False, unknown=True, lower=True, rule=False)`

**Parameters:**

- `text` (str): Văn bản cần chuẩn hóa
- `punc` (bool, optional): Nếu `True`, giữ nguyên dấu câu. Default: `False`
- `unknown` (bool, optional): Nếu `True`, giữ nguyên từ không xác định. Default: `True`
- `lower` (bool, optional): Nếu `True`, chuyển về chữ thường. Default: `True`
- `rule` (bool, optional): Nếu `True`, chỉ sử dụng regex. Default: `False`

**Returns:**

- `str`: Văn bản đã được chuẩn hóa

## Troubleshooting

### Lỗi WinError 193 với vinorm gốc

Nếu bạn gặp lỗi này:

```
OSError: [WinError 193] %1 is not a valid Win32 application
```

**Giải pháp:** Sử dụng vinormx này thay thế!

### Migration từ vinorm gốc

```python
# Cũ
from vinorm import TTSnorm

# Mới - chỉ cần thay đổi import
from vinormx import TTSnorm

# API hoàn toàn giống nhau!
```

## Performance

Benchmarks trên Windows 10 64-bit:

| Text length  | Vinorm X |
| ------------ | -------- |
| 100 chars    | ~0.01s   |
| 1,000 chars  | ~0.05s   |
| 10,000 chars | ~0.3s    |

## Requirements

- Python 3.6+
- Windows, macOS, hoặc Linux
- Không cần dependencies ngoài

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - Dựa trên vinorm gốc của [v-nhandt21](https://github.com/v-nhandt21/Vinorm) và [NoahDrisort](https://github.com/NoahDrisort/vinorm_cpp_version).

## Credits

- **Original Vinorm**: [v-nhandt21/Vinorm](https://github.com/v-nhandt21/Vinorm)
- **Original C++ Version**: [NoahDrisort/vinorm_cpp_version](https://github.com/NoahDrisort/vinorm_cpp_version)
- **Authors**: Lê Tấn Đăng Tâm, Đỗ Trí Nhân (AILab, HCMUS)
- **Supervisor**: Prof. Vũ Hải Quân

---

**🎯 Giải pháp hoàn hảo cho lỗi WinError 193 trên Windows!**
