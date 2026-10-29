# Java — thực hành và xử lý lỗi nhập môn

Ví dụ sử dụng cú pháp lớp truyền thống, phù hợp bài tập Java cơ bản. Mỗi bài nên có một lớp chạy thử, dữ liệu đầu vào và kết quả mong đợi. Không lưu mật khẩu hoặc dữ liệu cá nhân thật trong ví dụ.

## Cài đặt JDK & IntelliJ
**Tình huống:** IDE chạy được nhưng terminal báo không tìm thấy javac. JDK có công cụ biên dịch; kiểm tra `java -version`, `javac -version` và JDK cấu hình trong dự án. Tên file phải khớp lớp public theo cách tổ chức thông thường.
```java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Xin chào Java");
    }
}
```
**Tự luyện:** lưu Hello.java, chạy `javac Hello.java` rồi `java Hello`. **Hướng giải:** không thêm .class vào tên lớp khi chạy; phân biệt thư mục hiện tại và classpath. Không sửa PATH ngẫu nhiên trước khi xác định terminal đang dùng bộ JDK nào.

## Biến, kiểu dữ liệu trong Java
**Tình huống:** đọc một số rồi đọc tên nhưng tên thành chuỗi rỗng. Khi dùng Scanner, nextInt để lại dấu xuống dòng; cách dễ kiểm soát là đọc nguyên dòng rồi chuyển đổi và kiểm tra lỗi.
```java
int age = Integer.parseInt("20");
double average = (7 + 8) / 2.0;
System.out.println(age + 1); // 21
System.out.println(average); // 7.5
```
**Tự luyện:** chuyển `"hai mươi"`, chuỗi rỗng và số quá lớn. **Hướng giải:** parseInt có thể ném NumberFormatException; yêu cầu nhập lại chứ không tự biến dữ liệu sai thành 0. So nội dung String bằng equals hoặc Objects.equals khi cần xử lý null, không dựa vào == để so nội dung.

## Cấu trúc điều khiển
**Tình huống:** vòng lặp vượt giới hạn mảng. Với mảng n phần tử, chỉ số từ 0 tới n-1; điều kiện thường là i < values.length.
```java
int[] values = {2, 4, 6};
int sum = 0;
for (int value : values) {
    sum += value;
}
System.out.println(sum); // 12
```
**Tự luyện:** mảng rỗng, một phần tử và ba phần tử. **Hướng giải:** tổng bắt đầu 0, không truy cập phần tử đầu khi chưa kiểm tra rỗng. Với while, chỉ ra biến làm điều kiện thay đổi; tránh nhầm phép gán và so sánh hoặc bỏ quên nhánh kết thúc.

## Class, Object, Constructor
**Tình huống:** một sản phẩm được tạo với tên rỗng hoặc giá âm. Constructor và phương thức cập nhật nên bảo vệ bất biến, không chỉ giao diện nhập liệu.
```java
final class Product {
    private final String id;
    private final String name;
    Product(String id, String name) {
        if (id == null || id.isBlank() || name == null || name.isBlank()) {
            throw new IllegalArgumentException("Thiếu mã hoặc tên");
        }
        this.id = id;
        this.name = name;
    }
}
```
**Tự luyện:** thử tên null, khoảng trắng và tên hợp lệ. **Hướng giải:** trạng thái không hợp lệ bị từ chối ngay, không tạo đối tượng nửa hợp lệ rồi sửa sau. this chỉ đối tượng hiện tại; constructor không có kiểu trả về.

## Kế thừa & Đa hình
**Tình huống:** nhiều loại sản phẩm có cách tính phí khác nhau. Lời gọi phương thức được chọn theo loại đối tượng thực khi có ghi đè.
```java
class Item { double fee() { return 10; } }
class DigitalItem extends Item {
    @Override double fee() { return 0; }
}
Item item = new DigitalItem();
System.out.println(item.fee()); // 0.0
```
**Tự luyện:** cho nhiều Item vào danh sách và cộng fee. **Hướng giải:** dùng ghi đè thay vì kiểm tra chuỗi tên lớp. Overload là nhiều chữ ký tham số, khác override. Không ép kiểu xuống nếu chưa biết đối tượng thật; ưu tiên hợp đồng ở lớp cha.

## Interface & Abstract Class
**Tình huống:** cần thay nơi lưu dữ liệu nhưng giữ nguyên nghiệp vụ. Interface mô tả hợp đồng; abstract class có thể chia sẻ trạng thái và phần triển khai khi phù hợp.
```java
interface PricePolicy { double price(double original); }
class HalfPrice implements PricePolicy {
    public double price(double original) { return original / 2; }
}
```
**Tự luyện:** thêm chính sách không giảm và kiểm thử qua biến PricePolicy. **Hướng giải:** nơi dùng không phụ thuộc chi tiết một lớp cụ thể; phương thức triển khai interface phải có mức truy cập phù hợp. Không chọn kế thừa chỉ để tránh viết vài dòng, nếu quan hệ đúng hơn là “sử dụng”.

## Try-catch & Custom Exception
**Tình huống:** lỗi bị bỏ qua bằng catch rỗng khiến chương trình vẫn báo lưu thành công. Chỉ bắt lỗi tại nơi có thể xử lý, bổ sung ngữ cảnh và giữ nguyên nguyên nhân khi chuyển tiếp.
```java
try {
    int quantity = Integer.parseInt("abc");
    System.out.println(quantity);
} catch (NumberFormatException error) {
    System.out.println("Số lượng phải là số nguyên");
}
```
**Tự luyện:** quy định lỗi nhập dữ liệu khác lỗi đọc file. **Hướng giải:** người dùng có thể sửa input, còn lỗi I/O cần thông báo phù hợp; không lộ thông tin nhạy cảm trong thông báo. Dùng try-with-resources cho tài nguyên AutoCloseable, không dựa vào việc đóng thủ công ở cuối đường chạy thành công.

## ArrayList & HashMap
**Tình huống:** hai sản phẩm cùng mã làm dữ liệu cũ bị ghi đè. Map.put có thể thay giá trị hiện có; muốn từ chối trùng cần kiểm tra hoặc dùng thao tác phù hợp.
```java
java.util.Map<String, String> products = new java.util.HashMap<>();
products.put("P01", "Bút");
if (products.putIfAbsent("P01", "Vở") != null) {
    System.out.println("Mã đã tồn tại");
}
```
**Tự luyện:** thêm, tìm mã không tồn tại và xóa khi duyệt danh sách. **Hướng giải:** không mặc định thứ tự HashMap; dùng iterator hoặc tạo danh sách mới khi cần lọc. Nhắc rõ ví dụ Map đơn luồng không tự giải quyết cạnh tranh ghi từ nhiều luồng.

## Dự án: Quản lý sản phẩm
**Bài thực hành:** quản lý mã duy nhất, tên, giá và số lượng; hỗ trợ thêm, tìm, cập nhật và xuất danh sách. Chia lớp dữ liệu, dịch vụ và nhập/xuất. Dùng BigDecimal hoặc đơn vị tiền nguyên theo quy ước bài tập thay vì tùy tiện dùng double cho tiền thực.

**Tự luyện:** tạo 8 ca: tên rỗng, mã trùng, giá âm, số lượng 0, tìm không thấy, dữ liệu hợp lệ, file thiếu và file hỏng. **Hướng giải:** xác định quy tắc số lượng 0 trước, kiểm tra trạng thái sau thao tác bị từ chối phải không đổi. Ghi rõ phần chưa triển khai, không coi việc chương trình biên dịch là đã kiểm thử đầy đủ.

# Tài liệu tham khảo
https://dev.java/learn/
