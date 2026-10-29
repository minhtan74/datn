## Mục tiêu
Dùng ánh xạ đếm tần suất và giải thích va chạm băm.

## Kiến thức trọng tâm
Bảng băm biến khóa thành vị trí tra cứu thông qua hàm băm. Map lưu cặp khóa–giá trị; set lưu các phần tử phân biệt. Khi các khóa khác nhau có cùng vị trí băm, cấu trúc phải xử lý va chạm, chẳng hạn nối chuỗi hoặc địa chỉ mở.

Tra cứu, chèn và xóa thường có thời gian kỳ vọng O(1) trong điều kiện thích hợp; không phải bảo đảm xấu nhất O(1). Số lượng phần tử, số ô và chất lượng hàm băm ảnh hưởng hiệu năng. Khóa dùng trong bảng băm cần có tính băm và so sánh nhất quán theo ngôn ngữ.

Đếm từ bằng map tăng bộ đếm mỗi khi gặp từ. Nếu chuẩn hóa chữ hoa/thường, phải nêu quy tắc trước. Dùng set loại bản sao nhưng không tự tạo thứ tự sắp xếp. Nếu bài toán cần duyệt tăng dần, cần bước sắp xếp hoặc cấu trúc có thứ tự thích hợp.

## Ví dụ có hướng dẫn
Với [a,b,a,c,b,a], lần lượt cập nhật count[x]=count.get(x,0)+1, được a:3,b:2,c:1. Số khóa phân biệt là 3, khác tổng số phần tử 6.

## Bài tập thực hành
Viết bộ đếm ký tự và bài toán kiểm tra có phần tử trùng. Kiểm thử dữ liệu rỗng, tất cả giống nhau và phân biệt chữ A với a theo quy tắc đã chọn.

## Gợi ý tự kiểm tra
Dùng set để phát hiện trùng, map để lưu tần suất. Giải thích thời gian kỳ vọng O(n), bộ nhớ O(k) với k khóa phân biệt.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html