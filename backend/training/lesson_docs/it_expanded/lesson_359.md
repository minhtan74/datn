## Mục tiêu
Mô phỏng min-heap và phân biệt ưu tiên với FIFO.

## Kiến thức trọng tâm
Hàng đợi ưu tiên lấy phần tử theo độ ưu tiên, không nhất thiết theo thứ tự đến. Min-heap nhị phân thường biểu diễn bằng mảng và hình dạng cây nhị phân hoàn chỉnh; mỗi nút cha có khóa không lớn hơn các con. Phần tử nhỏ nhất ở gốc nhưng toàn bộ mảng chưa được sắp xếp.

Với chỉ số bắt đầu từ 0, con trái của i ở 2*i+1, con phải ở 2*i+2. Chèn phần tử vào cuối rồi đưa lên để khôi phục tính heap; lấy min thay gốc bằng phần tử cuối rồi đưa xuống. Chiều cao O(log n) dẫn tới chi phí chèn/lấy min O(log n); xem min O(1).

Heap hữu ích khi liên tục cần công việc ưu tiên hoặc k phần tử nổi bật. Nếu nhiều việc bằng ưu tiên và cần giữ thứ tự đến, bổ sung bộ đếm thứ tự. Không dùng heap để thay thế mọi yêu cầu tìm kiếm theo khóa tùy ý.

## Ví dụ có hướng dẫn
Chèn 5,2,8 vào min-heap, gốc là 2. Lấy min trả 2 rồi heap mới có gốc 5. Thứ tự mảng biểu diễn không phải dãy đã sắp xếp đầy đủ.

## Bài tập thực hành
Mô phỏng thêm 1 vào heap [2,5,8]. Lập lịch ba công việc có ưu tiên khác nhau và giải thích quy ước khi bằng ưu tiên.

## Gợi ý tự kiểm tra
Kết quả lấy lần lượt là 1,2,5,8 nếu không thêm phần tử khác. Nêu rõ số ưu tiên nhỏ hay lớn được phục vụ trước.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html