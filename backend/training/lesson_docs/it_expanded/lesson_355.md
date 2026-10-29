## Mục tiêu
Phân tích chi phí theo kích thước đầu vào và nêu điều kiện để thuật toán đúng.

## Kiến thức trọng tâm
Kích thước đầu vào n cần được xác định trước khi phân tích. Một vòng lặp thăm n phần tử thường O(n); hai vòng lặp lồng nhau, mỗi vòng n bước, thường O(n²). Hai vòng nối tiếp có chi phí O(n)+O(n), vẫn là O(n). Vòng lặp chia đôi miền mỗi bước thường gợi ý O(log n).

Phân biệt trường hợp tốt nhất, xấu nhất và trung bình. Big-O là chặn trên tiệm cận; hằng số, kiểu dữ liệu và môi trường vẫn ảnh hưởng thời gian chạy thực tế. Bộ nhớ phụ phân tích riêng với bộ nhớ chứa đầu vào.

Bất biến là mệnh đề đúng tại các mốc trong vòng lặp, giúp lập luận đúng đắn. Khi tìm số lớn nhất, sau k bước, biến best phải chứa giá trị lớn nhất trong k phần tử đã xét. Test rỗng, một phần tử, trùng lặp và biên giúp tìm lỗi; một vài test qua chưa chứng minh đúng với mọi đầu vào.

## Ví dụ có hướng dẫn
Duyệt [3,1,5]: khởi tạo best=3, sau phần tử 1 vẫn là 3, sau 5 là 5. Nếu khởi tạo best=0 mà mọi số âm, thuật toán có thể trả kết quả không tồn tại trong mảng.

## Bài tập thực hành
Phân tích hai vòng nối tiếp và hai vòng lồng nhau. Viết hàm tìm max có quy ước khi đầu vào rỗng; thử [-5,-2,-9], [7], [2,2].

## Gợi ý tự kiểm tra
Chi phí lần lượt O(n) và O(n²). Với mảng rỗng phải trả dấu hiệu không có kết quả hoặc báo lỗi đã quy định, không tự trả 0.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html