# Kiểm tra và tạo lại PDF theo mẫu Nguyên lí HĐH — 13/10/2026

Phạm vi là 7 khóa, 65 bài trong database local hiện tại. Đã đọc 290 file PDF trong thư mục uploads và training/lesson_docs (không tính bộ mới), kiểm tra số trang, lớp văn bản và lưu SHA-256. Tất cả mở được và trích xuất được văn bản. Đây là kiểm tra kỹ thuật và cấu trúc; chưa thẩm định học thuật từng khẳng định trong toàn bộ tài liệu.

## Cấu trúc áp dụng

Mẫu đối chiếu là các bài PDF thật của khóa Nguyên Lí HDH, gồm đầu trang tên môn/chương/bài, tiêu đề đánh số, ghi chú nguồn, mục tiêu bài học, nội dung chia mục, câu hỏi ôn tập và chân trang đánh số trang.

- 54 bài Python, JavaScript, Java, HTML/CSS, React và MySQL được dựng lại từ nguồn Markdown phù hợp với tiêu đề bài trong database. Giữ ví dụ mã, tóm tắt, bài tập và sổ tay học thêm ở bài cuối mỗi khóa.
- Bài 46 “Khái niệm cơ sở dữ liệu” không có nguồn Markdown cũ. Đã chuyển phần nội dung từ PDF thật sang nguồn Markdown riêng và bổ sung mục tiêu, câu hỏi ôn tập.
- 11 bài HĐH được đưa vào bộ mới bằng cách giữ nguyên PDF hiện tại để bảo toàn hình, công thức, thông tin tác giả và định dạng mẫu. Bài cuối vẫn chứa phần học thêm đã có.
- Tài liệu các môn khác ghi nguồn StudyOnline; không gán thông tin tác giả/khoa của bài giảng HĐH cho các môn này.

## Tệp và tái tạo

Kết quả bộ mới: 65 PDF, tổng 183 trang. Đã áp dụng 54 bài được định dạng lại vào database local và lập lại chỉ mục tài liệu chính tương ứng. Kiểm tra sau áp dụng xác nhận 65/65 file đúng hash, có mục tiêu/câu hỏi ôn tập, tải qua endpoint có chữ ký trả HTTP 200 và có tài liệu RAG `indexed` với số chunk lớn hơn 0. Kiểm tra HTTP dùng TestClient và tài khoản admin hiện có; chưa kiểm tra trực quan từng trang trong trình duyệt.

- [Script tạo lại](../backend/training/lesson_docs/rebuild_os_structure.py)
- [File ZIP gồm 65 PDF và mục lục](../backend/training/lesson_docs/rebuilt/tai_lieu_theo_mau_hdh.zip)
- [Kiểm tra toàn bộ PDF](../backend/training/lesson_docs/rebuilt/all_pdfs_audit.json)
- [Đối chiếu bộ mới](../backend/training/lesson_docs/rebuilt/verification.json)
- [Bộ PDF mới](../backend/training/lesson_docs/rebuilt/)
- [Nhật ký đường dẫn trước/sau khi áp dụng](../backend/training/lesson_docs/rebuilt/applied.json)
- [Kết quả xác minh sau áp dụng](../backend/training/lesson_docs/rebuilt/applied_verification.json)

Chạy tại backend:

```powershell
.venv/Scripts/python.exe training/lesson_docs/rebuild_os_structure.py
.venv/Scripts/python.exe training/lesson_docs/rebuild_os_structure.py --apply
.venv/Scripts/python.exe training/lesson_docs/verify_rebuilt.py
```

Lệnh đầu kiểm tra và tạo file riêng. Lệnh sau kiểm tra tiêu đề và hash, cập nhật đường dẫn tài liệu bài học cùng các bản ghi tài liệu RAG tương ứng trong database local, lập lại chỉ mục. Các PDF gốc được giữ nguyên, đường dẫn cũ lưu trong nhật ký. Database Docker là môi trường riêng.
