# Python — thực hành, giải thích lỗi và tự học

Tài liệu bổ sung cho từng bài của khóa Python cơ bản. Hãy chạy ví dụ, dự đoán kết quả trước khi xem hướng giải và lưu lại traceback khi cần trợ giúp. Ví dụ dùng Python 3, không cần cài thư viện ngoài.

## Cài đặt Python & IDE
**Tình huống:** “Em đã cài Python nhưng VS Code báo không tìm thấy thư viện hoặc không chạy đúng file.” Kiểm tra terminal đang đứng ở thư mục nào, tên file đã lưu và trình thông dịch được chọn. Môi trường ảo tách thư viện của dự án khỏi Python hệ thống; cài gói và chạy chương trình bằng cùng một interpreter.
```python
import sys
print(sys.executable)
print("Xin chào StudyOnline")
```
Chạy `python -m venv .venv` trong thư mục dự án. Trên Windows có thể chạy trực tiếp `.venv\Scripts\python.exe hello.py` mà không cần thay đổi chính sách PowerShell. Không đặt tên file trùng thư viện như `json.py`.

**Tự luyện:** tạo chương trình in tên và một phép tính; chạy từ terminal và nút Run. **Hướng giải:** hai cách phải dùng cùng interpreter và cho cùng kết quả; chụp lỗi nếu khác nhau. Đọc dòng cuối traceback rồi tìm vị trí thuộc file của mình, không cài lại toàn bộ công cụ ngay.

## Biến và kiểu dữ liệu
**Hỏi thực tế:** “Sao `print("2" + 3)` báo lỗi?” Trong Python, chuỗi và số nguyên không cộng trực tiếp. Muốn cộng số thì đổi chuỗi sang số; muốn ghép chữ thì đổi số sang chuỗi. `input()` luôn trả chuỗi, kể cả khi người dùng gõ 20.
```python
assert int("2") + 3 == 5
assert "2" + str(3) == "23"

def next_age(raw):
    try:
        age = int(raw)
    except ValueError:
        return "Hãy nhập tuổi bằng chữ số"
    return age + 1 if age >= 0 else "Tuổi không được âm"

assert next_age("20") == 21
assert next_age("hai mươi") == "Hãy nhập tuổi bằng chữ số"
```
**Tự luyện:** thử chuỗi rỗng, khoảng trắng, số âm và `"2.5"`. **Hướng giải:** `int("2.5")` không hợp lệ; nếu bài toán chấp nhận số thực thì dùng float và kiểm tra miền giá trị. Không bắt mọi lỗi rồi trả 0 vì sẽ che dữ liệu sai.

## Toán tử trong Python
**Tình huống:** nhập điểm hoặc tính tiền bị sai vì nhầm phép gán, so sánh và thứ tự tính. `=` gán giá trị; `==` kiểm tra bằng nhau; `/` chia thực, `//` lấy thương làm tròn xuống và `%` lấy phần dư. Với số âm, không coi `//` là cắt phần thập phân về 0.
```python
assert 7 / 2 == 3.5
assert 7 // 2 == 3
assert -7 // 2 == -4
assert 7 % 2 == 1
score = 7
assert 0 <= score <= 10
assert (2 + 3) * 4 == 20
```
**Tự luyện:** tính số hộp đủ 6 sản phẩm và số sản phẩm dư cho 20 sản phẩm. **Hướng giải:** `20 // 6` bằng 3 hộp, `20 % 6` bằng 2 sản phẩm. Đổi mẫu chia sang 0 phải phát hiện dữ liệu không hợp lệ trước phép chia. Khi so số thực đo đạc, cân nhắc sai số thay vì dùng đẳng thức tuyệt đối tùy tiện.

## Câu lệnh if - else
**Hỏi thực tế:** “Em bị IndentationError: dòng print sau if viết thế nào?” Dòng thuộc khối if phải thụt vào. Dùng nhất quán bốn dấu cách, không trộn tab và khoảng trắng. Dấu hai chấm kết thúc dòng điều kiện.
```python
if 5 > 2:
    print("đúng")

def classify(score):
    if not 0 <= score <= 10:
        raise ValueError("Điểm phải trong 0..10")
    if score >= 8:
        return "Tốt"
    elif score >= 5:
        return "Đạt"
    return "Cần ôn"

assert classify(5) == "Đạt"
assert classify(8) == "Tốt"
```
**Tự luyện:** thử -1, 0, 4.9, 5, 8 và 11. **Hướng giải:** điểm ngoài miền bị từ chối; điểm sát ngưỡng kiểm tra dấu `>=`. Kiểm tra ngưỡng cao trước để nhánh thấp không bắt mất trường hợp điểm cao. Muốn trợ giúp, gửi nguyên code có xuống dòng và thông báo lỗi đầy đủ.

