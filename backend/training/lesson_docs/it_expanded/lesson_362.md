## Mục tiêu
Kết hợp lựa chọn cấu trúc, kiểm thử và phân tích chi phí trong một chương trình nhỏ.

## Kiến thức trọng tâm
Thiết kế một bộ tra cứu tên và tần suất xuất hiện. Yêu cầu gồm thêm dữ liệu, đếm, tìm và xuất báo cáo theo thứ tự. Tách quy tắc chuẩn hóa khỏi cấu trúc lưu: chẳng hạn có gộp chữ hoa/thường hay không phải được quyết định trước.

Map phù hợp cập nhật tần suất, set phù hợp kiểm tra duy nhất, danh sách sắp xếp phù hợp xuất thứ tự và tìm nhị phân trên bản dữ liệu đã sắp. Không tự dùng tìm nhị phân sau khi thêm dữ liệu mà không duy trì thứ tự. Nếu chỉ cần top k liên tục, cân nhắc heap và giải thích chi phí.

Sản phẩm cần tài liệu đầu vào/đầu ra, test và nhận xét Big-O cho từng chức năng. Tách dữ liệu rỗng, trùng lặp, Unicode và quy mô lớn. Benchmark phải cùng môi trường và cùng dữ liệu; không suy ra thuật toán đúng chỉ vì chạy nhanh.

## Ví dụ có hướng dẫn
Đầu vào An,Bình,An cho báo cáo An:2,Bình:1. Nếu không gộp hoa/thường, an và An là hai khóa khác nhau; nếu gộp phải nêu cách chuẩn hóa.

## Bài tập thực hành
Viết chương trình nhận một danh sách từ; xuất số từ phân biệt, tần suất và danh sách theo tên. Nộp ít nhất sáu test và phân tích thời gian cập nhật, sắp xếp, tra cứu.

## Gợi ý tự kiểm tra
Kết quả đếm phải khớp tổng số phần tử. Với k khóa, xuất báo cáo sắp xếp thường O(k log k). Giữ lại test hồi quy khi sửa xử lý Unicode.

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.

## Đọc thêm
https://opendatastructures.org/
https://docs.python.org/3/tutorial/datastructures.html
https://docs.python.org/3/library/heapq.html