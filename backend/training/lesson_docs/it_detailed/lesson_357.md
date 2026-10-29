## Vị trí bài học trong khóa
- Khóa học: Cấu trúc dữ liệu và giải thuật cơ bản.
- Chương 4: Tra cứu và dữ liệu có thứ tự.
- Các bài trong chương: Bảng băm, tập hợp và ánh xạ; Cây nhị phân và cây tìm kiếm nhị phân.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Dùng ánh xạ đếm tần suất và giải thích va chạm băm.

## Kiến thức nền
Bảng băm biến khóa thành vị trí tra cứu thông qua hàm băm. Map lưu cặp khóa–giá trị; set lưu các phần tử phân biệt. Khi các khóa khác nhau có cùng vị trí băm, cấu trúc phải xử lý va chạm, chẳng hạn nối chuỗi hoặc địa chỉ mở.

Tra cứu, chèn và xóa thường có thời gian kỳ vọng O(1) trong điều kiện thích hợp; không phải bảo đảm xấu nhất O(1). Số lượng phần tử, số ô và chất lượng hàm băm ảnh hưởng hiệu năng. Khóa dùng trong bảng băm cần có tính băm và so sánh nhất quán theo ngôn ngữ.

Đếm từ bằng map tăng bộ đếm mỗi khi gặp từ. Nếu chuẩn hóa chữ hoa/thường, phải nêu quy tắc trước. Dùng set loại bản sao nhưng không tự tạo thứ tự sắp xếp. Nếu bài toán cần duyệt tăng dần, cần bước sắp xếp hoặc cấu trúc có thứ tự thích hợp.

## 1. Từ khóa tới vị trí lưu
Hàm băm và số ô bảng quyết định vị trí khởi đầu của khóa. Va chạm không có nghĩa hai khóa bằng nhau. Cấu trúc vẫn cần phép so sánh khóa đúng. Hệ số tải là số phần tử chia số ô theo mô hình bảng; khi tăng quá mức có thể cần mở rộng và băm lại tùy triển khai.

## 2. Bộ đếm có quy tắc đầu vào rõ
```python
def frequencies(words, ignore_case=False):
    result = {}
    for word in words:
        key = word.casefold() if ignore_case else word
        result[key] = result.get(key, 0) + 1
    return result

assert frequencies(['An', 'an']) == {'An': 1, 'an': 1}
assert frequencies(['An', 'an'], True) == {'an': 2}
```
casefold là một lựa chọn xử lý chữ hoa/thường, không tự giải quyết mọi khác biệt biểu diễn Unicode. Nếu ứng dụng cần chuẩn hóa NFC, phải nêu thêm bước đó và viết test tương ứng.

## 3. Độ phức tạp và giới hạn
Trong điều kiện băm tốt, n cập nhật có thời gian kỳ vọng O(n), bộ nhớ O(k) cho k khóa khác nhau, chưa tính độ dài khóa và chi phí băm chuỗi. Không khẳng định chuỗi rất dài luôn được xử lý cùng chi phí như một ký tự.
Set có thể kiểm tra trùng, nhưng sau khi loại bản sao cần quyết định thứ tự đầu ra. Không dựa vào một lần chạy để suy ra set có thứ tự sắp xếp.

## 4. Bài tập và đáp án
Với An,Bình,An,an và ignore_case=True, kết quả là an:3,bình:1. Hãy thêm báo cáo giảm dần theo tần suất rồi tăng theo tên khi hòa; bước sắp xếp k khóa có chi phí thêm O(k log k). Đối chiếu tổng đếm với bốn đầu vào để phát hiện mất hoặc nhân đôi dữ liệu.

## Bài tập vận dụng bổ sung
Viết bộ đếm ký tự và bài toán kiểm tra có phần tử trùng. Kiểm thử dữ liệu rỗng, tất cả giống nhau và phân biệt chữ A với a theo quy tắc đã chọn.

## Hướng giải bài tập bổ sung
Dùng set để phát hiện trùng, map để lưu tần suất. Giải thích thời gian kỳ vọng O(n), bộ nhớ O(k) với k khóa phân biệt.

## Câu hỏi tự kiểm tra
1. Map lưu loại dữ liệu nào?
2. Set dùng chủ yếu để biểu diễn gì?
3. Va chạm băm xảy ra khi nào?
4. O(1) của bảng băm thường cần hiểu ra sao?
5. Với a,b,a,a thì tần suất a là bao nhiêu?

## Gợi ý đáp án và điểm cần nhớ
- Cặp khóa–giá trị. Map liên kết một khóa với một giá trị.
- Các phần tử phân biệt. Set biểu diễn tính thuộc tập và tính duy nhất.
- Khóa khác nhau ánh xạ tới cùng vị trí. Cần chiến lược xử lý nhiều khóa chung vị trí.
- Hiệu năng kỳ vọng với điều kiện phù hợp. Phân bố khóa và triển khai ảnh hưởng chi phí.
- 3. Map tăng bộ đếm cho mỗi lần xuất hiện của a.

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
