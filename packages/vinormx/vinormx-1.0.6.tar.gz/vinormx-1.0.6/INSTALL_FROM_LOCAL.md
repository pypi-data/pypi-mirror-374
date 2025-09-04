# 📦 Cài đặt Vinorm từ thư mục local

## 🗂️ Chuẩn bị cấu trúc thư mục

Tạo thư mục project với cấu trúc sau:

```
vinorm-windows/
│
├── vinorm_windows.py       # File chính
├── setup.py               # Script cài đặt
├── README.md             # Documentation
├── MANIFEST.in           # Danh sách files cần include
└── requirements.txt      # Dependencies (nếu có)
```

## 📁 Cách 1: Cài đặt trực tiếp từ thư mục

### Bước 1: Di chuyển vào thư mục chứa setup.py

```bash
cd /path/to/vinorm-windows
# Hoặc trên Windows:
cd C:\path\to\vinorm-windows
```

### Bước 2: Cài đặt bằng pip

```bash
# Cài đặt bình thường
pip install .

# Hoặc cài đặt ở chế độ development (editable mode)
pip install -e .

# Hoặc với verbose để xem chi tiết
pip install -v .
```

## 📁 Cách 2: Cài đặt từ thư mục khác

Nếu bạn đang ở thư mục khác:

```bash
# Cài đặt từ path tuyệt đối
pip install /path/to/vinorm-windows

# Trên Windows:
pip install C:\path\to\vinorm-windows

# Cài đặt từ path tương đối
pip install ../vinorm-windows
pip install ./vinorm-windows
```

## 📁 Cách 3: Build wheel rồi cài đặt

### Bước 1: Build wheel

```bash
cd vinorm-windows
python setup.py sdist bdist_wheel
```

### Bước 2: Cài đặt từ wheel

```bash
pip install dist/vinorm_windows-3.0.0-py3-none-any.whl
```

## 📁 Cách 4: Cài đặt với requirements

Nếu có file `requirements.txt`:

```bash
# Cài dependencies trước
pip install -r requirements.txt

# Rồi cài package
pip install .
```

## 🛠️ Tạo files cần thiết

### MANIFEST.in

Tạo file `MANIFEST.in` để include các files cần thiết:

```
include README.md
include LICENSE
include requirements.txt
recursive-include vinorm_windows *.py
```

### requirements.txt

Tạo file `requirements.txt` (trong trường hợp này là empty vì không có dependencies):

```
# Không có dependencies bên ngoài
# Chỉ sử dụng Python standard library
```

## 🧪 Kiểm tra sau khi cài đặt

### Bước 1: Kiểm tra package đã cài

```bash
pip list | grep vinorm
# hoặc
pip show vinorm-windows
```

### Bước 2: Test import

```python
# Test trong Python
python -c "from vinorm_windows import TTSnorm; print('✅ Installed successfully!')"
```

### Bước 3: Test chức năng

```python
python -c "from vinorm_windows import TTSnorm; print(TTSnorm('test 123'))"
```

## 🔄 Development Mode (Editable Install)

Nếu bạn muốn chỉnh sửa code và thấy thay đổi ngay lập tức:

```bash
pip install -e .
```

Với editable mode:

- ✅ Thay đổi code trong thư mục → áp dụng ngay lập tức
- ✅ Không cần cài lại sau mỗi lần sửa
- ✅ Thuận tiện cho development

## 🗑️ Gỡ cài đặt

```bash
pip uninstall vinorm-windows
```

## ⚠️ Troubleshooting

### Lỗi: "No module named setuptools"

```bash
pip install setuptools wheel
```

### Lỗi: Permission denied

```bash
# Cài cho user hiện tại
pip install --user .

# Hoặc dùng sudo (Linux/Mac)
sudo pip install .
```

### Lỗi: "Microsoft Visual C++ 14.0 is required"

Đây không phải vấn đề với vinorm-windows vì nó là pure Python. Nhưng nếu gặp:

```bash
pip install --upgrade pip setuptools wheel
```

### Lỗi: File path quá dài (Windows)

```bash
# Sử dụng path ngắn hơn
subst V: C:\very\long\path\to\vinorm-windows
cd V:
pip install .
```

## 🎯 Ví dụ hoàn chỉnh

```bash
# 1. Tải files về thư mục
mkdir vinorm-windows
cd vinorm-windows

# 2. Đặt các files: vinorm_windows.py, setup.py, README.md

# 3. Cài đặt
pip install .

# 4. Test
python -c "from vinorm_windows import TTSnorm; print(TTSnorm('Xin chào 123'))"
```

## 📋 Checklist cài đặt thành công

- [ ] Thư mục có đủ files: `vinorm_windows.py`, `setup.py`
- [ ] Chạy `pip install .` không có lỗi
- [ ] `pip list` hiển thị package
- [ ] Import thành công: `from vinorm_windows import TTSnorm`
- [ ] Test function: `TTSnorm("test")` trả về kết quả
- [ ] Không có lỗi WinError 193

---

**🎉 Sau khi cài đặt thành công, bạn có thể import và sử dụng ở bất kỳ đâu trong hệ thống!**
