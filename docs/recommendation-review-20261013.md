# Rà soát gợi ý học tập — 13/10/2026

Kết luận: logic hiện tại phù hợp cho hỗ trợ lựa chọn nội dung ôn tập, có căn cứ và xử lý thiếu dữ liệu. Chưa đủ cơ sở để gọi là phép đo năng lực đã được kiểm chứng học thuật.

## Những điểm đã xác minh

- Tách điểm chính thức theo cấu hình đề với căn cứ nội dung từ lượt gần nhất.
- Nhóm theo mã chủ đề trong từng khóa; không cộng nhiều lượt của cùng question ID để tăng số câu làm căn cứ.
- Dưới 5 câu không xếp Yếu/Tốt; câu thiếu chủ đề vẫn tính điểm tổng nhưng không suy đoán kiến thức.
- Phân loại lúc nộp được lưu riêng; sửa câu hỏi sau đó không đổi phân loại kết quả cũ. Dữ liệu trước migration được ghi rõ là khôi phục theo metadata tại lúc migration.
- Giải thích có tỷ lệ đúng, số câu, đề, thời điểm và link kết quả.
- Liên kết bài luyện phải đúng khóa, có câu của chủ đề, được xác nhận và còn lượt hoặc có lượt đang làm chưa hết hạn.
- So sánh chỉ lấy bài làm mới sau checkpoint; hiện số câu ở cả hai mốc, chênh lệch điểm phần trăm và giới hạn về khác độ khó/nhớ đáp án. Không coi mở gợi ý là đã học xong.

## Kiểm tra dữ liệu local

Chỉ đọc số liệu tổng hợp, không ghi điểm hoặc xác nhận hộ giảng viên:

| Chỉ số | Số lượng |
|---|---:|
| Chủ đề trong danh mục | 55 |
| Chủ đề được xác nhận | 0 |
| Chủ đề gắn bài học | 0 |
| Chủ đề gắn bộ ôn tập | 0 |
| Học viên đang hoạt động, có ghi danh | 9 |
| Cặp học viên–chủ đề đủ ít nhất 5 câu | 17 |
| Cặp học viên–chủ đề chưa đủ 5 câu | 112 |
| Cặp đủ dữ liệu nhưng tỷ lệ đúng dưới 70% | 11 |
| Gợi ý có liên kết trực tiếp từ nguồn bài/tên trùng chính xác | 3 |
| Gợi ý có nút bài luyện được xác nhận | 0 |

Vì danh mục chưa được xác nhận/liên kết, hệ thống chủ yếu dẫn đến danh sách bài. Đây là thiếu cấu hình nội dung thực tế, không phải nút bài luyện bị lỗi. Giảng viên cần kiểm tra nội dung và xác nhận trong **Chủ đề kiến thức** trước khi demo phần liên kết cụ thể.

## Các điểm đã sửa khi rà soát

- Không chặn mở nội dung học khi ghi checkpoint bị lỗi; thông báo rằng chưa có mốc so sánh.
- Hiển thị lỗi khi bấm Cập nhật gợi ý thất bại.
- Đổi tên danh mục và cập nhật tên ở câu hỏi trong cùng giao dịch.
- Từ chối tạo chủ đề cho khóa không tồn tại bằng lỗi 404 thay vì lỗi ràng buộc database.

## Giới hạn cần trình bày trung thực

- Mốc 5 câu và 70% là quy tắc ban đầu, chưa được hiệu chỉnh trên một nghiên cứu học viên.
- Question ID khác nhau không bảo đảm câu hỏi độc lập về kiến thức; các bản sao câu hỏi ở nhiều đề vẫn có thể làm tăng số câu. Giáo viên cần kiểm tra trùng nội dung và chất lượng câu hỏi.
- Các đề có thể khác độ khó, thời điểm; hiện chưa điều chỉnh tỷ lệ theo độ khó hoặc độ cũ của kết quả.
- Checkpoint ghi nhận mở gợi ý, chưa chứng minh học viên đã đọc hết bài hoặc sự cải thiện do việc ôn.
- Kiểm thử xác nhận logic phần mềm; không thay cho đánh giá hiệu quả học tập hoặc kiểm tra trực quan đầy đủ giao diện.

Kết quả kiểm tra sau sửa: **76 tests passed**; build frontend thành công. [Bộ tình huống kiểm chứng](recommendation-validation.md).
