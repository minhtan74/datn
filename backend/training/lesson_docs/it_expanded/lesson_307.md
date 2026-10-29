Mục tiêu: chọn cấu trúc phù hợp với thao tác truy cập, tìm kiếm và cập nhật.

Mảng lưu các phần tử ở vùng nhớ liên tiếp trong mô hình cơ bản. Truy cập theo chỉ số có thời gian O(1), nhưng tìm một giá trị trong mảng chưa sắp xếp thường cần O(n). Chèn vào giữa mảng có thể phải dịch chuyển nhiều phần tử nên thường là O(n).

Danh sách liên kết gồm các nút, mỗi nút chứa dữ liệu và liên kết. Danh sách đơn có liên kết tới nút sau; muốn tới phần tử thứ k phải đi từ đầu nên thường O(k). Nếu đã biết nút đứng trước vị trí cần chèn, việc nối một nút mới có thể O(1), chưa tính thời gian tìm vị trí.

Không có cấu trúc luôn tốt nhất: mảng phù hợp truy cập ngẫu nhiên và thường có tính cục bộ bộ nhớ tốt; danh sách liên kết phù hợp một số thao tác nối/tách khi đã có vị trí. Big-O mô tả tốc độ tăng chi phí, không phải số giây chính xác.

Tự luyện: mô phỏng chèn X vào giữa [A,B,C,D], rồi mô phỏng thao tác đó với danh sách liên kết. Đếm thao tác phải thay đổi.

Video tham khảo (tiếng Anh): Data Structures: Arrays vs Linked Lists — mycodeschool.
Nguồn gốc: https://www.youtube.com/watch?v=lC-yYCOnN8Q
Video minh họa một phần nội dung; đọc kết hợp bài học và bài tập tiếng Việt phía trên.