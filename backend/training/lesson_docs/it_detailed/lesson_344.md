## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 5: Kiểm thử dữ liệu và dịch vụ.
- Các bài trong chương: Kiểm thử API và phân quyền; Kiểm thử cơ sở dữ liệu và tính toàn vẹn.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Đối chiếu thao tác ứng dụng với ràng buộc dữ liệu và rollback trong môi trường test.

## Kiến thức nền
Kiểm thử dữ liệu xác nhận bản ghi được tạo, cập nhật hoặc giữ nguyên đúng yêu cầu. Kiểm tra khóa ngoại, tính duy nhất, giá trị NULL và ràng buộc miền. Với ghi danh, một cặp học viên–khóa có thể cần duy nhất; chỉ chặn bấm hai lần ở giao diện không đủ xử lý hai yêu cầu đồng thời.

Transaction nhóm thay đổi thành đơn vị công việc. Nếu một bước thất bại, rollback giúp tránh trạng thái một phần theo thiết kế giao dịch. Test cần xác minh trạng thái trước/sau, không chỉ thấy thông báo lỗi là cho rằng dữ liệu chưa đổi.

Dùng database test hoặc bản sao đã được phép, đánh dấu dữ liệu tạo cho test và dọn đúng phạm vi. Không chạy lệnh xóa hàng loạt trên dữ liệu học viên thật. Cần tính cả số bản ghi, liên kết và trường quan trọng; một phép COUNT không chứng minh mọi trường đã đúng.

## 1. Bằng chứng dữ liệu cần kiểm tra
Đếm bản ghi chỉ là một phần. Xác minh đúng user_id, course_id, trạng thái và trường thời gian nếu liên quan. Một bản ghi tồn tại nhưng gắn sai người dùng là lỗi dù COUNT tăng đúng một. Không lấy nội dung toast làm bằng chứng duy nhất cho commit.

## 2. Schema lab minh họa
```sql
CREATE TABLE lab_enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    UNIQUE (user_id, course_id)
);
```
Chỉ tạo bảng này trong database test. Cú pháp ID tự tăng và khóa ngoại phụ thuộc hệ quản trị; ví dụ tối thiểu không đại diện toàn schema của ứng dụng. Ghi lại ràng buộc thực tế trước khi viết kỳ vọng.

## 3. Test giao dịch nhiều bước
Tạo bản ghi cha, tạo bản ghi liên quan, gây lỗi có kiểm soát trước commit rồi kiểm tra rollback. Một thư viện có thể tự commit từng helper nên việc đặt hai lời gọi cạnh nhau không bảo đảm chúng nằm trong một transaction. Phải kiểm tra ranh giới giao dịch thật.

## 4. Đồng thời và dọn dữ liệu
Hai request đều kiểm tra “chưa có” trước khi insert có thể cùng vượt bước kiểm tra. Ràng buộc unique ở database là lớp bảo vệ cuối, còn server cần xử lý lỗi để trả phản hồi có nghĩa. Dọn test theo ID đã tạo, không DELETE toàn bảng hoặc quét theo tên người dùng thật.

## 5. Bài tập có tiêu chí
Thiết kế test trùng, NULL, khóa ngoại sai và rollback; nêu môi trường test, dữ liệu trước/sau và phép query đọc để xác nhận. Đạt khi bằng chứng phân biệt “request lỗi nhưng đã ghi một phần” với “giao dịch được hoàn tác đúng”.

## Bài tập vận dụng bổ sung
Thiết kế test chèn trùng, khóa ngoại không tồn tại và lỗi ở bước hai của giao dịch. Ghi trạng thái mong đợi của cả hai bảng, thực hiện trên database test.

## Hướng giải bài tập bổ sung
Sau rollback đúng thiết kế, không còn thay đổi một phần trong giao dịch đó. Việc dọn test phải dựa vào ID test đã tạo.

## Câu hỏi tự kiểm tra
1. Ràng buộc unique thường dùng để làm gì?
2. Khóa ngoại hỗ trợ điều gì?
3. Chỉ khóa nút đăng ký có xử lý chắc chắn yêu cầu đồng thời không?
4. Rollback được dùng để làm gì?
5. Môi trường nào phù hợp cho test ghi/xóa dữ liệu?

## Gợi ý đáp án và điểm cần nhớ
- Ngăn giá trị hoặc tổ hợp khóa bị trùng theo quy tắc. Unique biểu diễn tính duy nhất ở mức database.
- Toàn vẹn tham chiếu. Khóa ngoại liên kết tới bản ghi hợp lệ theo ràng buộc.
- Không. Hai client hoặc hai request vẫn có thể đến server.
- Hoàn tác thay đổi chưa commit của giao dịch. Rollback xử lý thay đổi trong phạm vi transaction.
- Database test hoặc bản sao được phép. Dữ liệu thử cần được cô lập và kiểm soát.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
