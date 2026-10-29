# Kiểm tra và bổ sung tài liệu học tập — 12/10/2026

Phạm vi: database local đang cấu hình cho backend, 7 khóa, 65 bài. Kiểm tra đường dẫn thật, mở PDF và trích xuất văn bản; không xem đường dẫn mẫu trong database là tài liệu đã có. Kiểm tra này xác nhận khả năng đọc/tải và phạm vi nội dung, không phải chứng nhận học thuật độc lập cho toàn bộ bài giảng.

| Khóa hiện có | Số bài | PDF đọc được trước | Bổ sung tài liệu chính | PDF đọc được sau |
|---|---:|---:|---:|---:|
| Python Cơ Bản Cho Người Mới Bắt Đầu | 9 | 0 | 9 | 9 |
| JavaScript Từ Zero Đến Hero | 9 | 0 | 9 | 9 |
| Lập Trình Java Căn Bản | 9 | 9 | 0 | 9 |
| HTML & CSS Nhập Môn | 9 | 9 | 0 | 9 |
| ReactJS Chuyên Sâu | 9 | 9 | 0 | 9 |
| MySQL & Thiết Kế Cơ Sở Dữ Liệu | 9 | 9 | 0 | 9 |
| Nguyên Lí HDH | 11 | 11 | 0 | 11 |
| **Tổng** | **65** | **47** | **18** | **65** |

## Nội dung đã bổ sung

- Viết mới bài “Cài đặt Python & IDE”: trình thông dịch, môi trường ảo, chạy chương trình, đọc traceback, lỗi logic và bài tập kèm hướng dẫn.
- Dựng PDF cho 18 bài Python/JavaScript đang dùng đường dẫn mẫu; các bài còn lại trong nhóm này có nguồn Markdown phù hợp sẵn nên sử dụng nguồn đó.
- Viết 7 sổ tay học thêm riêng theo khóa, mỗi sổ tay 3 trang, tổng 21 trang. Có giải thích, ví dụ, lỗi thường gặp, bài tập ba mức, lời giải định hướng, tiêu chí đánh giá và nguồn học tiếp.
- Ghép học thêm vào sau tài liệu chính của bài cuối mỗi khóa: bài 9, 18, 27, 36, 45, 54, 65. File gốc của các bài đã có tài liệu được giữ lại.
- Lập chỉ mục 23 tài liệu bài được bổ sung/cập nhật và 7 tài liệu học thêm theo khóa, tổng 30 bản ghi có chunk RAG.

Chi tiết nội dung và các PDF riêng tại [mục lục học thêm](../backend/training/lesson_docs/supplements/README.md). Bộ mở rộng này tập trung vào vận dụng kiến thức của các chương đang có, không tuyên bố đã bao phủ toàn bộ chuyên ngành hoặc mọi nội dung nâng cao ngoài đề cương.

## Kết quả kiểm tra

- 65/65 PDF tồn tại, mở được và có văn bản trích xuất được.
- 65/65 đường tải có chữ ký qua `/api/lessons/media` trả HTTP 200 và nội dung PDF. Kiểm tra bằng TestClient với tài khoản admin đang hoạt động, không qua trình duyệt.
- 30/30 tài liệu bổ sung/cập nhật có trạng thái `indexed` và số chunk lớn hơn 0.
- Các ví dụ Python trong sổ tay học thêm chạy thành công, bao gồm các assert cho phân loại, đối số mặc định và lớp sinh viên.
- Không gọi LLM để đo chất lượng trả lời hoặc chất lượng quiz sau khi thêm tài liệu.

Nhật ký trước/sau: [changes.json](../backend/training/lesson_docs/completed/changes.json).
Kiểm tra ban đầu: [audit_before.json](../backend/training/lesson_docs/completed/audit_before.json).
Kết quả xác minh: [verification.json](../backend/training/lesson_docs/completed/verification.json).

## Lưu ý về dữ liệu demo và khả năng tái tạo

Database này có khóa 7 là Nguyên Lí HDH. Nguồn demo Tiếng Anh/Toán trong repo không phản ánh khóa đang có; không gắn PDF bài 55 trở đi từ bộ demo đó bằng ID. Script mới dùng tên khóa để chọn sổ tay và kiểm tra ID/tiêu đề khi chọn nguồn tài liệu chính.

Kết quả bổ sung đã được áp dụng cho database local. Docker dùng database/volume riêng, cần kiểm tra và chạy script trong môi trường tương ứng nếu muốn bổ sung tại đó. Sửa nội dung Markdown không tự cập nhật các file đang được học viên tải.
