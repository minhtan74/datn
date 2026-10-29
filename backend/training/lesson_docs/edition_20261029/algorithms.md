# Cấu trúc dữ liệu và giải thuật — ví dụ và kiểm tra bất biến

Các ví dụ Python chạy bằng thư viện chuẩn. Độ phức tạp phải gắn với kích thước đầu vào và giả định; thời gian một lần chạy không đủ chứng minh Big-O. Tự kiểm tra dữ liệu rỗng, trùng và giá trị biên trước khi tối ưu.

## Mảng và danh sách liên kết
**Tình huống:** chọn cấu trúc chỉ vì nghe “thêm/xóa nhanh”. Truy cập theo chỉ số ở mảng khác việc đi theo liên kết. Danh sách liên kết có thể thay đổi liên kết nhanh khi đã biết nút/vị trí phù hợp, nhưng tìm vị trí vẫn có chi phí; bộ nhớ và locality cũng quan trọng.
```python
values = [10, 20, 30]
assert values[0] == 10
assert values[-1] == 30
```
**Tự luyện:** mô tả thêm ở đầu, tìm theo giá trị và đọc phần tử thứ k. **Hướng giải:** tách chi phí tìm vị trí khỏi chi phí cập nhật; đừng coi Python list là danh sách liên kết chỉ vì tên “list”.

## Ngăn xếp và hàng đợi
**Tình huống:** hàng xử lý yêu cầu phải giữ thứ tự đến. Queue là FIFO, stack là LIFO; chọn theo hành vi cần bảo đảm.
```python
from collections import deque
queue = deque(["A", "B"])
assert queue.popleft() == "A"
stack = ["A", "B"]
assert stack.pop() == "B"
```
**Tự luyện:** xử lý khi rỗng và mô tả undo hai thao tác. **Hướng giải:** kiểm tra rỗng hoặc xử lý lỗi theo hợp đồng. Dùng list.pop(0) cho hàng dài phải dịch phần tử; deque phù hợp thao tác hai đầu trong bài đơn luồng này, không tự thay thế cơ chế phối hợp nhiều producer/consumer.

## Tìm kiếm tuyến tính và nhị phân
**Tình huống:** tìm nhị phân trả sai vì dữ liệu chưa sắp xếp. Binary search cần thứ tự và bất biến rõ ràng; với dữ liệu trùng, phải quy định cần bất kỳ vị trí hay vị trí đầu tiên.
```python
from bisect import bisect_left
values = [1, 3, 3, 8]
i = bisect_left(values, 3)
assert i == 1
j = bisect_left(values, 5)
assert j == 3 and values[j] != 5
```
**Tự luyện:** tìm 0, 1, 3, 9 và trên mảng rỗng. **Hướng giải:** bisect trả vị trí chèn, không tự chứng minh giá trị tồn tại; kiểm tra chỉ số trong miền và phần tử bằng đích trước khi kết luận tìm thấy.

## Sắp xếp và độ phức tạp
**Tình huống:** muốn sắp xếp sản phẩm theo giá rồi tên. Xác định khóa và việc có được sửa dữ liệu đầu vào hay không.
```python
items = [(2, "B"), (1, "C"), (1, "A")]
ordered = sorted(items, key=lambda item: (item[0], item[1]))
assert ordered == [(1, "A"), (1, "C"), (2, "B")]
assert items[0] == (2, "B")
```
**Tự luyện:** dữ liệu đã tăng, giảm, trùng và rỗng. **Hướng giải:** kiểm tra bảo toàn số phần tử và tính có thứ tự. Với thuật toán tự viết, nêu worst/average/best khi cần; không kết luận O(n) chỉ từ một input đã sắp xếp.

## Big-O, bất biến và kiểm tra thuật toán
**Tình huống:** hai vòng lặp không phải lúc nào cũng O(n²). Hai vòng nối tiếp mỗi vòng n bước cho O(n); vòng lồng mỗi vòng n bước thường cho O(n²) theo mô hình công việc mỗi bước hằng số.

**Tự luyện:** đếm số phép so sánh của tìm tuyến tính trên đầu, giữa, cuối và không tìm thấy. **Hướng giải:** nêu n là số phần tử, không phải “độ dài code”. Bất biến giúp chứng minh: sau k phần tử đã duyệt, tổng tạm bằng tổng đúng k phần tử đó. Kiểm thử có thể tìm phản ví dụ nhưng không thay thế mọi chứng minh tổng quát.

## Đệ quy và ngăn xếp lời gọi
**Tình huống:** thiếu điều kiện dừng hoặc bài toán không nhỏ đi. Mỗi bước đệ quy cần tiến tới base case và có hợp đồng rõ.
```python
def factorial(n):
    if n < 0:
        raise ValueError("n không âm")
    return 1 if n == 0 else n * factorial(n - 1)

assert factorial(0) == 1
assert factorial(5) == 120
```
**Tự luyện:** giải thích cây lời gọi cho n=3. **Hướng giải:** n giảm một ở mỗi bước; với n lớn cần xét giới hạn stack và dùng vòng lặp khi phù hợp. Đệ quy không mặc nhiên nhanh hơn vòng lặp; phải tính cả số lời gọi và bộ nhớ.

