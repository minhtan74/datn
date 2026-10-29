# Rà soát file dư — 13/10/2026

Chỉ kiểm tra, không xóa hoặc di chuyển file. Phạm vi: cây thư mục dự án trừ `.git`, đồ thị import mã nguồn frontend/backend, tham chiếu file trong các cột văn bản của database local, hai nhật ký cập nhật PDF và ba bản sao lưu SQL. Dùng SHA-256 để nhận diện PDF giống hệt nhau.

## Kết luận

- Không phát hiện file trong `frontend/src` nằm ngoài đồ thị import bắt đầu từ `main.jsx`; không phát hiện relative import bị thiếu file.
- Không phát hiện module Python nghiệp vụ trong `backend/app` nằm ngoài đồ thị import từ `main.py` (bỏ qua file `__init__.py`). Kiểm tra import không chứng minh mọi hàm hoặc quy tắc CSS đều được sử dụng.
- Có 4 PDF upload không tìm thấy tham chiếu trong database local, nhật ký khôi phục hoặc backup SQL. Cả 4 đều có bản sao giống hệt được giữ ở vị trí khác. Đây là nhóm file dư rõ nhất.
- Có các bản build/cache và bản đóng gói có thể tái tạo. Không coi môi trường thư viện, nguồn huấn luyện hoặc dữ liệu MySQL là file rác.

## Bốn PDF dư có thể dọn

| File trong `backend/uploads/documents` | Nội dung | Bản giống hệt cần giữ |
|---|---|---|
| `1789547183_8115d8761c91.pdf` | Python là gì? Cài đặt môi trường lập trình | `1789547498_c276bec77285.pdf` |
| `1789547292_2e7cdf1e69a3.pdf` | Cùng bài Python ở trên | `1789547498_c276bec77285.pdf` |
| `1789547296_301cd1842885.pdf` | Cùng bài Python ở trên | `1789547498_c276bec77285.pdf` |
| `1789547466_f1df8a42cc08.pdf` | Khái niệm cơ sở dữ liệu, bản một trang | `1789530044_3fc86e099f4c.pdf` |

Tổng dung lượng khoảng **0,28 MiB**. Hai bản được giữ có tham chiếu trong dữ liệu khôi phục. Kết luận áp dụng cho database local được kiểm tra; chưa kiểm tra database Docker hoặc môi trường khác.

## Có thể tái tạo, dọn khi cần

| Nhóm | Dung lượng | Điều kiện |
|---|---:|---|
| `frontend/dist/` | 2,11 MiB | Có thể tạo lại bằng `npm run build`; cần giữ khi đang dùng `vite preview` hoặc phục vụ trực tiếp thư mục này |
| Các thư mục `__pycache__/`, file `.pyc` | 0,84 MiB | Python tự tạo lại |
| `backend/.pytest_cache/` | Chưa đo được | Cache pytest; môi trường hiện tại bị từ chối quyền đọc |
| `backend/training/lesson_docs/rebuilt/tai_lieu_theo_mau_hdh.zip` | 13,29 MiB | Bản đóng gói để tải về; chứa bản sao 65 PDF đã có riêng. Có thể bỏ khi không còn cần chia sẻ ZIP |

`rebuilt/` tổng 29,63 MiB: chứa bộ xuất mới, ZIP và nhật ký xác minh. PDF website đang dùng được lưu riêng trong `uploads/documents`. Các PDF xuất có thể dựng lại, nhưng vẫn hữu ích để đối chiếu và dùng `--apply`; không nên xóa cả thư mục cùng các nhật ký.

## Cần giữ

- `backend/data/mysql-data/` (233,60 MiB): dữ liệu MySQL, được `start-dev.ps1` sử dụng.
- `backend/data/backups/` (30,21 MiB): ba bản sao lưu SQL để khôi phục.
- 72 file upload đang được database local tham chiếu.
- 59 file upload chỉ được hai nhật ký khôi phục PDF tham chiếu và 107 file khác được các backup SQL tham chiếu. Dù không phục vụ bài học hiện tại, chúng có thể cần khi khôi phục dữ liệu cũ.
- `backend/.venv/` (243,80 MiB), `frontend/node_modules/` (75,70 MiB): thư viện để chạy ứng dụng. Có thể cài lại, nhưng xóa sẽ yêu cầu thiết lập lại trước khi chạy.
- `backend/training/lesson_docs/pdf/` (5,35 MiB): bộ PDF demo được `seed_lesson_docs.py` sử dụng và README hướng dẫn. Không thừa chỉ vì website hiện dùng bộ mới.
- `backend/training/lesson_docs/completed/`: tài liệu bổ sung và nhật ký trước/sau; script tạo lại vẫn dùng một số file trong nhóm này.
- `course7_english.md`, `course8_discrete_math.md`, `seed_extra_courses.py`: dữ liệu demo Tiếng Anh/Toán được tài liệu hướng dẫn sử dụng, dù database local hiện có môn HĐH.
- Migration Alembic, các file SQL, tests, Postman, nguồn Markdown, dữ liệu huấn luyện và kết quả đánh giá: phục vụ khởi tạo, kiểm thử, tái tạo hoặc đối chiếu. `migration_add_payments.sql` được Docker Compose dùng trực tiếp.
- `.env`, `.env.example`, `.gitkeep`, file cấu hình Git/Docker: có mục đích rõ ràng, không phải file dư.

## Bản sao PDF và giới hạn

Đếm được **415 PDF**, **237 nội dung khác nhau theo SHA-256**, **167 nhóm có bản giống hệt nhau**. Bản xuất trong training, bản website trong uploads và bản gốc để khôi phục có vai trò khác nhau; không thể xóa mọi file trùng hash.

Không đọc được `backend/.pytest_cache/` do quyền truy cập. Với `.venv` và `node_modules`, chỉ thống kê file/dung lượng, không thẩm định từng file thư viện bên thứ ba. Không phân tích nội dung các file dữ liệu MySQL như mã nguồn; xác định vai trò qua cấu hình khởi động. Không chạy toàn bộ chức năng website để chứng minh mọi hàm được gọi.

Danh sách máy đọc được: [file-audit-details.json](file-audit-details.json). Không chứa giá trị cấu hình bí mật hoặc nội dung bản ghi database.
