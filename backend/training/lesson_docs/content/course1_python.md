=== LESSON 2 ===
## Mục tiêu bài học
- Hiểu biến là gì và cách đặt tên biến đúng quy tắc
- Phân biệt được các kiểu dữ liệu cơ bản: int, float, str, bool
- Biết kiểm tra và chuyển đổi kiểu dữ liệu

## 1. Biến trong Python
Biến là một cái tên dùng để lưu giá trị trong bộ nhớ. Trong Python không cần khai báo kiểu tường minh; kiểu được xác định lúc chạy, dựa vào giá trị được gán bằng dấu `=`.

```python
ten = "An"
tuoi = 20
diem = 8.5
da_dang_ky = True
```

Quy tắc đặt tên: chỉ gồm chữ cái, chữ số và dấu gạch dưới; không bắt đầu bằng chữ số; phân biệt chữ hoa, chữ thường (`diem` khác `Diem`); không trùng từ khoá như `if`, `for`, `class`. Nên đặt tên viết thường, nối bằng dấu gạch dưới, ví dụ `so_luong_sinh_vien`.

## 2. Các kiểu dữ liệu cơ bản
- **int**: số nguyên, ví dụ `10`, `-3`.
- **float**: số thực, ví dụ `3.14`.
- **str**: chuỗi ký tự đặt trong dấu nháy đơn hoặc kép, ví dụ `"Xin chào"`.
- **bool**: chỉ có hai giá trị `True` và `False`.

Ngoài ra còn có `list` (danh sách có thể thay đổi), `tuple` (bất biến), `dict` (từ điển key-value) và `set` (tập hợp). Hàm `type(x)` trả về kiểu của giá trị x, ví dụ `type(3.14)` trả về `<class 'float'>`.

## 3. Chuyển đổi kiểu
Dùng các hàm `int()`, `float()`, `str()`, `bool()` để đổi kiểu. Hàm `input()` luôn trả về chuỗi nên cần ép kiểu khi tính toán.

```python
tuoi = int(input("Nhập tuổi: "))
print("Năm sau bạn", tuoi + 1, "tuổi")
print(type(tuoi))   # <class 'int'>
```

## Tóm tắt
- Biến lưu giá trị, kiểu được xác định theo giá trị gán.
- Bốn kiểu cơ bản: int, float, str, bool; dùng `type()` để kiểm tra.
- `input()` trả về chuỗi, cần `int()` hoặc `float()` khi tính toán.

## Bài tập vận dụng
1. Khai báo biến lưu họ tên, tuổi, điểm trung bình của bạn rồi in ra kiểu của từng biến.
2. Nhập hai số từ bàn phím và in ra tổng của chúng.
3. Giải thích vì sao `"5" + "3"` cho kết quả khác `5 + 3`.

=== LESSON 3 ===
## Mục tiêu bài học
- Sử dụng được toán tử số học, so sánh và logic
- Hiểu độ ưu tiên của các toán tử
- Phân biệt toán tử gán `=` và toán tử so sánh `==`

## 1. Toán tử số học
Các toán tử số học gồm `+` (cộng), `-` (trừ), `*` (nhân), `/` (chia, luôn ra số thực), `//` (chia lấy phần nguyên), `%` (chia lấy dư) và `**` (luỹ thừa).

```python
print(7 / 2)    # 3.5
print(7 // 2)   # 3
print(7 % 2)    # 1
print(2 ** 10)  # 1024
```

Toán tử `%` thường dùng để kiểm tra số chẵn, lẻ: `n % 2 == 0` là số chẵn.

## 2. Toán tử so sánh
Các toán tử so sánh trả về giá trị `True` hoặc `False`: `==` (bằng), `!=` (khác), `>`, `<`, `>=`, `<=`. Không được nhầm `==` (so sánh) với `=` (phép gán).

## 3. Toán tử logic
- `and`: đúng khi cả hai vế cùng đúng.
- `or`: đúng khi ít nhất một vế đúng.
- `not`: đảo ngược giá trị logic.

```python
tuoi = 20
print(tuoi >= 18 and tuoi < 60)   # True
print(not (tuoi > 30))            # True
```

## 4. Toán tử gán rút gọn và độ ưu tiên
Có thể viết gọn `x += 5` thay cho `x = x + 5`; tương tự với `-=`, `*=`, `/=`. Độ ưu tiên từ cao xuống thấp: `**`, sau đó `*` `/` `//` `%`, rồi `+` `-`, tiếp theo là so sánh, cuối cùng là `not`, `and`, `or`. Dùng dấu ngoặc để làm rõ ý.

## Tóm tắt
- Số học: `+ - * / // % **`; so sánh cho kết quả True/False; logic dùng `and`, `or`, `not`.
- `==` là so sánh, `=` là gán.
- Dùng ngoặc để kiểm soát thứ tự tính.

## Bài tập vận dụng
1. Nhập một số nguyên và in ra số đó chẵn hay lẻ (dùng `%`).
2. Tính diện tích và chu vi hình chữ nhật từ chiều dài, chiều rộng nhập vào.
3. Viết biểu thức logic kiểm tra một năm là năm nhuận.

=== LESSON 4 ===
## Mục tiêu bài học
- Viết được câu lệnh rẽ nhánh if, elif, else
- Hiểu vai trò của thụt lề trong Python
- Kết hợp điều kiện bằng toán tử logic

## 1. Câu lệnh if
Câu lệnh `if` thực hiện một khối lệnh khi điều kiện đúng. Khối lệnh trong Python được xác định bằng thụt lề (thường 4 dấu cách), không dùng dấu ngoặc nhọn. Sau điều kiện phải có dấu hai chấm `:`.

```python
diem = 7.5
if diem >= 5:
    print("Đạt")
```

## 2. if - else và elif
`else` xử lý trường hợp điều kiện sai. Khi có nhiều nhánh, dùng `elif`; Python kiểm tra lần lượt từ trên xuống và chỉ chạy nhánh đầu tiên đúng.

```python
diem = 7.5
if diem >= 8:
    print("Giỏi")
elif diem >= 6.5:
    print("Khá")
elif diem >= 5:
    print("Trung bình")
else:
    print("Yếu")
```

## 3. Điều kiện phức hợp và if lồng nhau
Kết hợp nhiều điều kiện bằng `and`, `or`, `not`. Có thể đặt `if` bên trong `if` khác, nhưng nên hạn chế lồng quá sâu để code dễ đọc.

```python
tuoi = 20
co_the = True
if tuoi >= 18 and co_the:
    print("Được đăng ký")
```

## 4. Biểu thức điều kiện một dòng
Python cho phép viết gọn: `ket_qua = "Đạt" if diem >= 5 else "Không đạt"`.

## Tóm tắt
- `if`, `elif`, `else` dùng để rẽ nhánh; khối lệnh xác định bằng thụt lề.
- Chỉ nhánh đầu tiên có điều kiện đúng được thực hiện.
- Dùng `and`, `or`, `not` để ghép điều kiện.

## Bài tập vận dụng
1. Nhập điểm và in ra xếp loại theo thang điểm Giỏi, Khá, Trung bình, Yếu.
2. Nhập ba số và tìm số lớn nhất bằng câu lệnh if.
3. Viết chương trình kiểm tra một năm có phải năm nhuận hay không.

=== LESSON 5 ===
## Mục tiêu bài học
- Sử dụng vòng lặp for với range và với danh sách
- Sử dụng vòng lặp while khi chưa biết trước số lần lặp
- Điều khiển vòng lặp bằng break và continue

## 1. Vòng lặp for
Vòng lặp `for` dùng để lặp qua từng phần tử của một dãy (list, tuple, str, range). Hàm `range(n)` sinh các số từ 0 đến n-1; `range(a, b)` từ a đến b-1; `range(a, b, bước)` cho phép đặt bước nhảy.

```python
for i in range(1, 6):
    print(i)

for item in [10, 20, 30]:
    print(item)
```

## 2. Vòng lặp while
Vòng lặp `while` lặp trong khi điều kiện còn đúng. Cần đảm bảo điều kiện sẽ trở thành sai ở một thời điểm, nếu không chương trình chạy vô hạn.

```python
tong = 0
n = 1
while n <= 100:
    tong += n
    n += 1
print("Tổng 1..100 =", tong)
```

## 3. break và continue
Lệnh `break` thoát khỏi vòng lặp ngay lập tức. Lệnh `continue` bỏ qua phần còn lại của vòng lặp hiện tại và sang vòng kế tiếp.

```python
for i in range(1, 10):
    if i % 2 == 0:
        continue      # bỏ qua số chẵn
    if i > 7:
        break         # dừng khi i > 7
    print(i)          # in 1 3 5 7
```

## 4. Vòng lặp lồng nhau
Đặt một vòng lặp bên trong vòng lặp khác, ví dụ in bảng cửu chương: vòng ngoài chạy theo số nhân, vòng trong chạy từ 1 đến 10.

## Tóm tắt
- `for` khi biết trước dãy cần lặp; `while` khi lặp theo điều kiện.
- `break` thoát vòng lặp, `continue` sang vòng kế tiếp.
- Cẩn thận vòng lặp vô hạn khi dùng `while`.

## Bài tập vận dụng
1. In bảng cửu chương của một số nhập từ bàn phím.
2. Tính tổng các số chẵn từ 1 đến 100.
3. Dùng `while` để yêu cầu người dùng nhập mật khẩu cho đến khi đúng.

=== LESSON 6 ===
## Mục tiêu bài học
- Định nghĩa và gọi hàm bằng từ khoá def
- Sử dụng tham số, tham số mặc định và giá trị trả về
- Hiểu phạm vi của biến trong và ngoài hàm

## 1. Định nghĩa hàm
Hàm là một khối lệnh được đặt tên để tái sử dụng. Từ khoá `def` dùng để định nghĩa hàm; hàm trả về giá trị bằng `return`. Nếu không có `return`, hàm trả về `None`.

```python
def cong(a, b):
    return a + b

print(cong(3, 4))   # 7
```

## 2. Tham số và đối số
Tham số là tên khai báo trong định nghĩa hàm, đối số là giá trị truyền vào khi gọi. Tham số có thể có giá trị mặc định, và có thể truyền theo tên.

```python
def chao(ten, loi="Xin chào"):
    print(loi, ten)

chao("An")                  # Xin chào An
chao("Bình", loi="Chào bạn")  # Chào bạn Bình
```

## 3. Trả về nhiều giá trị
Hàm có thể trả về nhiều giá trị cùng lúc (dưới dạng tuple):

```python
def min_max(ds):
    return min(ds), max(ds)

nho, lon = min_max([4, 9, 1, 7])
```

## 4. Phạm vi biến
Biến khai báo trong hàm là biến cục bộ, chỉ dùng được trong hàm đó. Biến khai báo ngoài hàm là biến toàn cục. Nên truyền dữ liệu vào hàm bằng tham số và lấy kết quả bằng `return` thay vì dùng biến toàn cục.

## Tóm tắt
- `def` định nghĩa hàm, `return` trả về kết quả (mặc định `None`).
- Tham số có thể có giá trị mặc định; có thể trả về nhiều giá trị.
- Biến trong hàm là biến cục bộ.

## Bài tập vận dụng
1. Viết hàm kiểm tra một số có phải số nguyên tố hay không.
2. Viết hàm tính giai thừa của n.
3. Viết hàm nhận danh sách điểm và trả về điểm trung bình.

=== LESSON 7 ===
## Mục tiêu bài học
- Hiểu khái niệm lớp (class) và đối tượng (object)
- Định nghĩa lớp với thuộc tính và phương thức
- Sử dụng phương thức khởi tạo `__init__` và tham số `self`

## 1. Lớp và đối tượng
Lập trình hướng đối tượng (OOP) mô hình hoá chương trình thành các đối tượng. Lớp (class) là bản thiết kế mô tả thuộc tính và hành vi; đối tượng (object) là một thể hiện cụ thể của lớp. Từ khoá `class` dùng để định nghĩa lớp.

## 2. Phương thức khởi tạo và self
Phương thức khởi tạo là `__init__`, được gọi tự động khi tạo đối tượng. Tham số đầu tiên của mọi phương thức thường là `self`, tham chiếu tới đối tượng hiện tại.

```python
class SinhVien:
    def __init__(self, ten, diem):
        self.ten = ten
        self.diem = diem

    def xep_loai(self):
        if self.diem >= 8:
            return "Giỏi"
        return "Khá" if self.diem >= 6.5 else "Trung bình"

sv = SinhVien("An", 8.5)
print(sv.ten, sv.xep_loai())   # An Giỏi
```

## 3. Thuộc tính lớp và phương thức đặc biệt
Thuộc tính khai báo ngay trong thân lớp (ngoài `__init__`) là thuộc tính lớp, dùng chung cho mọi đối tượng. Phương thức `__str__` quy định chuỗi hiển thị khi in đối tượng bằng `print()`.

```python
class SinhVien:
    truong = "ĐH Công nghệ"      # thuộc tính lớp
    def __str__(self):
        return f"{self.ten} ({self.diem})"
```

## Tóm tắt
- Lớp là bản thiết kế, đối tượng là thể hiện của lớp.
- `__init__` khởi tạo đối tượng; `self` tham chiếu tới chính đối tượng.
- `__str__` tuỳ biến cách in đối tượng.

## Bài tập vận dụng
1. Viết lớp HinhChuNhat có phương thức tính diện tích và chu vi.
2. Viết lớp TaiKhoan có phương thức nạp tiền, rút tiền (không cho rút quá số dư).
3. Tạo 3 đối tượng SinhVien và in danh sách ra màn hình.

=== LESSON 8 ===
## Mục tiêu bài học
- Hiểu tính kế thừa và lợi ích của nó
- Viết lớp con kế thừa lớp cha, gọi phương thức lớp cha bằng `super()`
- Ghi đè (override) phương thức của lớp cha

## 1. Kế thừa là gì
Kế thừa (inheritance) cho phép lớp con dùng lại thuộc tính và phương thức của lớp cha, giúp tránh lặp code. Lớp con được khai báo bằng cách đặt tên lớp cha trong dấu ngoặc.

```python
class Nguoi:
    def __init__(self, ten):
        self.ten = ten
    def gioi_thieu(self):
        print("Tôi là", self.ten)

class SinhVien(Nguoi):
    def __init__(self, ten, mssv):
        super().__init__(ten)
        self.mssv = mssv
```

## 2. Hàm super()
Hàm `super()` trả về đối tượng đại diện cho lớp cha, dùng để gọi phương thức của lớp cha, thường là `__init__`, để lớp con không phải viết lại phần khởi tạo chung.

## 3. Ghi đè phương thức
Lớp con có thể định nghĩa lại một phương thức của lớp cha với cùng tên để thay đổi hành vi. Đây là cơ sở của đa hình: cùng một lời gọi phương thức nhưng mỗi đối tượng xử lý theo cách riêng.

```python
class SinhVien(Nguoi):
    def gioi_thieu(self):
        super().gioi_thieu()
        print("MSSV:", self.mssv)
```

## 4. Kiểm tra quan hệ kế thừa
`isinstance(sv, Nguoi)` cho biết đối tượng có thuộc lớp (hoặc lớp cha của lớp) đó hay không; `issubclass(SinhVien, Nguoi)` kiểm tra quan hệ giữa hai lớp. Python hỗ trợ đa kế thừa, tức một lớp có thể kế thừa nhiều lớp cha.

## Tóm tắt
- Lớp con kế thừa thuộc tính, phương thức của lớp cha.
- `super()` gọi lớp cha; ghi đè phương thức để thay đổi hành vi.
- `isinstance` và `issubclass` kiểm tra quan hệ kế thừa.

## Bài tập vận dụng
1. Viết lớp Dong_vat và hai lớp con Cho, Meo cùng ghi đè phương thức `keu()`.
2. Viết lớp NhanVien kế thừa Nguoi, bổ sung thuộc tính lương và phương thức tính lương.
3. Giải thích sự khác nhau giữa ghi đè và gọi `super()` trong một phương thức.

=== LESSON 9 ===
## Mục tiêu bài học
- Áp dụng OOP để xây dựng chương trình quản lý sinh viên
- Kết hợp lớp, danh sách, hàm và vòng lặp trong một dự án nhỏ
- Rèn kỹ năng chia chương trình thành các phần nhỏ

## 1. Yêu cầu bài toán
Xây dựng chương trình console quản lý danh sách sinh viên với các chức năng: thêm sinh viên, hiển thị danh sách, tìm theo tên, xoá sinh viên và thống kê điểm trung bình.

## 2. Thiết kế
- Lớp `SinhVien` lưu mã, tên, điểm và có phương thức `xep_loai()`.
- Lớp `QuanLySinhVien` chứa danh sách (list) các sinh viên và các phương thức xử lý: `them`, `hien_thi`, `tim_theo_ten`, `xoa`, `diem_trung_binh`.
- Hàm `main()` hiển thị menu, nhận lựa chọn của người dùng bằng vòng lặp `while`.

## 3. Cài đặt mẫu

```python
class SinhVien:
    def __init__(self, ma, ten, diem):
        self.ma, self.ten, self.diem = ma, ten, diem

    def xep_loai(self):
        return "Giỏi" if self.diem >= 8 else "Khá" if self.diem >= 6.5 else "Trung bình"

class QuanLySinhVien:
    def __init__(self):
        self.ds = []

    def them(self, sv):
        self.ds.append(sv)

    def tim_theo_ten(self, tu_khoa):
        return [sv for sv in self.ds if tu_khoa.lower() in sv.ten.lower()]

    def diem_trung_binh(self):
        return sum(sv.diem for sv in self.ds) / len(self.ds) if self.ds else 0
```

## 4. Gợi ý mở rộng
Lưu danh sách ra file (văn bản hoặc JSON) để dữ liệu không mất khi tắt chương trình; kiểm tra dữ liệu nhập (điểm từ 0 đến 10, mã không trùng); sắp xếp danh sách theo điểm.

## Tóm tắt
- Chia bài toán thành các lớp có trách nhiệm rõ ràng.
- Dùng list để lưu tập đối tượng, duyệt bằng vòng lặp hoặc list comprehension.
- Menu bằng `while` giúp chương trình chạy liên tục đến khi người dùng thoát.

## Bài tập vận dụng
1. Hoàn thiện chương trình với đầy đủ menu và các chức năng ở trên.
2. Thêm chức năng sắp xếp danh sách theo điểm giảm dần.
3. Thêm chức năng ghi và đọc danh sách sinh viên từ file JSON.
