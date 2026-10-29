Mục tiêu: mô phỏng LIFO, FIFO và chọn stack hoặc queue đúng tình huống.

Stack là ngăn xếp theo nguyên tắc LIFO: phần tử vào sau được lấy trước. push thêm vào đỉnh, pop lấy khỏi đỉnh, peek xem đỉnh mà không xóa. Với triển khai phù hợp, các thao tác cơ bản có thể O(1). Gọi pop trên stack rỗng cần được xử lý theo quy ước của chương trình.

Queue là hàng đợi theo nguyên tắc FIFO: phần tử vào trước được lấy trước. enqueue thêm vào cuối, dequeue lấy ở đầu. Có thể dùng danh sách liên kết hoặc bộ đệm vòng để tránh dịch toàn bộ phần tử mỗi lần lấy đầu.

Stack hữu ích cho kiểm tra dấu ngoặc và quay lui; queue hữu ích cho xử lý công việc theo thứ tự đến và duyệt BFS. Cấu trúc mô tả quy tắc lấy dữ liệu, không đồng nghĩa với một kiểu lưu bộ nhớ duy nhất.

Tự luyện: thực hiện push(A), push(B), pop(), push(C), pop() trên stack. Làm chuỗi tương tự với enqueue và dequeue rồi so sánh kết quả.

Video tham khảo (tiếng Anh): Data Structures: Stacks and Queues — HackerRank.
Nguồn gốc: https://www.youtube.com/watch?v=wjI1WNcIntg
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.