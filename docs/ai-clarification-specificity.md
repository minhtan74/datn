# Sửa AI hỏi lại thừa

Đã sửa vấn đề số 3 trong báo cáo web: câu đã đủ chủ đề/dữ kiện không còn bị ép gửi thêm code hoặc tên khái niệm chỉ vì một từ khóa trùng.

## Nguyên nhân và thay đổi

- Quy tắc `báo lỗi/sửa lỗi` trước đây chặn cả câu hỏi kiến thức về hành vi API hoặc kiểm thử. Bản sửa phân biệt yêu cầu chẩn đoán một lỗi cá nhân còn thiếu dữ liệu với câu hỏi định nghĩa/so sánh/hành vi đã rõ.
- Quy tắc đại từ tiếng Anh chạy trên văn bản bỏ dấu, làm “thật” khớp với `that`. Nay `this`/`that` được xét trên văn bản gốc; đây là nguyên nhân cụ thể tìm được ở câu hỏi máy một lõi, thay cho giả thuyết ban đầu về đại từ “nó”.
- Khi câu đã nêu đối tượng, đại từ trong chính câu không tự gây hỏi lại hoặc kéo chủ đề cũ vào câu mới. Câu như “Nó hoạt động thế nào?” vẫn hỏi thêm nếu không có đối tượng/ngữ cảnh.
- Câu so sánh rõ có thể bắt đầu chủ đề mới sau một lời hỏi thêm về sửa code. Lượt hỏi tiếp thật sự vẫn dùng chủ đề đã giải quyết trong hội thoại.
- Prompt trả lời nhắc không đòi code chỉ vì xuất hiện từ “lỗi”; truy hồi tài liệu, ngưỡng liên quan, phân quyền và quy tắc không bịa khi thiếu tài liệu vẫn được giữ.

## Kiểm chứng

- **77 kiểm thử backend đạt**, gồm trường hợp có dấu/không dấu, câu rõ/thiếu dữ kiện, chuyển chủ đề, hỏi tiếp và lỗi dịch vụ/phạm vi hội thoại.
- **3/3 ca hồi quy qua API thật** được trả lời trực tiếp, có nguồn; đã đối chiếu ý chính với các chunk nguồn lưu trong kết quả.
- **6/6 ca thiếu thông tin qua API thật** vẫn hỏi thêm đúng loại, không tự gắn nguồn.
- Bộ phân loại cho **50/50 câu kiến thức đã đóng băng** đi vào bước truy hồi. Đây chỉ là kiểm tra phân loại, không phải 50/50 câu trả lời đúng.

| Ca từng hỏi lại nhầm | Sau sửa | Nguồn hỗ trợ ý chính |
|---|---|---|
| Máy một lõi có đồng thời được không, có phải song song thật không? | Có thể xen kẽ để nhiều việc tiến triển; không đồng nghĩa song song thật trên một lõi | Chunk 1297/1158: đồng thời, song song và xen kẽ |
| HashMap.put cùng một khóa có tự báo lỗi trùng không? | Có thể ghi đè; muốn tránh trùng thì kiểm tra hoặc dùng thao tác phù hợp, có ví dụ putIfAbsent | Chunk 2106–2107: Map.put và ví dụ sản phẩm |
| Chạy lại ca gây lỗi đã thay thế hồi quy chưa? | Chưa; phân biệt confirmation testing với regression testing theo vùng ảnh hưởng | Chunk 2707: kiểm tra sau sửa |

Sáu ca vẫn hỏi thêm: giải thích không nêu chủ đề, code Python bị lỗi chưa có code/log, giải câu 2 chưa có đề, chọn lựa không nêu đối tượng, “Trong Python, nó là gì?”, và “Hàm này hoạt động thế nào?” chưa nêu hàm.

## Dữ liệu và giới hạn

Các câu gọi API dùng hội thoại audit riêng và xóa đúng id sau khi kiểm tra. Trước/sau vẫn là 4 hội thoại, 18 tin nhắn, 176 tài liệu và 2063 chunk. Không sửa hay xóa lịch sử người dùng có sẵn.

Không ghi đè kết quả đánh giá 90% trước đây, không công bố phần trăm chính xác mới cho toàn bộ AI. Chỉ các ca hồi quy trên được đối chiếu nội dung trả lời trong lần kiểm tra này; mô hình vẫn có thể cần hỏi thêm khi dữ kiện thực sự chưa đủ.

Mã: [clarification.py](../backend/app/ai/rag/clarification.py), [prompt/pipeline](../backend/app/ai/rag/rag_pipeline.py), [kiểm thử](../backend/tests/test_tutor_clarification.py).

Bằng chứng: [câu trả lời đầu tiên và trang nguồn](ai-clarification-specificity-results.json), [script gọi API thật](ai-clarification-specificity-check.py).
