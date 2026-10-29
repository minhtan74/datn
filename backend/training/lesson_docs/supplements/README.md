# Tài liệu học thêm cho các khóa đang có

Biên soạn ngày 12/10/2026, đối chiếu database local có 7 khóa và 65 bài. Tên và ID trong database này khác một số dữ liệu demo: khóa 7 là Nguyên Lí HDH, không phải Tiếng Anh. Không nạp tài liệu theo giả định ID khóa trong seed cũ.

Mỗi tài liệu có mục tiêu, giải thích, ví dụ, bài tập nhận biết/vận dụng/phân tích, gợi ý lời giải và tiêu chí tự đánh giá. Đây là phần mở rộng do dự án biên soạn; các liên kết nguồn dùng để đối chiếu và học tiếp, không phải tài liệu sao chép nguyên văn.

| Khóa | Nội dung bổ sung | Nguồn Markdown | PDF riêng | Học viên tải trong bài |
|---|---|---|---|---|
| Python | Tham chiếu, sao chép, kiểm tra giá trị biên, hàm, thiết kế quản lý sinh viên | [python.md](python.md) | [PDF](../completed/supplement_course_1.pdf) | 9 — Dự án nhỏ: Quản lý sinh viên |
| JavaScript | Chuyển kiểu, DOM an toàn, Promise, Fetch, phản hồi cũ, lưu To-do List | [javascript.md](javascript.md) | [PDF](../completed/supplement_course_2.pdf) | 18 — Module & Fetch API |
| Java | equals/hashCode, đóng gói, interface, collection, ngoại lệ, quản lý sản phẩm | [java.md](java.md) | [PDF](../completed/supplement_course_3.pdf) | 27 — Dự án: Quản lý sản phẩm |
| HTML/CSS | Semantic, form, bàn phím, box model, Grid/Flexbox, responsive | [html_css.md](html_css.md) | [PDF](../completed/supplement_course_4.pdf) | 36 — Dự án: Landing Page Responsive |
| React | State, updater, effect, cleanup, request cũ, context và quyền truy cập | [react.md](react.md) | [PDF](../completed/supplement_course_5.pdf) | 45 — Dự án: Trang quản lý khoá học |
| MySQL | JOIN nhân dòng, NULL, chuẩn hóa, ràng buộc, giao dịch, callback lặp, chỉ mục | [mysql.md](mysql.md) | [PDF](../completed/supplement_course_6.pdf) | 54 — Dự án: Thiết kế CSDL website học trực tuyến |
| Nguyên Lí HDH | Đồng thời/song song, Round Robin, IPC, race condition, semaphore, deadlock | [os.md](os.md) | [PDF](../completed/supplement_course_7.pdf) | 65 — Các giải pháp đồng bộ hóa |

Trên website, mở bài ở cột cuối và tải tài liệu: phần học thêm được ghép sau bài học chính. File gốc được giữ nguyên, đường dẫn trước/sau lưu tại [changes.json](../completed/changes.json). AI Tutor có thêm bản học thêm riêng theo khóa để truy hồi. Tài liệu chính của bài cuối được đồng bộ chỉ mục với bản PDF mới.

## Kiểm tra và bổ sung trên database khác

Chạy từ backend:

```powershell
.venv\Scripts\python -X utf8 training/lesson_docs/complete_materials.py
.venv\Scripts\python -X utf8 training/lesson_docs/complete_materials.py --build
.venv\Scripts\python -X utf8 training/lesson_docs/complete_materials.py --apply
```

Lệnh mặc định chỉ đọc database và xuất kiểm tra file tại completed/audit.json. --build cần Chrome/Edge để tạo PDF. --apply thay đường dẫn tài liệu của bài cần bổ sung và ghi chỉ mục RAG; đọc kết quả kiểm tra trước khi áp dụng cho database khác. Script từ chối tài liệu chính không khớp ID/tiêu đề hoặc khóa không có học thêm phù hợp. Không dùng script seed Tiếng Anh/Toán theo ID 7/8 cho database này.

Hệ thống hiện dùng một tài liệu chính cho mỗi bài, nên phần mở rộng được ghép vào PDF bài cuối thay vì thêm một nút tài liệu mới. Sửa nguồn Markdown cần dựng lại PDF; muốn cập nhật bản đã gắn phải chủ động triển khai lại, vì --apply bỏ qua URL đã gắn để không nạp trùng.
