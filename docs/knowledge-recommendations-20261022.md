# Gợi ý ôn tập theo chương và bài — 22/10/2026

Đã triển khai chung cho đề cuối khóa/đề tổng hợp, bộ kiểm tra chương và bài. Điểm chính thức giữ theo cấu hình của quiz; phân tích kiến thức dùng đúng/sai của từng câu đã gắn chương/bài.

## Thay đổi

- Form câu hỏi nhập tay và bản nháp Word/AI có chọn chương, bài. Phạm vi bộ ôn bị khóa đúng chương/bài. AI có danh sách mã bài hợp lệ trong ngữ liệu và trả phân loại để giảng viên kiểm tra trước khi duyệt; mã ngoài phạm vi bị loại khỏi đề xuất. Không gọi thêm LLM để phân loại.
- Nộp bài lưu snapshot chương/bài và tên. Trang kết quả có bảng riêng của lượt vừa nộp, kể cả khi tải lại hoặc giáo viên sửa câu hỏi về sau.
- Dashboard/Tiến độ và trang kết quả có gợi ý hiện tại: tối đa 3 phần ưu tiên, bài đủ căn cứ đứng trước chương; chương đủ căn cứ đứng trước kết luận về bài chỉ có ít câu. Bỏ gợi ý chủ đề/làm lại trùng nội dung đã được bao phủ.
- Bấm ôn đi đúng bài hoặc mở đúng chương. Có bộ luyện bài thì dẫn vào đó; chưa có thì dùng bộ luyện chương và ghi rõ. Không hiện bộ rỗng, khóa không còn ghi danh hoặc lượt đã hết mà không thể tiếp tục.
- Kết quả mới thay thế căn cứ cũ của cùng bài học qua các đề; các bài khác giữ căn cứ gần nhất. Bảng tổng chương có thể gồm nhiều thời điểm; câu chỉ gắn chương có nhóm riêng. Không đổi điểm cuối khóa đã nộp.
- Mở gợi ý ghi checkpoint, so sánh sau khi có kết quả mới đúng phần kiến thức. Báo khác bộ câu hoặc mẫu ít; không khẳng định việc ôn gây ra cải thiện.
- Học tiếp ưu tiên khóa chưa hoàn thành có lượt nộp quiz mới nhất.

## Kiểm chứng

- **98 kiểm thử backend**: `test_knowledge.py`, `test_recommendations.py`, `test_quiz_difficulty.py`, `test_quiz_stream.py`, `test_quiz_shuffle.py`, `test_word_import.py`.
- **3 kiểm thử Node** cho bộ đọc luồng AI, giữ tương thích sinh quiz.
- **9 kiểm tra MySQL tích hợp** trên database sao chép: migration, quyền, phân loại theo lô/nhập tay, nộp đề cuối khóa, snapshot không đổi, checkpoint chờ, luyện bài thay căn cứ và điểm cuối khóa giữ nguyên. Ví dụ bài 1 từ 1/6 lên 6/6, phần trước/sau hiện +83,3 điểm phần trăm. Bản sao được xóa sau kiểm tra, không chèn kết quả hoặc mốc ôn giả vào database local. [Kết quả](knowledge-integration.json).
- **8 kiểm tra Chrome**: thống kê bài ở kết quả thật, link ôn/luyện, giải thích căn cứ, bảng kiến thức hiện tại, mở đúng chương, điện thoại không tràn ngang, khóa chương của form giảng viên và chọn bài. Không lưu thay đổi câu hỏi khi kiểm tra trình duyệt. [Kết quả](knowledge-browser.json).
- Frontend build thành công; cảnh báo CSS font import và kích thước bundle đã tồn tại từ trước.

Ảnh: [kết quả](knowledge-result.png), [tiến độ](knowledge-progress.png), [điện thoại](knowledge-mobile.png), [soạn câu hỏi](knowledge-authoring.png).

## Dữ liệu local và giới hạn

Đã áp dụng `0021_knowledge_scope`. Khôi phục được chương cho 97/210 câu và bài cho 66/210 câu, từ phạm vi đề hoặc tên khớp duy nhất; không suy đoán chủ đề đồng nghĩa. Giữ 1.307 câu trả lời hiện có; 232 câu trả lời xác định được chương và 96 xác định được bài. Phần còn lại vẫn tính điểm tổng, chỉ báo chưa phân loại cho phân tích chương/bài.

Với dữ liệu vừa test ở HĐH: gợi ý bài 1 đúng 6/20, bài 2 đúng 3/10; bài 1 có bộ luyện riêng, bài 2 dẫn bộ luyện chương. Chương 3 có 1/12 đúng nhưng từng bài còn ít câu nên gợi ý ôn chương thay vì kết luận yếu từng bài.

Cần ít nhất 5 question ID khác nhau, dưới 70% thì ưu tiên ôn. Đây là quy tắc hỗ trợ ban đầu, chưa đo hiệu quả sư phạm. Bài luyện dùng bộ câu hiện có; hệ thống chưa tự tạo câu tương đương mới mỗi lần bấm. Với câu cũ chưa rõ nguồn kiến thức, giảng viên chọn chương/bài trong form để các lượt nộp mới có phân loại đầy đủ; phân loại lịch sử được giữ nguyên.

Môi trường khác cần chạy `alembic upgrade head` trước khi sử dụng phiên bản này.
