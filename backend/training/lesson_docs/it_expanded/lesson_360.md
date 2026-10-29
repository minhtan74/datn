## Mục tiêu
Biểu diễn đồ thị và chọn chiến lược duyệt đúng mục tiêu.

## Kiến thức trọng tâm
Đồ thị gồm đỉnh và cạnh, có thể có hướng hoặc vô hướng. Danh sách kề lưu các láng giềng của mỗi đỉnh; ma trận kề dùng ô biểu diễn quan hệ từng cặp đỉnh. Với đồ thị thưa, danh sách kề thường tiết kiệm bộ nhớ hơn ma trận O(V²).

BFS dùng queue để duyệt theo lớp. Trong đồ thị không trọng số, BFS tìm số cạnh ít nhất từ đỉnh xuất phát tới các đỉnh đến được. DFS đi sâu theo nhánh, có thể dùng đệ quy hoặc stack. Cả hai cần quản lý đã thăm để tránh lặp với chu trình.

Với danh sách kề và cách triển khai chuẩn, duyệt toàn phần liên quan có chi phí O(V+E). Một lần duyệt từ s không bảo đảm thăm hết đồ thị không liên thông. Để duyệt toàn bộ, có thể bắt đầu lại ở đỉnh chưa thăm. BFS thông thường không tự giải đường đi ngắn nhất theo trọng số tùy ý.

## Ví dụ có hướng dẫn
Đồ thị A-B, A-C, B-D, C-D. BFS từ A phát hiện B,C trước D; đường đi tới D có hai cạnh. Thứ tự giữa B và C phụ thuộc thứ tự danh sách kề.

## Bài tập thực hành
Viết danh sách kề, vẽ vết queue BFS và stack DFS. Thêm đỉnh E cô lập rồi kiểm tra một lần BFS từ A có thăm E không.

## Gợi ý tự kiểm tra
Không thăm E nếu không có đường nối. Đánh dấu phát hiện phù hợp để tránh đưa cùng đỉnh vào queue lặp lại nhiều lần.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html