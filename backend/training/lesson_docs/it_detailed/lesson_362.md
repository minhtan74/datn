## Vị trí bài học trong khóa
- Khóa học: Cấu trúc dữ liệu và giải thuật cơ bản.
- Chương 6: Thiết kế lời giải và thực hành.
- Các bài trong chương: Chia để trị và quy hoạch động nhập môn; Dự án nhỏ: bộ tra cứu và thống kê dữ liệu.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Kết hợp lựa chọn cấu trúc, kiểm thử và phân tích chi phí trong một chương trình nhỏ.

## Kiến thức nền
Thiết kế một bộ tra cứu tên và tần suất xuất hiện. Yêu cầu gồm thêm dữ liệu, đếm, tìm và xuất báo cáo theo thứ tự. Tách quy tắc chuẩn hóa khỏi cấu trúc lưu: chẳng hạn có gộp chữ hoa/thường hay không phải được quyết định trước.

Map phù hợp cập nhật tần suất, set phù hợp kiểm tra duy nhất, danh sách sắp xếp phù hợp xuất thứ tự và tìm nhị phân trên bản dữ liệu đã sắp. Không tự dùng tìm nhị phân sau khi thêm dữ liệu mà không duy trì thứ tự. Nếu chỉ cần top k liên tục, cân nhắc heap và giải thích chi phí.

Sản phẩm cần tài liệu đầu vào/đầu ra, test và nhận xét Big-O cho từng chức năng. Tách dữ liệu rỗng, trùng lặp, Unicode và quy mô lớn. Benchmark phải cùng môi trường và cùng dữ liệu; không suy ra thuật toán đúng chỉ vì chạy nhanh.

## 1. Đặc tả sản phẩm
Đầu vào là danh sách tên; đầu ra gồm số bản ghi, số tên phân biệt, tần suất và báo cáo có thứ tự. Chọn chính sách bỏ khoảng trắng đầu/cuối và gộp hoa/thường rõ ràng. Nếu giữ nguyên tên để hiển thị, có thể lưu riêng khóa chuẩn hóa và nhãn hiển thị.

## 2. Chương trình mẫu có thể chạy
```python
def build_report(names):
    counts = {}
    for name in names:
        key = name.strip().casefold()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))

assert build_report(['An', ' Bình ', 'an', '']) == [('an', 2), ('bình', 1)]
assert build_report([]) == []
```
Theo hợp đồng mẫu, chuỗi rỗng bị bỏ qua nên tổng tần suất bằng số mục hợp lệ, không phải số mục thô. Nếu đề bài muốn giữ mục rỗng phải thay cả cài đặt và test.

## 3. Phân tích và nâng cấp
Với n mục và k khóa khác nhau, đếm thường O(n) kỳ vọng theo mô hình băm; sắp xếp O(k log k), chưa tính độ dài chuỗi. Giữ dữ liệu nguồn nếu cần truy vết lỗi chuẩn hóa. Nếu báo cáo lấy top k liên tục trên luồng lớn, đề xuất heap và so sánh với sắp xếp toàn bộ.

## 4. Hồ sơ nghiệm thu
Nộp mã nguồn, cách chạy, hợp đồng chuẩn hóa, tối thiểu sáu test và phân tích Big-O. Test gồm rỗng, tất cả trùng, khoảng trắng, chữ hoa/thường, Unicode và hòa tần suất. Giữ thứ tự thứ hai theo tên để báo cáo xác định. Không chứng minh đúng bằng một ảnh chụp đầu ra; phải có đầu vào và kỳ vọng đối chiếu.

## Bài tập vận dụng bổ sung
Viết chương trình nhận một danh sách từ; xuất số từ phân biệt, tần suất và danh sách theo tên. Nộp ít nhất sáu test và phân tích thời gian cập nhật, sắp xếp, tra cứu.

## Hướng giải bài tập bổ sung
Kết quả đếm phải khớp tổng số phần tử. Với k khóa, xuất báo cáo sắp xếp thường O(k log k). Giữ lại test hồi quy khi sửa xử lý Unicode.

## Câu hỏi tự kiểm tra
1. Cấu trúc nào phù hợp đếm tần suất theo khóa?
2. Sau khi thêm phần tử làm mất thứ tự, trước tìm nhị phân cần gì?
3. Tổng các tần suất phải bằng gì?
4. Báo cáo sắp xếp k khóa thường cần bao nhiêu thời gian với thuật toán O(k log k)?
5. Benchmark nhanh có tự chứng minh chương trình đúng không?

## Gợi ý đáp án và điểm cần nhớ
- Map. Map liên kết mỗi khóa với bộ đếm.
- Khôi phục hoặc duy trì thứ tự. Tìm nhị phân yêu cầu thứ tự phù hợp.
- Tổng số phần tử đầu vào đã tính. Mỗi phần tử đầu vào đóng góp một lần vào một bộ đếm.
- O(k log k). Chi phí sắp xếp áp dụng cho số khóa phân biệt k.
- Không. Đúng đắn cần đối chiếu kết quả và yêu cầu.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://opendatastructures.org/
- https://docs.python.org/3/tutorial/datastructures.html
- https://docs.python.org/3/library/heapq.html
