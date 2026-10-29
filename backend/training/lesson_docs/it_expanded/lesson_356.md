## Mục tiêu
Xác định trường hợp cơ sở, bước tiến triển và chi phí của lời giải đệ quy.

## Kiến thức trọng tâm
Hàm đệ quy gọi lại chính nó để giải bài toán nhỏ hơn. Cần có trường hợp cơ sở và đại lượng giảm tới trường hợp đó. Với giai thừa n không âm: 0! = 1 và n! = n*(n-1)!. Nếu không kiểm tra miền đầu vào, lời gọi với số âm có thể không bao giờ tới cơ sở.

Mỗi lời gọi lưu trạng thái trên ngăn xếp lời gọi. Tính giai thừa theo cách trên có n bước và độ sâu O(n). Đệ quy không tự làm thuật toán nhanh hơn; phiên bản lặp có thể giảm bộ nhớ phụ.

Một bài toán chia thành nhiều nhánh có thể lặp lại tính toán. Fibonacci đệ quy trực tiếp tính nhiều lần cùng giá trị; memoization lưu lời giải bài toán con để tái sử dụng. Phải phân biệt số lời gọi với độ sâu ngăn xếp. Trong thực tế, giới hạn ngăn xếp có thể làm đệ quy sâu thất bại.

## Ví dụ có hướng dẫn
factorial(3) chờ 3*factorial(2), tiếp tục tới factorial(0)=1, rồi trả ngược 1,2,6. Độ sâu tăng theo n dù mỗi lời gọi chỉ làm ít phép toán.

## Bài tập thực hành
Viết giả mã giai thừa có kiểm tra n>=0. Vẽ cây lời gọi Fibonacci(5) và đánh dấu các giá trị được tính lại; đề xuất cách lưu kết quả.

## Gợi ý tự kiểm tra
Có cơ sở, miền đầu vào và bước tiến triển rõ ràng. Memoization tránh tính lại, còn vòng lặp có thể tránh ngăn xếp sâu cho giai thừa.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html