# Tối ưu tốc độ và hiển thị bản nháp AI — 22/10/2026

## Thay đổi

- Với đề nhiều mức có tối đa 12 câu, gửi ngữ liệu một lần để sinh đủ phân bổ độ khó, sau đó tự giải lại một lần. Trường hợp 10 câu giảm từ ba lượt sinh xuống một lượt sinh, vẫn giữ bước kiểm tra đáp án.
- Với đề nhiều mức lớn hơn 12 câu, chạy tối đa hai nhóm song song. Giới hạn chung trong một tiến trình backend cho bước sinh/kiểm tra quiz là hai. Session database chỉ được sử dụng ở thread điều phối; các worker nhận ngữ liệu đã đọc.
- Mỗi worker có tập loại trùng riêng; thread điều phối loại trùng giữa các nhóm và với câu hỏi đã lưu. Lô nhiều mức giữ nhãn hợp lệ của model và không lấy vượt số câu yêu cầu ở mỗi mức.
- Giao diện nhận các sự kiện qua `/api/ai/generate-quiz/stream` và hiển thị bản nháp trước khi bước kiểm tra đáp án hoàn tất. API JSON cũ vẫn sử dụng được.
- Khi AI còn xử lý, khóa chỉnh sửa câu hỏi và duyệt để kết quả kiểm tra cuối không ghi đè nội dung đang sửa. Hoàn tất sẽ cập nhật cờ đúng/sai, cảnh báo độ khó và mở lại các thao tác.
- Giữ câu đã nhận được khi luồng báo lỗi, mất kết nối hoặc người dùng dừng chờ. Việc dừng chờ không bảo đảm ngắt được một yêu cầu đã gửi tới nhà cung cấp AI; backend sẽ dừng ở mốc thông báo tiếp theo. Không tự lưu quiz.

## Đo bằng Gemini thật

Thử trên database bản sao, đúng khóa 7 / Chương 1: Tổng quan (chương 19), yêu cầu 10 câu với 3 dễ / 5 trung bình / 2 khó:

| Cách chạy | Bản nháp đầu tiên | Hoàn tất | Câu trả về |
|---|---:|---:|---:|
| Trước đợt tối ưu này, chờ JSON đầy đủ | 48,76 giây | 48,76 giây | 9 |
| Thử sinh song song và trả từng nhóm | 35,40 giây | 57,20 giây | 9 |
| Luồng cuối: gom đề ngắn vào một lượt sinh | **23,40 giây** | **31,98 giây** | **9** |

Lần đo JSON cũ gặp HTTP 503 ở bước kiểm tra; lần đo song song tự giải lại được toàn bộ chín câu. Lần đo cuối tự giải lại khớp đáp án 9/9 câu và gắn một cảnh báo về độ khó; không có câu thiếu căn cứ theo phép kiểm tra của hệ thống. Các lần chạy khác thời điểm, chịu biến động dịch vụ, không phải benchmark kiểm soát tải hay cam kết tốc độ. Giảng viên vẫn cần xem lại cảnh báo và nội dung trước khi duyệt. Số câu có thể thiếu vì loại câu trùng/không hợp lệ; giữ chức năng Sinh bù.

## Xác minh

- **41 test backend đạt**: quy tắc sinh và độ khó, kiểm tra chung, phân bổ lô nhiều mức, song song có giới hạn, loại trùng, trả bản nháp trước bước thẩm định, stream thành công/lỗi/phân quyền, đảo quiz và gợi ý học tập. Dữ liệu kiểm thử nằm trong bộ nhớ.
- **3 test JavaScript đạt**: JSON và Unicode chia qua nhiều gói mạng, lỗi sau khi đã nhận một phần và luồng kết thúc thiếu sự kiện hoàn tất.
- **8 kiểm tra Chrome đạt**, không có exception JavaScript: hiển thị câu trước khi hoàn tất, khóa duyệt/chỉnh sửa trong khi xử lý, áp dụng kết quả thẩm định cuối, mở lại chỉnh sửa, giữ bản nháp khi lỗi/mất kết nối/dừng chờ. Bài kiểm tra giao diện dùng HTTP server mô phỏng có gửi từng phần thật và chờ trước sự kiện hoàn tất; không gọi Gemini thêm.
- Frontend build thành công. Các cảnh báo CSS/bundle đã có từ trước vẫn còn.

## Bằng chứng

- [Lần đo song song](ai-speed-live.json), [lần đo cuối](ai-speed-mixed.json).
- [Kết quả kiểm tra giao diện](ai-stream-ui.json), [ảnh giao diện](ai-stream-ui.png).
