## Vị trí bài học trong khóa
- Khóa học: Cấu trúc dữ liệu và giải thuật cơ bản.
- Chương 6: Thiết kế lời giải và thực hành.
- Các bài trong chương: Chia để trị và quy hoạch động nhập môn; Dự án nhỏ: bộ tra cứu và thống kê dữ liệu.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Phân biệt chia để trị với lưu trạng thái bài toán con.

## Kiến thức nền
Chia để trị chia bài toán thành các phần nhỏ, giải rồi kết hợp; merge sort là ví dụ. Quy hoạch động thường phù hợp khi có các bài toán con chồng lặp và cấu trúc tối ưu thích hợp. Không phải cứ có đệ quy là cần quy hoạch động.

Một lời giải quy hoạch động cần định nghĩa trạng thái, chuyển trạng thái, trường hợp cơ sở và thứ tự tính. Với số cách bước lên n bậc, mỗi bước 1 hoặc 2 bậc, có thể đặt ways[0]=1, ways[1]=1 và ways[n]=ways[n-1]+ways[n-2]. Bộ nhớ có thể giảm nếu chỉ cần hai trạng thái trước.

Tham lam chọn quyết định cục bộ, nhưng cần chứng minh cho bài toán cụ thể. Chẳng hạn đổi tiền với mệnh giá tùy ý không bảo đảm thuật toán luôn lấy đồng lớn nhất sẽ dùng ít đồng nhất. Bắt đầu từ mô hình bài toán và ví dụ phản chứng, không chọn kỹ thuật theo tên gọi hấp dẫn.

## 1. Từ lời giải trực tiếp tới trạng thái
Xác định thông tin tối thiểu để mô tả bài toán con. Với số cách lên cầu thang, trạng thái chỉ cần số bậc còn lại khi bước cho phép luôn là 1 hoặc 2. Nếu luật thay đổi theo bước trước, trạng thái phải chứa thêm thông tin; không tái sử dụng công thức cũ một cách máy móc.

## 2. Cài đặt bottom-up có kiểm tra biên
```python
def stair_ways(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError('invalid n')
    previous, current = 1, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous

assert stair_ways(0) == 1
assert stair_ways(4) == 5
assert stair_ways(6) == 13
```
Theo mô hình phép toán số học hằng số: O(n) thời gian, O(1) số biến phụ. Với số nguyên rất lớn, chi phí bit và bộ nhớ số nguyên tăng theo kích thước giá trị, nên mô hình này là một giả định phân tích.

## 3. Phân biệt kỹ thuật
Chia để trị nhấn mạnh chia, giải và kết hợp; quy hoạch động lưu lời giải bài toán con hữu ích để tránh tính lại. Tham lam cần tính chất bảo đảm quyết định cục bộ dẫn tới tối ưu. Với mệnh giá 1,3,4 và tiền 6, lấy 4 trước cho ba đồng, còn 3+3 chỉ hai đồng.

## 4. Bài tập có lời giải định hướng
Lập bảng số đồng ít nhất cho tiền từ 0 tới 6 với các mệnh giá trên. Đặt dp[0]=0; trạng thái chưa đạt dùng vô cực; xét mọi đồng không vượt số tiền và lấy min(dp[s-coin]+1). Kết quả cho 6 là 2. Kiểm tra riêng trường hợp không tạo được số tiền nếu bỏ mệnh giá 1.

## Bài tập vận dụng bổ sung
Lập bảng ways từ 0 tới 6 và viết phiên bản dùng hai biến. Tự kiểm tra giả định mỗi bước chỉ là 1 hoặc 2, không áp công thức cho yêu cầu khác.

## Hướng giải bài tập bổ sung
ways[5]=8, ways[6]=13. Nêu rõ trạng thái 0 biểu diễn một cách không thực hiện bước nào, giúp công thức nhất quán.

## Câu hỏi tự kiểm tra
1. Thành phần nào cần định nghĩa trong quy hoạch động?
2. Merge sort minh họa kỹ thuật nào?
3. Với ways[0]=1, ways[1]=1 và bước 1 hoặc 2, ways[4] là gì?
4. Tham lam lấy đồng lớn nhất có tối ưu cho mọi hệ mệnh giá không?
5. Nếu chỉ cần hai trạng thái trước, có thể tối ưu gì?

## Gợi ý đáp án và điểm cần nhớ
- Trạng thái và công thức chuyển. Trạng thái, cơ sở và thứ tự tính quyết định lời giải.
- Chia để trị. Thuật toán chia, giải các nửa và trộn.
- 5. Dãy tiếp theo là 2,3,5.
- Không. Hệ 1,3,4 với số tiền 6 là một phản ví dụ.
- Bộ nhớ lưu bảng. Có thể lưu hai giá trị thay cho toàn bảng.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://opendatastructures.org/
- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/heapq.html
