## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 2: Kỹ thuật kiểm thử và xử lý lỗi.
- Các bài trong chương: Phân vùng tương đương và giá trị biên; Báo cáo lỗi và kiểm thử hồi quy.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Chọn dữ liệu đại diện thay vì kiểm tra ngẫu nhiên mọi giá trị.

## Kiến thức nền
Phân vùng tương đương chia miền dữ liệu thành các nhóm dự kiến được xử lý tương tự, rồi chọn đại diện cho mỗi nhóm. Phải xét cả nhóm hợp lệ và không hợp lệ theo yêu cầu; đây là kỹ thuật lựa chọn test, không phải chứng minh mọi giá trị trong nhóm chắc chắn có hành vi giống nhau.

Với trường tuổi chỉ chấp nhận số nguyên từ 18 tới 60, có các vùng nhỏ hơn 18, từ 18 đến 60 và lớn hơn 60. Có thể chọn 17, 30, 61 làm đại diện. Kiểu đầu vào không phải số nguyên cũng cần xem xét theo hợp đồng dữ liệu.

Phân tích giá trị biên tập trung vào ranh giới vì lỗi so sánh và lệch một đơn vị thường xuất hiện ở đó. Với ví dụ trên, các điểm sát biên như 17,18,19 và 59,60,61 giúp kiểm tra cách xử lý ngưỡng dưới và trên.

## 1. Bắt đầu từ miền đầu vào
Giả sử tuổi bắt buộc là số nguyên, hợp lệ 18–60 bao gồm hai đầu. Chia miền số nguyên thành dưới 18, 18–60, trên 60; xét thêm dữ liệu thiếu, chuỗi không chuyển được hoặc số thập phân theo API. Không dùng kỹ thuật biên để né việc làm rõ kiểu dữ liệu.

## 2. Ví dụ dữ liệu và kỳ vọng
```text
Giá trị    Phân loại             Kỳ vọng theo giả định
17         Ngay dưới biên dưới  Từ chối
18         Tại biên dưới        Chấp nhận
19         Ngay trên biên dưới  Chấp nhận
59         Ngay dưới biên trên  Chấp nhận
60         Tại biên trên        Chấp nhận
61         Ngay trên biên trên  Từ chối
```
Đây là lựa chọn ba điểm quanh mỗi biên cho dữ liệu rời rạc. Tài liệu và tiêu chuẩn có thể định nghĩa các biến thể bao phủ khác; luôn ghi biến thể đang dùng. Với số thực không có “số kế tiếp” giống số nguyên nếu chưa quy định độ chính xác và bước dữ liệu.

## 3. Sai lầm thường gặp
Chỉ thử 30 rồi kết luận 18 và 60 đúng; chỉ thử giá trị hợp lệ; tự chấp nhận chuỗi “18” dù hợp đồng yêu cầu JSON number; đưa null và chuỗi rỗng vào cùng vùng dù server xử lý khác. Những quyết định này có thể làm mất ca quan trọng.

## 4. Bài tập và lời giải
Điểm quiz là số nguyên 0–100: thử -1,0,1,99,100,101, cùng trường thiếu và sai kiểu theo yêu cầu. Nếu số lượt tối đa là 3, kiểm tra trước lượt 3, sau lượt 3 và trường hợp lượt cuối đang làm: đây còn là bài toán trạng thái, không chỉ biên số. Nêu giới hạn của kỹ thuật thay vì tuyên bố sáu giá trị đã bao phủ mọi lỗi.

## Bài tập vận dụng bổ sung
trường điểm nhận số nguyên 0–100. Liệt kê vùng hợp lệ, các vùng không hợp lệ và dữ liệu biên; nêu kết quả mong đợi cho từng giá trị.

## Câu hỏi tự kiểm tra
1. Phân vùng tương đương giúp làm gì?
2. Tuổi hợp lệ là số nguyên 18–60. Giá trị nào thuộc vùng hợp lệ?
3. Bộ nào kiểm tra sát biên dưới 18 cho đầu vào nguyên?
4. Điểm hợp lệ từ 0 đến 100. Giá trị 101 thuộc vùng nào?
5. Vì sao cần kiểm tra giá trị biên?

## Gợi ý đáp án và điểm cần nhớ
- Chọn đại diện cho các nhóm đầu vào xử lý tương tự. Chọn đại diện giúp giảm số lượng test có chủ đích.
- 30. 30 nằm trong khoảng bao gồm cả 18 và 60.
- 17, 18, 19. Các điểm ngay dưới, tại và ngay trên biên kiểm tra điều kiện ngưỡng.
- Không hợp lệ phía trên. 101 vượt giới hạn trên; không tự suy đoán hành vi làm tròn.
- Dễ xuất hiện lỗi điều kiện và lệch một đơn vị. Kiểm tra biên nhắm vào một nhóm lỗi phổ biến, không bao phủ mọi lỗi.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
