## Mục tiêu
Đối chiếu thao tác ứng dụng với ràng buộc dữ liệu và rollback trong môi trường test.

## Kiến thức trọng tâm
Kiểm thử dữ liệu xác nhận bản ghi được tạo, cập nhật hoặc giữ nguyên đúng yêu cầu. Kiểm tra khóa ngoại, tính duy nhất, giá trị NULL và ràng buộc miền. Với ghi danh, một cặp học viên–khóa có thể cần duy nhất; chỉ chặn bấm hai lần ở giao diện không đủ xử lý hai yêu cầu đồng thời.

Transaction nhóm thay đổi thành đơn vị công việc. Nếu một bước thất bại, rollback giúp tránh trạng thái một phần theo thiết kế giao dịch. Test cần xác minh trạng thái trước/sau, không chỉ thấy thông báo lỗi là cho rằng dữ liệu chưa đổi.

Dùng database test hoặc bản sao đã được phép, đánh dấu dữ liệu tạo cho test và dọn đúng phạm vi. Không chạy lệnh xóa hàng loạt trên dữ liệu học viên thật. Cần tính cả số bản ghi, liên kết và trường quan trọng; một phép COUNT không chứng minh mọi trường đã đúng.

## Ví dụ có hướng dẫn
Hai yêu cầu đăng ký cùng khóa đến gần nhau. Ràng buộc unique và xử lý server phải bảo đảm chỉ một ghi danh; giao diện cần phản hồi theo hợp đồng thay vì báo thành công hai bản ghi.

## Bài tập thực hành
Thiết kế test chèn trùng, khóa ngoại không tồn tại và lỗi ở bước hai của giao dịch. Ghi trạng thái mong đợi của cả hai bảng, thực hiện trên database test.

## Gợi ý tự kiểm tra
Sau rollback đúng thiết kế, không còn thay đổi một phần trong giao dịch đó. Việc dọn test phải dựa vào ID test đã tạo.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf