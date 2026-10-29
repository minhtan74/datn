## Mục tiêu
Phân biệt chia để trị với lưu trạng thái bài toán con.

## Kiến thức trọng tâm
Chia để trị chia bài toán thành các phần nhỏ, giải rồi kết hợp; merge sort là ví dụ. Quy hoạch động thường phù hợp khi có các bài toán con chồng lặp và cấu trúc tối ưu thích hợp. Không phải cứ có đệ quy là cần quy hoạch động.

Một lời giải quy hoạch động cần định nghĩa trạng thái, chuyển trạng thái, trường hợp cơ sở và thứ tự tính. Với số cách bước lên n bậc, mỗi bước 1 hoặc 2 bậc, có thể đặt ways[0]=1, ways[1]=1 và ways[n]=ways[n-1]+ways[n-2]. Bộ nhớ có thể giảm nếu chỉ cần hai trạng thái trước.

Tham lam chọn quyết định cục bộ, nhưng cần chứng minh cho bài toán cụ thể. Chẳng hạn đổi tiền với mệnh giá tùy ý không bảo đảm thuật toán luôn lấy đồng lớn nhất sẽ dùng ít đồng nhất. Bắt đầu từ mô hình bài toán và ví dụ phản chứng, không chọn kỹ thuật theo tên gọi hấp dẫn.

## Ví dụ có hướng dẫn
Bốn bậc có ways[2]=2, ways[3]=3, ways[4]=5. Đổi 6 với mệnh giá 1,3,4: tham lam 4+1+1 dùng ba đồng nhưng 3+3 dùng hai.

## Bài tập thực hành
Lập bảng ways từ 0 tới 6 và viết phiên bản dùng hai biến. Tự kiểm tra giả định mỗi bước chỉ là 1 hoặc 2, không áp công thức cho yêu cầu khác.

## Gợi ý tự kiểm tra
ways[5]=8, ways[6]=13. Nêu rõ trạng thái 0 biểu diễn một cách không thực hiện bước nào, giúp công thức nhất quán.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html