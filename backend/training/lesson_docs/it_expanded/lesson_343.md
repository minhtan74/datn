## Mục tiêu
Thiết kế ca kiểm thử hợp đồng HTTP và quyền truy cập theo tài khoản.

## Kiến thức trọng tâm
API test cần kiểm tra phương thức, đường dẫn, tham số, kiểu dữ liệu, mã trạng thái và nội dung phản hồi theo hợp đồng. Mã 200 không đủ chứng minh đúng: cần xác nhận dữ liệu, tác dụng phụ và quyền. Lỗi có thể nằm ở nghiệp vụ dù phản hồi vẫn là JSON hợp lệ.

Phân biệt xác thực danh tính với phân quyền tài nguyên. Kiểm tra người chưa đăng nhập, đúng chủ sở hữu, người khác và vai trò quản trị theo yêu cầu. Thay ID tài nguyên là tình huống kiểm tra quyền ở mức đối tượng quan trọng; chỉ thực hiện trên dữ liệu lab được phép.

Test đầu vào gồm thiếu trường, sai kiểu, giá trị biên và tài nguyên không tồn tại. Không đưa token vào báo cáo hoặc nguồn mã. Tạo dữ liệu test riêng và dọn trong phạm vi đó. Các mã phản hồi cụ thể phụ thuộc hợp đồng API, không suy ra mọi lỗi đều phải cùng một mã.

## Ví dụ có hướng dẫn
GET kết quả quiz của chính mình được phép. Đổi result_id sang bài của tài khoản lab khác phải bị từ chối theo hợp đồng; kiểm tra nội dung phản hồi không lộ dữ liệu dù mã trạng thái có vẻ đúng.

## Bài tập thực hành
Lập năm test cho API đăng ký: hợp lệ, khóa không tồn tại, thiếu xác thực, đăng ký trùng và ID sai kiểu. Nêu điều kiện dữ liệu trước/sau, dùng môi trường thử nghiệm.

## Gợi ý tự kiểm tra
Kiểm tra đồng thời mã, schema, quyền và tác dụng dữ liệu. Không ghi token thật vào minh chứng.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf