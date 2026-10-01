=== LESSON 19 ===
## Mục tiêu bài học
- Phân biệt JDK, JRE và JVM
- Cài đặt JDK và IntelliJ IDEA
- Viết, biên dịch và chạy chương trình Java đầu tiên

## 1. JDK, JRE và JVM
JVM (Java Virtual Machine) là máy ảo chạy bytecode của Java. Mã nguồn Java được biên dịch thành bytecode, sau đó JVM chạy bytecode trên từng hệ điều hành, nhờ đó chương trình Java chạy được ở nhiều nơi. JRE (Java Runtime Environment) gồm JVM và thư viện chuẩn, đủ để chạy chương trình. JDK (Java Development Kit) gồm JRE cùng trình biên dịch `javac` và các công cụ phát triển; muốn viết chương trình cần cài JDK.

## 2. Cài đặt môi trường
1. Tải và cài JDK bản LTS (ví dụ 17 hoặc 21).
2. Kiểm tra bằng lệnh `java -version` và `javac -version` trong cửa sổ dòng lệnh.
3. Cài IntelliJ IDEA (bản Community là đủ) — môi trường phát triển tích hợp (IDE) phổ biến để viết mã Java.
4. Tạo dự án mới: File, New, Project, chọn JDK vừa cài.

## 3. Chương trình Java đầu tiên
Mỗi chương trình Java bắt đầu chạy từ phương thức `public static void main(String[] args)`. Tên file `.java` phải trùng với tên lớp public bên trong.

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Xin chào Java!");
    }
}
```

Quy trình: `javac HelloWorld.java` biên dịch ra file `HelloWorld.class` (bytecode), rồi `java HelloWorld` chạy chương trình. Trong IDE chỉ cần bấm nút Run.

## Tóm tắt
- JDK ⊃ JRE ⊃ JVM; viết chương trình cần JDK.
- Mã nguồn được biên dịch thành bytecode rồi chạy trên JVM.
- Điểm vào của chương trình là phương thức `main`.

## Bài tập vận dụng
1. Cài JDK và IntelliJ, chụp lại kết quả lệnh `java -version`.
2. Viết chương trình in ra họ tên và lớp của bạn.
3. Giải thích vì sao Java được gọi là "viết một lần, chạy mọi nơi".

=== LESSON 20 ===
## Mục tiêu bài học
- Nắm các kiểu dữ liệu nguyên thuỷ và kiểu tham chiếu
- Khai báo biến, hằng số và ép kiểu
- Sử dụng String đúng cách

## 1. Kiểu dữ liệu nguyên thuỷ
Java có tám kiểu nguyên thuỷ: `byte`, `short`, `int`, `long`, `float`, `double`, `char` và `boolean`. Kiểu `int` lưu số nguyên 32 bit, `long` lưu số nguyên 64 bit (thêm hậu tố L), `double` là kiểu số thực mặc định, `char` lưu một ký tự Unicode và `boolean` chỉ nhận `true` hoặc `false`.

```java
int tuoi = 20;
double diem = 8.5;
char xepLoai = 'A';
boolean dau = true;
long dan = 8_000_000_000L;
```

## 2. Biến và hằng số
Java là ngôn ngữ định kiểu tĩnh, mỗi biến phải được khai báo kiểu trước khi dùng. Từ khoá `final` dùng để khai báo hằng số, giá trị không thể gán lại: `final double PI = 3.14159;`.

## 3. Ép kiểu
Chuyển từ kiểu nhỏ sang lớn là tự động (`int` sang `double`); chuyển từ kiểu lớn sang nhỏ phải ép kiểu tường minh và có thể mất dữ liệu.

```java
int a = 7;
double b = a;          // tự động: 7.0
int c = (int) 9.8;     // ép kiểu: 9
```

## 4. Kiểu tham chiếu và String
`String` là kiểu tham chiếu dùng để lưu chuỗi ký tự và là đối tượng bất biến (immutable). Để so sánh nội dung hai chuỗi phải dùng phương thức `equals`, không dùng toán tử `==`, vì `==` chỉ so sánh hai biến có cùng trỏ tới một đối tượng hay không.

```java
String a = new String("java");
String b = new String("java");
System.out.println(a == b);       // false
System.out.println(a.equals(b));  // true
```

## Tóm tắt
- Tám kiểu nguyên thuỷ; `double` là số thực mặc định.
- `final` tạo hằng số; ép kiểu từ lớn xuống nhỏ phải viết tường minh.
- So sánh chuỗi bằng `equals`, không dùng `==`.

## Bài tập vận dụng
1. Khai báo biến cho các thông tin của một sinh viên với kiểu dữ liệu phù hợp.
2. Nhập hai số nguyên và in ra thương dưới dạng số thực.
3. Giải thích kết quả của `"abc" == "abc"` và `new String("abc") == new String("abc")`.

=== LESSON 21 ===
## Mục tiêu bài học
- Sử dụng câu lệnh rẽ nhánh if-else và switch-case
- Sử dụng các vòng lặp for, while, do-while
- Điều khiển vòng lặp bằng break và continue

## 1. Câu lệnh rẽ nhánh
Câu lệnh rẽ nhánh gồm `if`, `else if`, `else` và `switch`. Điều kiện của `if` phải là biểu thức `boolean`.

```java
int diem = 8;
if (diem >= 8) {
    System.out.println("Giỏi");
} else if (diem >= 6) {
    System.out.println("Khá");
} else {
    System.out.println("Trung bình");
}
```

## 2. switch-case
Câu lệnh `switch` chọn một nhánh theo giá trị của biểu thức, mỗi nhánh thường kết thúc bằng `break` để không chạy tiếp sang nhánh kế. Nhánh `default` xử lý các giá trị còn lại.

```java
switch (thu) {
    case 2: System.out.println("Thứ hai"); break;
    case 3: System.out.println("Thứ ba"); break;
    default: System.out.println("Khác");
}
```

## 3. Vòng lặp
Vòng lặp `for` dùng khi biết trước số lần lặp; `while` lặp khi điều kiện còn đúng; `do-while` luôn thực hiện thân vòng lặp ít nhất một lần vì kiểm tra điều kiện sau.

```java
for (int i = 1; i <= 5; i++) {
    System.out.println(i);
}
int n = 10;
do {
    n--;
} while (n > 5);
```

## 4. break, continue và mảng
Lệnh `break` thoát khỏi vòng lặp, lệnh `continue` bỏ qua phần còn lại của lần lặp hiện tại. Mảng là cấu trúc lưu nhiều phần tử cùng kiểu với kích thước cố định, chỉ số bắt đầu từ 0; duyệt mảng bằng `for` hoặc `for-each`: `for (int x : mang) {...}`.

## Tóm tắt
- `if`/`else`/`switch` để rẽ nhánh; nhớ `break` trong `switch`.
- `for`, `while`, `do-while` cho vòng lặp; `do-while` chạy ít nhất một lần.
- Mảng có kích thước cố định, chỉ số bắt đầu từ 0.

## Bài tập vận dụng
1. Nhập điểm và in xếp loại bằng if-else.
2. In bảng cửu chương của một số nhập vào bằng vòng lặp for.
3. Tìm giá trị lớn nhất trong một mảng số nguyên.

=== LESSON 22 ===
## Mục tiêu bài học
- Hiểu khái niệm lớp, đối tượng và sự khác nhau giữa chúng
- Viết lớp có thuộc tính, phương thức và constructor
- Áp dụng tính đóng gói với getter và setter

## 1. Lớp và đối tượng
Lớp (class) là bản thiết kế mô tả thuộc tính và phương thức của một nhóm đối tượng. Đối tượng (object) là một thể hiện cụ thể của lớp, được tạo bằng từ khoá `new`. Thuộc tính lưu trạng thái của đối tượng, phương thức mô tả hành vi.

## 2. Constructor
Constructor là phương thức đặc biệt được gọi khi tạo đối tượng, có tên trùng với tên lớp và không có kiểu trả về, kể cả `void`. Nếu lớp không khai báo constructor nào, Java tự tạo constructor mặc định không tham số. Từ khoá `this` tham chiếu tới đối tượng hiện tại, thường dùng khi tên tham số trùng tên thuộc tính.

```java
public class SinhVien {
    private String ten;
    private double diem;

    public SinhVien(String ten, double diem) {
        this.ten = ten;
        this.diem = diem;
    }
    public String getTen() { return ten; }
    public void setDiem(double diem) {
        if (diem >= 0 && diem <= 10) this.diem = diem;
    }
}
```

## 3. Tính đóng gói
Đóng gói (encapsulation) là việc che giấu dữ liệu bên trong lớp và chỉ cho truy cập qua phương thức. Thuộc tính thường được khai báo `private`, kèm phương thức getter và setter `public`; setter có thể kiểm tra dữ liệu hợp lệ. Các phạm vi truy cập gồm `private`, mặc định (không ghi), `protected` và `public`.

## 4. Thành phần static
Thành phần `static` thuộc về lớp chứ không thuộc về từng đối tượng, gọi được qua tên lớp, ví dụ `Math.sqrt(9)`. Dùng `static` cho biến đếm chung hoặc phương thức tiện ích.

## Tóm tắt
- Lớp là bản thiết kế, đối tượng tạo bằng `new`.
- Constructor trùng tên lớp, không có kiểu trả về; `this` là đối tượng hiện tại.
- Đóng gói: thuộc tính `private`, truy cập qua getter và setter.

## Bài tập vận dụng
1. Viết lớp HinhChuNhat với constructor, phương thức tính diện tích và chu vi.
2. Viết lớp TaiKhoan có phương thức rút tiền không cho rút quá số dư.
3. Tạo 3 đối tượng SinhVien và in thông tin ra màn hình.

=== LESSON 23 ===
## Mục tiêu bài học
- Hiểu và áp dụng kế thừa (inheritance)
- Phân biệt nạp chồng (overloading) và ghi đè (overriding)
- Hiểu đa hình (polymorphism) trong Java

## 1. Kế thừa
Kế thừa (inheritance) cho phép lớp con dùng lại thuộc tính và phương thức của lớp cha. Java dùng từ khoá `extends` và chỉ hỗ trợ đơn kế thừa với lớp. Từ khoá `super` dùng để gọi constructor hoặc phương thức của lớp cha. Mọi lớp trong Java đều kế thừa ngầm định từ lớp `Object`.

```java
class DongVat {
    protected String ten;
    DongVat(String ten) { this.ten = ten; }
    void keu() { System.out.println("..."); }
}
class Cho extends DongVat {
    Cho(String ten) { super(ten); }
    @Override
    void keu() { System.out.println(ten + ": gâu gâu"); }
}
```

## 2. Phân biệt overloading và overriding
Nạp chồng (overloading) là khai báo nhiều phương thức cùng tên trong một lớp nhưng khác danh sách tham số. Ghi đè (overriding) là lớp con định nghĩa lại phương thức của lớp cha với cùng tên và cùng tham số. Overloading được xác định lúc biên dịch, overriding được xác định lúc chạy; chú thích `@Override` giúp trình biên dịch kiểm tra ghi đè.

## 3. Đa hình
Đa hình (polymorphism) là khả năng một lời gọi phương thức cho ra hành vi khác nhau tuỳ đối tượng thực tế. Ví dụ biến kiểu `DongVat` trỏ tới đối tượng `Cho` thì lời gọi `keu()` chạy phương thức của `Cho`.

```java
DongVat[] ds = { new Cho("Mực"), new Meo("Mướp") };
for (DongVat d : ds) {
    d.keu();   // mỗi con kêu theo cách riêng
}
```

## 4. Từ khoá final
`final` đặt trước lớp thì lớp không thể bị kế thừa, đặt trước phương thức thì không thể bị ghi đè.

## Tóm tắt
- `extends` để kế thừa; `super` gọi lớp cha; Java chỉ đơn kế thừa với lớp.
- Overloading: cùng tên khác tham số; overriding: lớp con định nghĩa lại phương thức lớp cha.
- Đa hình: hành vi phụ thuộc đối tượng thực tế lúc chạy.

## Bài tập vận dụng
1. Viết lớp Hinh với phương thức dienTich() và hai lớp con HinhTron, HinhChuNhat ghi đè phương thức này.
2. Viết ví dụ nạp chồng phương thức `tong` cho hai và ba tham số.
3. Giải thích sự khác nhau giữa overloading và overriding.

=== LESSON 24 ===
## Mục tiêu bài học
- Hiểu và viết lớp trừu tượng (abstract class)
- Hiểu và cài đặt interface
- Phân biệt interface và abstract class

## 1. Lớp trừu tượng
Lớp trừu tượng (abstract class) là lớp không thể tạo đối tượng trực tiếp, khai báo bằng từ khoá `abstract`. Lớp trừu tượng có thể chứa cả phương thức trừu tượng (không có thân) và phương thức thường có thân. Lớp con phải cài đặt mọi phương thức trừu tượng, trừ khi nó cũng là lớp trừu tượng.

```java
abstract class Hinh {
    abstract double dienTich();
    void in() { System.out.println("Diện tích: " + dienTich()); }
}
class HinhTron extends Hinh {
    double r;
    HinhTron(double r) { this.r = r; }
    double dienTich() { return Math.PI * r * r; }
}
```

## 2. Interface
Interface là bản hợp đồng khai báo các phương thức mà lớp cài đặt phải thực hiện. Một lớp dùng từ khoá `implements` để cài đặt interface và có thể cài đặt nhiều interface cùng lúc. Từ Java 8, interface có thể chứa phương thức `default` có sẵn phần thân.

```java
interface CoTheBay {
    void bay();
}
class Chim implements CoTheBay {
    public void bay() { System.out.println("Chim bay"); }
}
```

## 3. Phân biệt interface và abstract class
Một lớp chỉ kế thừa (`extends`) được một abstract class nhưng cài đặt (`implements`) được nhiều interface. Abstract class có thể có thuộc tính thường và constructor, interface chỉ có hằng số và không có constructor. Dùng abstract class khi các lớp có chung phần cài đặt, dùng interface khi chỉ cần chung khả năng.

## 4. Lợi ích
Cả hai giúp lập trình theo hợp đồng, làm code dễ mở rộng và dễ thay thế thành phần (ví dụ thay lớp lưu dữ liệu bằng file hoặc cơ sở dữ liệu mà không đổi nơi sử dụng).

## Tóm tắt
- Abstract class: không tạo đối tượng trực tiếp, có thể có phương thức trừu tượng và thường.
- Interface: hợp đồng chỉ khai báo hành vi; lớp cài đặt nhiều interface bằng `implements`.
- Chọn abstract class khi có phần cài đặt chung, chọn interface khi cần chung khả năng.

## Bài tập vận dụng
1. Viết abstract class NhanVien với phương thức trừu tượng tinhLuong() và hai lớp con.
2. Viết interface CoTheDiChuyen và hai lớp cài đặt nó.
3. Nêu ba điểm khác nhau giữa interface và abstract class.

=== LESSON 25 ===
## Mục tiêu bài học
- Hiểu ngoại lệ (exception) và phân loại ngoại lệ
- Sử dụng try-catch-finally, throw và throws
- Viết ngoại lệ tự định nghĩa

## 1. Ngoại lệ là gì
Ngoại lệ (exception) là sự kiện bất thường xảy ra khi chương trình đang chạy, làm gián đoạn luồng thực thi. Checked exception bắt buộc phải xử lý hoặc khai báo `throws`, ví dụ `IOException`. Unchecked exception kế thừa từ `RuntimeException`, ví dụ `NullPointerException` và `ArithmeticException`.

## 2. try-catch-finally
Khối `try` chứa đoạn mã có thể phát sinh ngoại lệ, khối `catch` bắt và xử lý ngoại lệ đó; một khối `try` có thể đi kèm nhiều khối `catch` cho các loại ngoại lệ khác nhau. Khối `finally` dùng để chứa đoạn mã luôn được thực thi dù có ngoại lệ hay không, thường để đóng file hoặc đóng kết nối.

```java
try {
    int kq = 10 / soChia;
    System.out.println(kq);
} catch (ArithmeticException e) {
    System.out.println("Không chia được cho 0");
} finally {
    System.out.println("Kết thúc");
}
```

## 3. throw và throws
Từ khoá `throw` dùng để ném một ngoại lệ, ví dụ `throw new IllegalArgumentException("Sai giá trị")`. Từ khoá `throws` dùng để khai báo các ngoại lệ mà phương thức có thể ném ra ở chữ ký phương thức.

## 4. Ngoại lệ tự định nghĩa
Custom exception là lớp ngoại lệ do lập trình viên tự định nghĩa để mô tả lỗi nghiệp vụ, thường kế thừa từ `Exception` hoặc `RuntimeException`.

```java
class InvalidPriceException extends RuntimeException {
    public InvalidPriceException(String msg) { super(msg); }
}

void datGia(double gia) {
    if (gia < 0) throw new InvalidPriceException("Giá không được âm");
}
```

## Tóm tắt
- Checked phải xử lý hoặc `throws`; unchecked kế thừa `RuntimeException`.
- `finally` luôn chạy, dùng để giải phóng tài nguyên.
- `throw` ném ngoại lệ, `throws` khai báo ngoại lệ; có thể tự định nghĩa ngoại lệ nghiệp vụ.

## Bài tập vận dụng
1. Viết chương trình nhập hai số và xử lý ngoại lệ chia cho 0 bằng try-catch.
2. Viết ngoại lệ tự định nghĩa TuoiKhongHopLeException và ném ra khi tuổi âm.
3. Giải thích vì sao nên dùng `finally` khi làm việc với file.

=== LESSON 26 ===
## Mục tiêu bài học
- Hiểu Collection Framework và các interface List, Set, Map
- Sử dụng ArrayList để lưu danh sách
- Sử dụng HashMap để lưu cặp khoá - giá trị

## 1. Collection Framework
Collection Framework là tập hợp các interface và lớp dùng để lưu trữ và thao tác nhóm đối tượng. Các interface chính gồm `List` (có thứ tự, cho trùng), `Set` (không trùng lặp) và `Map` (cặp khoá - giá trị). Collection chỉ lưu đối tượng, nên kiểu nguyên thuỷ được tự động đóng gói, ví dụ `int` thành `Integer`.

## 2. ArrayList
`ArrayList` là lớp cài đặt `List` dựa trên mảng động, tự tăng kích thước khi thêm phần tử. Phương thức `add` thêm phần tử, `get` lấy phần tử theo chỉ số, `remove` xoá phần tử và `size` trả về số phần tử. Generic như `ArrayList<String>` giúp kiểm tra kiểu dữ liệu ngay lúc biên dịch.

```java
ArrayList<String> ds = new ArrayList<>();
ds.add("An");
ds.add("Bình");
for (String ten : ds) {
    System.out.println(ten);
}
System.out.println(ds.size());   // 2
```

## 3. HashMap
`HashMap` là lớp cài đặt `Map` lưu dữ liệu theo cặp khoá - giá trị, mỗi khoá là duy nhất. Phương thức `put` thêm hoặc cập nhật giá trị, `get` lấy giá trị theo khoá, `containsKey` kiểm tra khoá có tồn tại. `HashMap` không đảm bảo thứ tự phần tử; cần giữ thứ tự thêm vào thì dùng `LinkedHashMap`.

```java
HashMap<String, Double> diem = new HashMap<>();
diem.put("An", 8.5);
diem.put("Bình", 7.0);
System.out.println(diem.get("An"));          // 8.5
for (String ten : diem.keySet()) {
    System.out.println(ten + ": " + diem.get(ten));
}
```

## 4. Chọn cấu trúc phù hợp
Dùng `ArrayList` khi cần danh sách có thứ tự và truy cập theo chỉ số; `HashSet` khi cần loại bỏ phần tử trùng; `HashMap` khi cần tra cứu nhanh theo khoá.

## Tóm tắt
- `List` có thứ tự, `Set` không trùng, `Map` lưu cặp khoá - giá trị.
- `ArrayList` là mảng động; `HashMap` tra cứu nhanh theo khoá duy nhất.
- Dùng generic để kiểm tra kiểu ngay khi biên dịch.

## Bài tập vận dụng
1. Nhập danh sách tên học viên vào ArrayList rồi in ra theo thứ tự.
2. Dùng HashMap lưu điểm của học viên và tìm điểm theo tên.
3. Loại các phần tử trùng trong một danh sách bằng HashSet.

=== LESSON 27 ===
## Mục tiêu bài học
- Xây dựng ứng dụng console quản lý sản phẩm bằng Java
- Kết hợp lớp, ArrayList, HashMap và xử lý ngoại lệ
- Rèn kỹ năng thiết kế chương trình theo lớp

## 1. Yêu cầu
Ứng dụng quản lý sản phẩm với các chức năng: thêm sản phẩm, hiển thị danh sách, tìm theo mã, cập nhật giá, xoá sản phẩm và thống kê tổng giá trị kho.

## 2. Thiết kế
- Lớp `Product` gồm các thuộc tính `id`, `name`, `price` cùng getter và setter; setter của `price` ném `InvalidPriceException` khi giá nhỏ hơn 0.
- Lớp `ProductManager` dùng `ArrayList<Product>` để lưu danh sách và `HashMap<String, Product>` để tra cứu nhanh theo mã.
- Lớp `Main` hiển thị menu, đọc lựa chọn bằng `Scanner` và gọi các phương thức tương ứng.

## 3. Cài đặt mẫu

```java
class ProductManager {
    private final ArrayList<Product> ds = new ArrayList<>();
    private final HashMap<String, Product> theoMa = new HashMap<>();

    void them(Product p) {
        if (theoMa.containsKey(p.getId()))
            throw new IllegalArgumentException("Trùng mã sản phẩm");
        ds.add(p);
        theoMa.put(p.getId(), p);
    }

    Product tim(String id) { return theoMa.get(id); }

    double tongGiaTri() {
        double tong = 0;
        for (Product p : ds) tong += p.getPrice();
        return tong;
    }
}
```

## 4. Gợi ý mở rộng
Sắp xếp danh sách theo giá bằng `Comparator`; lưu danh sách ra file; thêm kiểu sản phẩm kế thừa (hàng điện tử, thực phẩm) để thực hành đa hình.

## Tóm tắt
- Mỗi lớp đảm nhận một trách nhiệm rõ ràng (dữ liệu, xử lý, giao diện).
- Kết hợp ArrayList cho danh sách và HashMap cho tra cứu nhanh.
- Dùng ngoại lệ để báo dữ liệu không hợp lệ.

## Bài tập vận dụng
1. Hoàn thiện ứng dụng với menu đầy đủ các chức năng.
2. Sắp xếp danh sách sản phẩm theo giá giảm dần.
3. Thêm chức năng ghi và đọc danh sách sản phẩm từ file.