## Bảng băm, tập hợp và ánh xạ
**Tình huống:** đếm từ bằng cách quét danh sách cho từng từ tốn công lặp. Map lưu khóa→giá trị; set kiểm tra thành viên, không biểu diễn số lần xuất hiện.
```python
from collections import Counter
counts = Counter(["a", "b", "a"])
assert counts["a"] == 2
assert len(set([1, 1, 2])) == 2
```
**Tự luyện:** từ hoa/thường và dấu câu cần được chuẩn hóa thế nào? **Hướng giải:** xác định quy tắc trước khi đếm, giữ dữ liệu gốc nếu cần giải thích kết quả. Chi phí tra bảng băm thường được mô tả theo kỳ vọng và giả định hàm băm, không hứa worst-case O(1) cho mọi cấu trúc/ngôn ngữ.

## Cây nhị phân và cây tìm kiếm nhị phân
**Tình huống:** nhầm mọi cây nhị phân đều là BST hoặc đều tìm kiếm O(log n). BST có quy tắc thứ tự theo khóa; cây lệch có chiều cao O(n). Quy tắc xử lý khóa trùng cần được nêu rõ.

**Tự luyện:** chèn 1, 2, 3, 4 vào BST đơn giản và vẽ chiều cao. **Hướng giải:** kết quả lệch cho thấy không thể giả định cân bằng. Duyệt inorder của BST đúng quy tắc cho thứ tự tăng theo hợp đồng; thử cây rỗng và một nút. Không cập nhật khóa của nút tùy tiện làm phá bất biến thứ tự.

## Heap và hàng đợi ưu tiên
**Tình huống:** cần xử lý việc có mức ưu tiên nhỏ nhất trước. Min-heap cho phần tử nhỏ nhất ở gốc, không giữ toàn bộ mảng đã sắp xếp.
```python
import heapq
tasks = [(3, 0, "C"), (1, 1, "A"), (1, 2, "B")]
heapq.heapify(tasks)
assert heapq.heappop(tasks)[2] == "A"
assert heapq.heappop(tasks)[2] == "B"
```
**Tự luyện:** hai việc cùng ưu tiên và tên không so sánh được. **Hướng giải:** dùng bộ đếm ổn định làm tiêu chí phụ; không sửa trực tiếp khóa ưu tiên trong heap rồi kỳ vọng bất biến tự sửa. Với hủy/cập nhật việc, cần thiết kế riêng cách đánh dấu hoặc dựng lại.

## Đồ thị, BFS và DFS
**Tình huống:** đồ thị có chu kỳ khiến duyệt lặp mãi. Đánh dấu visited đúng thời điểm; BFS tìm số cạnh ngắn nhất trên đồ thị không trọng số, không thay thế thuật toán đường đi trọng số tùy ý.
```python
from collections import deque
graph = {"A": ["B", "C"], "B": ["A"], "C": []}
queue, seen = deque(["A"]), {"A"}
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        if neighbor not in seen:
            seen.add(neighbor)
            queue.append(neighbor)
assert seen == {"A", "B", "C"}
```
**Tự luyện:** thêm nút không liên thông. **Hướng giải:** duyệt từ A không tự thăm thành phần khác; phân biệt có hướng và vô hướng khi thêm cạnh.

## Chia để trị và quy hoạch động nhập môn
**Tình huống:** tính lại cùng bài toán con rất nhiều lần. Quy hoạch động lưu kết quả khi bài toán có cấu trúc phù hợp; trước tiên phải xác định trạng thái, chuyển trạng thái và điều kiện đầu.
```python
def ways(n):
    if n < 0:
        return 0
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a

assert [ways(i) for i in range(4)] == [1, 1, 2, 3]
```
Bài toán: lên n bậc, mỗi lần 1 hoặc 2 bậc; quy ước n=0 có một cách rỗng. **Tự luyện:** liệt kê bằng tay n=3. **Hướng giải:** (1,1,1), (1,2), (2,1); thứ tự bước là một phần của cách.

## Dự án nhỏ: bộ tra cứu và thống kê dữ liệu
**Bài thực hành:** nạp danh sách sách/học viên lab, tìm theo mã, lọc tên và thống kê từ. Nêu trường duy nhất, quy tắc chuẩn hóa và xử lý trùng; chọn list/map/index phù hợp với thao tác thường dùng.

**Tự luyện:** so kết quả thuật toán tối ưu với cách đơn giản trên dữ liệu nhỏ trước khi đo tốc độ. **Hướng giải:** kiểm tra rỗng, trùng, Unicode, không tìm thấy và input lớn có kiểm soát. Báo cáo gồm bất biến, độ phức tạp dự kiến, môi trường đo và giới hạn; không dùng một biểu đồ thời gian để tuyên bố chứng minh Big-O.

# Tài liệu tham khảo
https://docs.python.org/3/library/collections.html