## Vòng lặp for, while
**Hỏi thực tế:** “In 1 đến 5 thì sao range lại ghi 6?” `range(a, b)` lấy a nhưng không lấy b. for duyệt các phần tử của một iterable; while lặp khi điều kiện còn đúng, cần bảo đảm có thay đổi dẫn tới kết thúc.
```python
assert list(range(1, 6)) == [1, 2, 3, 4, 5]
total, n = 0, 1
while n <= 5:
    total += n
    n += 1
assert total == 15

values = [10, 20, 30]
assert values[0] == 10
assert values[2] == 30
```
Danh sách ba phần tử có chỉ số 0, 1, 2; `values[3]` gây IndexError. “Có ba số” không có nghĩa chỉ số lớn nhất là 3.

**Tự luyện:** cộng các số chẵn từ 1 tới 10, thử cả dãy rỗng. **Hướng giải:** duyệt `range(2, 11, 2)` cho tổng 30; dãy rỗng cho tổng 0. break thoát vòng lặp; continue bỏ phần còn lại của lượt hiện tại, nên không đặt việc cập nhật điều kiện while sau một continue có thể chạy mãi.

## Định nghĩa và sử dụng hàm
**Hỏi thực tế:** “return và print có giống nhau không?” print hiển thị; return kết thúc hàm và chuyển kết quả cho nơi gọi. return là từ khóa, không phải tên một hàm. Hàm không return giá trị sẽ trả None.
```python
def add(a, b):
    return a + b

assert add(2, 3) == 5
result = add(2, 3)
print(result)

def append_item(item, items=None):
    if items is None:
        items = []
    return items + [item]

assert append_item("An") == ["An"]
assert append_item("Bình") == ["Bình"]
```
**Tự luyện:** viết hàm tính trung bình không in bên trong; quy định rõ danh sách rỗng. **Hướng giải:** trả số hoặc báo ValueError theo hợp đồng, rồi assert giá trị trả về. Đừng dùng danh sách mutable làm đối số mặc định nếu các lần gọi cần độc lập.

## Class và Object
**Tình huống:** nhiều học viên cùng tên nhưng cần quản lý riêng. Class mô tả cấu trúc và hành vi; object là một đối tượng cụ thể. Thuộc tính thay đổi theo từng học viên phải đặt trên instance, tránh một danh sách dùng chung ngoài ý muốn.
```python
class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.scores = []

    def add_score(self, score):
        if not 0 <= score <= 10:
            raise ValueError("Điểm không hợp lệ")
        self.scores.append(score)

a, b = Student(1, "An"), Student(2, "An")
a.add_score(8)
assert a.scores == [8] and b.scores == []
```
**Tự luyện:** thêm phương thức tính trung bình và trường hợp chưa có điểm. **Hướng giải:** xử lý danh sách rỗng rõ ràng; không chia 0 hoặc tự ghi điểm 0 cho người chưa làm bài. Tên trùng không đồng nghĩa cùng một object hoặc cùng mã học viên.

## Kế thừa (Inheritance)
**Tình huống:** học viên thường và học viên học bổng có chung thông tin nhưng cách tính học phí khác. Kế thừa phù hợp quan hệ “là một”; thành phần được chứa bên trong nên cân nhắc composition.
```python
class Learner:
    def __init__(self, name):
        self.name = name
    def tuition(self):
        return 100

class ScholarshipLearner(Learner):
    def tuition(self):
        return super().tuition() * 0.5

assert ScholarshipLearner("An").tuition() == 50
assert ScholarshipLearner("An").name == "An"
```
**Tự luyện:** cho hai loại đối tượng vào cùng một danh sách và gọi tuition. **Hướng giải:** phương thức ghi đè được chọn theo đối tượng; không cần chuỗi if kiểm tra mọi tên lớp. Lớp học “có nhiều học viên” không nên kế thừa Student chỉ để dùng lại thuộc tính.

## Dự án nhỏ: Quản lý sinh viên
**Yêu cầu thực hành:** lưu mã, tên và danh sách điểm; từ chối mã trùng, tên rỗng và điểm ngoài 0..10. Chia tách nhập liệu, xử lý và xuất kết quả. Không sửa database LMS thật để làm bài tập.
```python
def add_student(registry, student_id, name):
    if student_id in registry:
        raise ValueError("Mã đã tồn tại")
    if not name.strip():
        raise ValueError("Tên rỗng")
    registry[student_id] = {"name": name.strip(), "scores": []}

students = {}
add_student(students, "SV01", " An ")
assert students["SV01"]["name"] == "An"
```
**Tự luyện:** thêm, tìm, sửa tên, tính trung bình và lưu JSON vào file riêng. **Hướng giải:** kiểm tra trước khi ghi; lưu được rồi đọc lại để so dữ liệu. Báo cáo cần có ca mã trùng, không tìm thấy, chưa có điểm, file không tồn tại và JSON lỗi. Gợi ý học 30 phút: 5 phút ôn, 15 phút viết một chức năng, 10 phút tự kiểm tra; đây là gợi ý tự học, không phải lịch thi chính thức.

# Tài liệu tham khảo
https://docs.python.org/3/tutorial/
