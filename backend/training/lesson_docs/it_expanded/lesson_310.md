Mục tiêu: đọc Big-O và mô tả hai thuật toán sắp xếp cơ bản.

Big-O mô tả một chặn trên tiệm cận của chi phí theo kích thước đầu vào. O(n) tăng tuyến tính, O(n²) tăng theo bình phương. Khi so sánh cần cùng loại chi phí và trường hợp phân tích; không suy ra thời gian thực tế chỉ từ Big-O.

Selection sort chọn phần tử nhỏ nhất trong phần chưa sắp xếp rồi đưa về đầu phần đó. Thuật toán thường có O(n²) phép so sánh và có thể thực hiện tại chỗ. Merge sort chia dữ liệu, sắp xếp các nửa rồi trộn hai dãy đã có thứ tự; thời gian thường O(n log n).

Bản merge sort thông thường trên mảng cần O(n) bộ nhớ phụ. Một thuật toán ổn định giữ thứ tự tương đối của các phần tử có khóa bằng nhau. Ổn định và tại chỗ là hai thuộc tính khác nhau, không phải tên gọi của độ phức tạp thời gian.

Tự luyện: mô phỏng hai bước selection sort cho [4,2,5,1]. Trộn [1,4,7] với [2,3,8]. Với bản ghi cùng điểm, giải thích vì sao giữ thứ tự ban đầu có thể hữu ích.

Video tham khảo (tiếng Anh): Merge sort algorithm — mycodeschool.
Nguồn gốc: https://www.youtube.com/watch?v=TzeBrDU-JaY
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.