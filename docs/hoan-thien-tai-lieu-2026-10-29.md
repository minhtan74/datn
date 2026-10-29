# Hoàn thiện tài liệu khóa học — 29/10/2026

Đã bổ sung tài liệu cho **101 bài thuộc 10 khóa nội dung** trên database local. Bài trên web đã trỏ tới PDF gồm nội dung gốc và phụ lục thực hành mới; có thêm 10 PDF tổng hợp toàn khóa để đọc/tải từ các liên kết dưới đây.

## PDF toàn khóa

| Khóa | Số bài | Số trang bản tổng hợp | Tải PDF |
|---|---:|---:|---|
| Python Cơ Bản Cho Người Mới Bắt Đầu | 9 | 32 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_1_complete.pdf) |
| JavaScript Từ Zero Đến Hero | 9 | 32 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_2_complete.pdf) |
| Lập Trình Java Căn Bản | 9 | 31 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_3_complete.pdf) |
| HTML & CSS Nhập Môn | 9 | 31 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_4_complete.pdf) |
| ReactJS Chuyên Sâu | 9 | 31 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_5_complete.pdf) |
| MySQL & Thiết Kế Cơ Sở Dữ Liệu | 9 | 32 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_6_complete.pdf) |
| Nguyên Lí HDH | 11 | 66 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_7_complete.pdf) |
| Mạng máy tính cơ bản | 12 | 49 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_513_complete.pdf) |
| Cấu trúc dữ liệu và giải thuật cơ bản | 12 | 49 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_514_complete.pdf) |
| Kiểm thử phần mềm nhập môn | 12 | 49 | [PDF](../backend/training/lesson_docs/edition_20261029/generated/course_515_complete.pdf) |

Tổng các bản toàn khóa: **402 trang**, gồm phần gốc, **101 trang bổ sung** và mục lục. Số trang là số trang PDF thực tế, không phải thước đo duy nhất của độ đầy đủ nội dung.

## Nội dung được bổ sung

- Mỗi bài có tình huống thực tế, giải thích hoặc ví dụ, bài tự luyện và hướng giải.
- Python: lỗi trộn str/int, input, IndentationError, range/index, return/print, OOP và quản lý sinh viên.
- JavaScript: const và mảng, nối chuỗi, DOM null, form, Promise, xử lý lỗi HTTP và dữ liệu JSON.
- Java, HTML/CSS, React: tình huống công cụ, dữ liệu, giao diện, state, API, phân quyền và dự án theo bài.
- MySQL: khóa chính/khóa ngoại/NULL, LEFT JOIN đúng đối tượng, đếm sau JOIN, NOT EXISTS, ERD và quy tắc dữ liệu.
- Hệ điều hành, mạng, giải thuật và kiểm thử: mô hình thực hành, giả định, giá trị biên, quy trình chẩn đoán, kiểm chứng và báo cáo.

## Kiểm chứng

- **101/101** PDF bài tải qua API có xác thực thành công; hash nội dung khớp file đã dựng.
- **101/101** tài liệu bổ sung được index: tổng **842 chunk mới**, đúng khóa/bài và trang vật lý trong PDF.
- **11/11** câu tra cứu chọn được tài liệu mới trong phạm vi từng bài, bao phủ cả 10 khóa. Không gọi LLM trong kiểm tra này, nên chưa kết luận mọi câu trả lời AI sau bổ sung đều đúng hoặc hết lỗi từ chối.
- Chạy **21 khối ví dụ Python**; kiểm tra cú pháp **10 khối JavaScript**, trong đó chạy **7 khối thuần**; biên dịch **8 khối Java**. JSX và ví dụ DOM/fetch theo ngữ cảnh không được tính là đã chạy đầu cuối.
- **4 truy vấn SELECT/JOIN** được kiểm tra bằng dữ liệu lab SQLite riêng. Không dùng kết quả đó để thay thế xác minh mọi khác biệt MySQL; các lệnh cài đặt/server MySQL không được chạy như ví dụ tự động.
- Xem ba bản trình bày in: [Python](materials-preview-2.png), [MySQL](materials-preview-49.png), [kiểm thử](materials-preview-343.png). Đây là ảnh xem trước HTML print; kiểm tra tải/hash/văn bản thực hiện trực tiếp với PDF.
- Hash dữ liệu tài khoản, khóa/chương, quiz/câu hỏi, kết quả/đáp án, ghi danh, tiến độ, thanh toán, video, nội dung bài và lịch sử AI trước/sau khớp. Chỉ URL tài liệu bài học và các bản ghi tài liệu/chunk bổ sung được cập nhật.

## Giữ bản gốc và phạm vi cập nhật

Giữ toàn bộ PDF gốc, document và chunk cũ. Với 65 bài có index tài liệu chính, chỉ thêm index phụ lục; 36 bài trước đó chưa có index theo bài được index cả bản PDF. Phần bổ sung được ghi cùng URL mới trong một transaction. Có manifest và lệnh rollback để khôi phục riêng edition.

Khóa `PYTEST Course` và bài thử nghiệm #365 được loại khỏi bộ giáo trình. Đây là dữ liệu test, không phải khóa giảng dạy được bổ sung. Kết quả đã áp dụng cho database local; Docker/database khác cần áp dụng riêng theo quy trình.

## Nguồn, nhật ký và cách dựng lại

- [Nguồn Markdown và quy trình](../backend/training/lesson_docs/edition_20261029/README.md).
- [Manifest trước/sau](../backend/training/lesson_docs/edition_20261029/generated/manifest.json).
- [Xác minh tải PDF và trang RAG](../backend/training/lesson_docs/edition_20261029/generated/verification.json).
- [Kết quả tra cứu theo bài](../backend/training/lesson_docs/edition_20261029/generated/retrieval-validation.json).
- [Kiểm tra ví dụ](../backend/training/lesson_docs/edition_20261029/generated/code-validation.json), [lab SQL](../backend/training/lesson_docs/edition_20261029/generated/sql-validation.json).

Tài liệu mới được biên soạn bằng tiếng Việt với ví dụ riêng; mục Nguồn học tiếp dẫn tài liệu Python, MDN, Dev.java, React, MySQL 8.4, OSTEP, RFC 9293 và pytest. Nội dung bổ sung phục vụ đề cương hiện có, không tạo điểm hoặc kết quả học tập giả.
