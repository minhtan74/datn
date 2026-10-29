# Tài liệu bổ sung ngày 29/10/2026

10 nguồn Markdown khớp 101 tiêu đề bài trong 10 khóa nội dung. Mỗi mục bổ sung tình huống thực tế, giải thích, ví dụ hoặc mô hình thực hành, câu tự luyện và hướng giải. PDF bài học gồm bản gốc rồi tới phụ lục mới; file gốc được giữ.

| Nguồn | Phạm vi |
|---|---|
| [Python](python.md) | 9 bài; cài đặt, kiểu, lỗi code, vòng lặp, hàm, OOP, dự án |
| [JavaScript](javascript.md) | 9 bài; DOM, sự kiện, biến, async, fetch và dự án |
| [Java](java.md) | 9 bài; JDK, OOP, collection, exception và dự án |
| [HTML/CSS](html_css.md) | 9 bài; semantic, form, layout, responsive và khả dụng |
| [React](react.md) | 9 bài; props/state, Hook, API, router và dự án |
| [MySQL](mysql.md) | 9 bài; khóa, JOIN, nhóm, view, chuẩn hóa và ERD |
| [Hệ điều hành](os.md) | 11 bài; tiến trình, thread, điều phối, IPC và đồng bộ |
| [Mạng](network.md) | 12 bài; địa chỉ, DNS, TCP/IP, phân vùng và chẩn đoán |
| [Giải thuật](algorithms.md) | 12 bài; cấu trúc dữ liệu, bất biến, duyệt và tìm kiếm |
| [Kiểm thử](testing.md) | 12 bài; thiết kế ca, trạng thái, quyền, dữ liệu và báo cáo |

## Sản phẩm và nhật ký

- `generated/course_<id>_complete.pdf`: bản toàn khóa có mục lục và bookmark bài.
- `generated/lesson_<id>_<hash>.pdf`: PDF bài học đã ghép phụ lục.
- `generated/manifest.json`: URL/file trước–sau, hash, id tài liệu mới và dữ liệu bảo vệ.
- `generated/verification.json`: 101 lượt tải có xác thực, hash và trang RAG.
- `generated/retrieval-validation.json`: 11 câu tra cứu theo đúng khóa/bài.
- `generated/code-validation.json`, `generated/sql-validation.json`: kiểm tra ví dụ.

Các tài liệu AI mới dùng số trang vật lý của PDF đã ghép. Với 65 bài đã có tài liệu chính được index, chỉ index phần bổ sung để tránh nhân đôi toàn bộ kiến thức cũ. Với 36 bài chưa có index theo bài, index toàn bộ PDF. Các tài liệu và chunk cũ không bị ghi đè.

## Quy trình

Từ thư mục `backend`, tạo một edition mới hoặc dùng manifest đã chuẩn bị:

```powershell
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py prepare
node training/lesson_docs/edition_20261029/render.cjs
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py assemble
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py index
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/check_examples.py
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py apply
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py verify
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/check_retrieval.py
```

`prepare` dừng nếu manifest đã tồn tại để không ghi đè snapshot gốc. `apply` chạy một transaction, kiểm tra URL chưa đổi và hash dữ liệu học tập trước khi áp dụng. `verify` có thể chạy lại sau áp dụng. `render.cjs` dùng Playwright và Chromium đã cài trên máy; máy khác đặt `PLAYWRIGHT_MODULE` và `CHROMIUM_PATH`.

Hoàn tác riêng edition, với điều kiện URL bài học chưa bị sửa tiếp:

```powershell
.venv/Scripts/python.exe training/lesson_docs/edition_20261029/manage.py rollback
```

Rollback khôi phục URL và xóa đúng các document/chunk mới của edition; file cũ và file mới đều được giữ để đối chiếu. Không chạy prepare/apply chồng lên edition đã áp dụng.
