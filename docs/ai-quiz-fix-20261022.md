# Sửa thời gian chờ sinh câu hỏi AI — 22/10/2026

## Trường hợp được báo

Giảng viên sinh câu hỏi ôn tập **Chương 1: Tổng quan**, khóa **Nguyên Lí HDH**, giao diện chỉ hiển thị “Đang sinh…”. Đã tái hiện với khóa 7, chương 19, 10 câu phân bổ 3 dễ / 5 trung bình / 2 khó.

## Nguyên nhân đo được

- Đọc tài liệu chương mất 0,39 giây, không phải bước gây chậm chính.
- Mỗi mức độ khó trước đây gọi Gemini để sinh, rồi gọi thêm một lượt tự giải lại. Ba mức phải chờ ba lượt kiểm tra riêng trước khi API trả bản nháp.
- Lượt sinh hai câu khó chạm giới hạn 900 token (`MAX_TOKENS`), làm JSON bị cắt và phải gọi lại.
- Giao diện không có giới hạn thời gian chờ cho request này, không hiện thời gian đã chờ và chưa dùng `finally` để khôi phục trạng thái khi xảy ra lỗi bất ngờ.

## Thay đổi

- Sinh các nhóm độ khó rồi tự giải lại chung một lần. Câu hỏi vẫn được thẩm định đáp án và độ khó trước khi trả về khi dịch vụ AI đáp ứng được.
- Tăng ngân sách đầu ra cho nội dung, phương án, giải thích và căn cứ; giữ giới hạn tối đa 8192 token.
- Hiển thị nội dung đang xử lý và số giây đã chờ. Thêm **Dừng chờ**, giới hạn request sinh câu hỏi ở 180 giây và hiển thị lỗi ngay trên trang.
- Dùng `try/finally` cho sinh theo chương/bài, đề cuối khóa và sinh bù, để nút sinh hoạt động lại khi request kết thúc hoặc lỗi.
- Khi dừng chờ, trình duyệt ngừng chờ phản hồi và giữ các câu đã nhận được. Thao tác này không bảo đảm hủy công việc đang chạy trên backend; sinh câu hỏi không tự lưu quiz.
- Nếu bước tự giải lại không thành công, giữ bản nháp và hiển thị cảnh báo những câu chưa được tự kiểm tra. Giảng viên cần kiểm tra trước khi duyệt.

## Kết quả xác minh

Hai lần gọi Gemini thật dùng dữ liệu bản sao, không ghi quiz hoặc kết quả học tập vào database gốc:

| Lần chạy | Thời gian | Câu trả về | Quan sát |
|---|---:|---:|---|
| Trước sửa | 101,80 giây | 8/10 | 7 lượt gọi sinh/kiểm tra; phản hồi câu khó bị cắt một lần. |
| Sau sửa | 48,76 giây | 9/10 | Các lượt sinh kết thúc `STOP`; một lượt kiểm tra chung gặp HTTP 503 sau cơ chế thử lại. Bản nháp vẫn được trả về. |

Thời gian phụ thuộc dịch vụ Gemini và đây chỉ là hai lần quan sát, không phải cam kết tốc độ. Số câu có thể ít hơn yêu cầu vì hệ thống lọc câu trùng/không hợp lệ; giao diện vẫn có chức năng **Sinh bù**. Không coi 9 câu của lần thử sau là đã được tự kiểm tra đáp án: bước kiểm tra gặp lỗi dịch vụ.

- **36 test đạt**: sinh/độ khó, đảo quiz và gợi ý học tập. Có test mới xác nhận ba mức chỉ dùng một lượt kiểm tra chung và bản nháp có cảnh báo khi dịch vụ kiểm tra trả lỗi.
- Frontend build thành công; vẫn còn cảnh báo CSS/bundle đã ghi trong đợt kiểm tra trước.
- **7 phép kiểm tra Chrome đạt**, không có exception JavaScript: bộ đếm thời gian, dừng chờ, lỗi còn hiển thị sau khi toast đóng, lỗi bất ngờ không khóa nút, hết thời gian chờ không khóa nút, hiển thị bản nháp và cảnh báo chưa kiểm tra đáp án. Các tình huống API của phần kiểm tra Chrome được mô phỏng; timeout 180 giây được rút ngắn chỉ trong trình duyệt kiểm thử.
- Backend đang chạy có bật tự nạp lại mã. Không thay khóa API hoặc cấu hình database của người dùng.

## Bằng chứng

- [Trước sửa](ai-chapter-debug.json), [sau sửa](ai-chapter-after.json).
- [Kết quả kiểm tra giao diện](ai-ui-check.json), [ảnh giao diện kiểm thử](ai-ui-fixed.png).
