# Tài liệu chi tiết ba khóa công nghệ thông tin

Đã gắn 36 PDF mới vào đúng bài học. Mỗi bài 3 trang; mỗi bản tổng hợp toàn khóa 37 trang, gồm mục lục 6 chương và 12 bài. Bộ tài liệu được biên soạn cho phạm vi nhập môn của các khóa, không thay thế giáo trình chuyên sâu hoặc chứng nhận học thuật.

Nội dung gồm kiến thức nền, phân tích chi tiết theo chủ đề, ví dụ giải từng bước, mã nguồn hoặc bảng minh họa phù hợp, bài tập và hướng giải, câu hỏi tự kiểm tra, đáp án và tài liệu đọc thêm. Giữ nguyên video, câu hỏi quiz, điểm, ghi danh và tiến độ. File PDF cũ được giữ; URL trước/sau nằm trong manifest.

## Bản tổng hợp

- [Mạng máy tính cơ bản](F:/studyonline-main/studyonline-main/backend/training/lesson_docs/it_detailed/course_513_complete.pdf) — 37 trang.
- [Cấu trúc dữ liệu và giải thuật cơ bản](F:/studyonline-main/studyonline-main/backend/training/lesson_docs/it_detailed/course_514_complete.pdf) — 37 trang.
- [Kiểm thử phần mềm nhập môn](F:/studyonline-main/studyonline-main/backend/training/lesson_docs/it_detailed/course_515_complete.pdf) — 37 trang.

## Kiểm chứng

- 36 lượt tải PDF qua API có xác thực, đối chiếu hash với file đã kiểm tra.
- Kiểm tra văn bản tiếng Việt, các đề mục bắt buộc và nội dung nhiều hơn bản trước.
- Chạy 13 ví dụ Python và các assert trong tài liệu.
- Xem ba ảnh mẫu HTML dùng để dựng PDF; kiểm tra chữ, mã nguồn và bảng văn bản.
- Các bản tổng hợp có bookmark chương/bài; file nguồn Markdown và HTML được giữ trong backend/training/lesson_docs/it_detailed/.

## Dựng lại

Chạy từ backend:

```powershell
.\.venv\Scripts\python.exe training/lesson_docs/rebuild_it_materials.py --build
.\.venv\Scripts\python.exe training/lesson_docs/rebuild_it_materials.py --apply
```

Script kiểm tra tài liệu thay đổi sau lúc dựng và dừng nếu có tài liệu AI đã được lập chỉ mục cần đồng bộ. Không ghi kết quả học tập giả.
