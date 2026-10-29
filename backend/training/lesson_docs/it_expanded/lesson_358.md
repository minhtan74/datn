## Mục tiêu
Phân biệt cây nhị phân với BST; mô phỏng tìm kiếm và duyệt inorder.

## Kiến thức trọng tâm
Cây có các nút và quan hệ cha–con. Cây nhị phân có tối đa hai con tại mỗi nút. BST bổ sung quy tắc thứ tự; trong phiên bản không có khóa trùng, mọi khóa bên trái nhỏ hơn nút và bên phải lớn hơn nút. Có hai con không đủ để kết luận là BST.

Tìm kiếm so sánh mục tiêu với khóa nút hiện tại rồi chọn một nhánh. Chi phí phụ thuộc chiều cao h, thường O(h). Nếu cây cân đối thì h là O(log n); nếu chèn khóa tăng dần vào BST không tự cân bằng, cây có thể lệch và tìm kiếm tới O(n).

Duyệt inorder đi trái, nút, phải; với BST hợp lệ cho dãy tăng dần. Kiểm tra BST phải xét ràng buộc toàn cây con, không chỉ hai nút con trực tiếp. Bài này giới thiệu nguyên lý; thuật toán tự cân bằng như AVL không thuộc yêu cầu thực hành bắt buộc.

## Ví dụ có hướng dẫn
Chèn 4,2,6,1,3 tạo gốc 4, nhánh trái 2 với con 1 và 3, nhánh phải 6. Inorder thu 1,2,3,4,6. Tìm 3 đi qua 4 rồi 2 rồi 3.

## Bài tập thực hành
Vẽ BST khi chèn 1,2,3,4 và so sánh chiều cao với thứ tự 3,1,4,2. Viết truy vết tìm một khóa không tồn tại.

## Gợi ý tự kiểm tra
Cây chèn tăng dần có thể thành chuỗi. Không ghi mọi thao tác BST là O(log n) nếu chưa có điều kiện về chiều cao.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html