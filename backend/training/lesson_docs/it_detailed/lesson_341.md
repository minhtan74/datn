## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 4: Thiết kế kiểm thử theo hành vi.
- Các bài trong chương: Bảng quyết định và tổ hợp điều kiện; Kiểm thử chuyển trạng thái.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Chuyển quy tắc nghiệp vụ nhiều điều kiện thành các ca kiểm thử rõ ràng.

## Kiến thức nền
Bảng quyết định biểu diễn điều kiện và hành động theo từng quy tắc. Hữu ích khi kết quả phụ thuộc nhiều điều kiện kết hợp. Mỗi cột có thể mô tả một tổ hợp cùng hành vi mong đợi; cần phân biệt tổ hợp không thể xảy ra với tổ hợp chưa được kiểm tra.

Ví dụ quyền học phụ thuộc tài khoản hợp lệ, trạng thái ghi danh và nội dung miễn phí. Đặt giả định rõ trước khi lập bảng. Không mặc định mọi ứng dụng có cùng thứ tự ưu tiên giữa các điều kiện; cần hỏi hoặc xác nhận yêu cầu nếu quy tắc xung đột.

Khi số điều kiện tăng, số tổ hợp tăng nhanh. Có thể nhóm các quy tắc tương đương hoặc chọn kỹ thuật giảm tổ hợp theo rủi ro, nhưng phải ghi giới hạn. Pairwise không bảo đảm tìm mọi lỗi cần ba điều kiện tương tác. Dữ liệu test phải thực sự tạo được trạng thái đã mô tả.

## 1. Xác định điều kiện độc lập
Giả định bài miễn phí được xem không cần ghi danh; bài giới hạn cần ghi danh hợp lệ. Trong phạm vi tài khoản được phép dùng hệ thống, hai điều kiện Free và Enrolled cho bảng dưới. Nếu tài khoản bị khóa có quy tắc riêng, phải thêm hoặc làm rõ trước, không âm thầm áp bảng cho mọi vai trò.
```text
Quy tắc       Free       Enrolled       Cho xem
R1            Có         Có             Có
R2            Có         Không          Có
R3            Không      Có             Có
R4            Không      Không          Không
```
Có thể gộp R1 và R2 khi Enrolled không ảnh hưởng kết quả trong trường hợp Free; việc rút gọn cần giữ ý nghĩa điều kiện và khả năng truy vết.

## 2. Từ quy tắc sang test
Mỗi test tạo đúng trạng thái, gọi thao tác và xác minh quyền thật. Nếu UI ẩn nút, vẫn phải kiểm tra API trong môi trường được phép. Dữ liệu không hợp lệ như khóa đã gỡ không chỉ là một giá trị Free=false thông thường; nó có thể thuộc quy tắc tồn tại tài nguyên riêng.

## 3. Giảm tổ hợp có trách nhiệm
Ba điều kiện nhị phân tạo tối đa tám tổ hợp, trước khi loại các trường hợp bất khả thi. Pairwise nhắm tương tác từng cặp, không chứng minh bao phủ lỗi cần ba điều kiện. Tài liệu cần nêu cách chọn và phần bỏ lại.

## 4. Bài tập có đáp án
Giảm giá khi mã hợp lệ và tổng tiền ít nhất 500: cả hai đúng mới giảm. Tại biên 499/500/501, bổ sung kiểm tra giá trị biên bên cạnh bảng quyết định. Đừng tự dùng 499,99 nếu hợp đồng đang quy định đơn vị nguyên; xác nhận đơn vị tiền và cách làm tròn trước.

## Bài tập vận dụng bổ sung
Lập bảng cho giảm giá chỉ khi có mã hợp lệ và tổng tiền đạt ngưỡng. Viết test cho bốn tổ hợp, thêm tình huống mã hết hạn theo yêu cầu cụ thể.

## Hướng giải bài tập bổ sung
Hai điều kiện nhị phân có bốn tổ hợp trước khi rút gọn. Với phép AND, chỉ tổ hợp cả hai đúng được giảm giá.

## Câu hỏi tự kiểm tra
1. Bảng quyết định phù hợp khi nào?
2. Hai điều kiện đúng/sai độc lập có bao nhiêu tổ hợp?
3. Với giảm giá khi A AND B, trường hợp nào được giảm?
4. Tổ hợp không thể xảy ra nên được xử lý thế nào?
5. Pairwise có bảo đảm tìm mọi lỗi ba điều kiện tương tác không?

## Gợi ý đáp án và điểm cần nhớ
- Kết quả phụ thuộc tổ hợp nhiều điều kiện. Bảng nối các tổ hợp điều kiện với hành động.
- 4. Mỗi điều kiện có hai giá trị nên có 2 nhân 2 tổ hợp.
- A và B đều đúng. AND yêu cầu cả hai điều kiện thỏa.
- Ghi rõ lý do loại trừ theo yêu cầu. Cần minh bạch giả định và giới hạn của bảng.
- Không. Bao phủ cặp không tương đương bao phủ mọi bộ ba.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
