=== LESSON 1 ===
## Mục tiêu bài học
- Kiểm tra được trình thông dịch Python đang sử dụng
- Tạo môi trường ảo và chạy chương trình từ terminal
- Phân biệt lỗi cú pháp, lỗi lúc chạy và lỗi logic

## 1. Python và môi trường làm việc
Mã nguồn Python là văn bản trong file .py. Trình thông dịch đọc và thực thi mã; IDE hỗ trợ soạn thảo, tìm lỗi và gỡ lỗi nhưng không thay thế trình thông dịch. Ví dụ của khóa dùng Python 3. Trên Windows có thể dùng trình khởi chạy py nếu lệnh python chưa được cấu hình.

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe --version
```

Môi trường ảo tách thư viện của một dự án khỏi dự án khác. Không cần kích hoạt môi trường nếu gọi trực tiếp python.exe bên trong .venv. Trong VS Code, chọn trình thông dịch của môi trường này để terminal và trình gỡ lỗi sử dụng cùng Python.

## 2. Chương trình đầu tiên
Tạo file hello.py trong thư mục dự án. Lưu file trước khi chạy; kiểm tra thư mục hiện tại nếu terminal báo không tìm thấy file.

```python
name = "An"
print(f"Xin chào {name}")
print(2 + 3)
```

```powershell
.\.venv\Scripts\python.exe hello.py
```

Kết quả là hai dòng: Xin chào An và 5. Nếu chương trình chạy trong IDE nhưng không chạy trong terminal, kiểm tra trình thông dịch và thư mục làm việc thay vì cài lại mọi thứ.

## 3. Đọc lỗi và gỡ lỗi
SyntaxError báo mã không đúng cú pháp, chẳng hạn thiếu dấu đóng ngoặc. NameError xuất hiện khi dùng tên chưa được định nghĩa. ValueError có thể xảy ra khi chuyển chuỗi không hợp lệ thành số. Lỗi logic là chương trình chạy nhưng kết quả không đúng yêu cầu.

Đọc traceback từ dòng cuối để biết loại lỗi, sau đó tìm tên file và số dòng thuộc mã của mình. Đặt breakpoint trước dòng sai, xem giá trị và kiểu của biến, chạy từng bước rồi so sánh với kết quả dự kiến. Không sửa nhiều chỗ cùng lúc vì khó biết thay đổi nào giải quyết lỗi.

## Bài tập vận dụng
1. In tên, tuổi và tổng 12 + 8 từ một file Python.
2. Tạo lỗi bằng cách viết print(unknown_name), đọc traceback rồi sửa.
3. Viết phép tính diện tích hình chữ nhật; thử chiều dài 5, chiều rộng 3.

## Đáp án và tiêu chí tự kiểm tra
1. Mã nằm trong file, chạy từ terminal thành công và phép cộng trả 20.
2. Lỗi NameError: khai báo unknown_name hoặc sửa thành tên biến đã tồn tại.
3. Diện tích là 15; dùng phép nhân, không dùng phép cộng. Giải thích được vì sao chương trình trả 8 vẫn chạy nhưng sai logic.

## Tóm tắt
- IDE và trình thông dịch có vai trò khác nhau.
- Môi trường ảo giúp tách thư viện; dùng cùng trình thông dịch khi chạy và gỡ lỗi.
- Kiểm tra kết quả dự kiến và đọc traceback trước khi sửa mã.

## Nguồn học tiếp
https://docs.python.org/3/tutorial/venv.html
