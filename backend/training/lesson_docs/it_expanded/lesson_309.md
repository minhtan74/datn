Mục tiêu: xác định điều kiện áp dụng và so sánh chi phí tìm kiếm.

Tìm kiếm tuyến tính kiểm tra lần lượt các phần tử; dùng được với dữ liệu chưa sắp xếp. Trường hợp xấu nhất phải xét n phần tử nên là O(n). Kết quả tìm kiếm nên quy ước rõ vị trí tìm thấy hoặc dấu hiệu không có dữ liệu.

Tìm kiếm nhị phân trên mảng đã sắp xếp so sánh mục tiêu với phần tử giữa rồi bỏ một nửa khoảng tìm kiếm. Số bước so sánh trong trường hợp xấu nhất là O(log n). Điều kiện sắp xếp phải phù hợp phép so sánh; không được áp dụng trực tiếp lên một mảng tùy ý chưa sắp xếp.

Trong biến thể dùng hai biên đóng, nếu mục tiêu nhỏ hơn phần tử giữa thì cập nhật biên phải thành mid-1; nếu lớn hơn thì biên trái thành mid+1. Cần bảo đảm khoảng tìm kiếm giảm sau mỗi bước để tránh vòng lặp vô hạn.

Tự luyện: tìm 13 trong [2,5,8,13,21,34,55]. Ghi hai biên và phần tử giữa ở từng bước. Thử tiếp một giá trị không có trong mảng.

Video tham khảo (tiếng Anh): What is binary search — mycodeschool.
Nguồn gốc: https://www.youtube.com/watch?v=j5uXyPJ0Pew
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.