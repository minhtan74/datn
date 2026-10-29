## Mục tiêu
Tạo gói kiểm thử có thể chạy lại cho một chức năng học trực tuyến.

## Kiến thức trọng tâm
Tự động hóa phù hợp với ca lặp lại, kết quả mong đợi ổn định và giá trị phát hiện lỗi đủ lớn so với chi phí bảo trì. Không tự động hóa mọi thao tác chỉ vì có công cụ. Tách unit test nhanh, API/integration và một số luồng giao diện quan trọng theo nhu cầu sản phẩm.

Một test tốt có chuẩn bị, hành động và kiểm tra kết quả cụ thể. Các test nên độc lập, dữ liệu có thể tái tạo và dọn trong phạm vi đã tạo. Khi test chập chờn, tìm nguyên nhân như chờ bất đồng bộ hoặc phụ thuộc thứ tự, không đơn giản chạy lại tới khi xanh rồi bỏ qua.

Dự án chọn chức năng ghi danh hoặc nộp quiz: lập phạm vi, rủi ro, test case, dữ liệu, báo cáo lỗi và kết quả hồi quy. Phân biệt chức năng chưa kiểm tra với test đã qua. Tài liệu kết thúc phải nêu rủi ro còn lại; quiz không tự xác nhận bộ test thực tế đã được triển khai.

## Ví dụ có hướng dẫn
Test ghi danh xác nhận request thành công, bản ghi tồn tại đúng một lần và quyền mở bài được cập nhật. Một test khác dùng dữ liệu riêng cho đăng ký trùng; không phụ thuộc test trước đã chạy.

## Bài tập thực hành
Nộp kế hoạch một trang, 12 test gồm quyền/biên/trạng thái/dữ liệu, hai báo cáo lỗi mẫu ghi rõ là tình huống giả định và ba test tự động có thể chạy lại trên lab. Không tạo lỗi hoặc kết quả giả vào hệ thống thật.

## Gợi ý tự kiểm tra
Đánh giá theo tiêu chí: truy vết yêu cầu, kết quả mong đợi rõ, dữ liệu độc lập, kiểm tra có ý nghĩa, bằng chứng chạy và giới hạn. Không tính số lượng test là thước đo duy nhất.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf