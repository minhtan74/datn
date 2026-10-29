# MySQL — mô hình dữ liệu, truy vấn và bài tập có hướng giải

Chỉ chạy bài thực hành trong database lab riêng do người học tạo. Ví dụ dùng tên bảng minh họa, không phải lệnh yêu cầu sửa database StudyOnline đang có dữ liệu thật. Với chương trình gửi SQL, dùng tham số theo driver, không nối trực tiếp dữ liệu người dùng.

## Khái niệm cơ sở dữ liệu
**Hỏi thực tế:** “Hai học sinh có cùng id được không?” Nếu id là khóa chính trong cùng bảng thì không: khóa chính định danh hàng, phải duy nhất và không NULL. Hai bảng khác nhau có thể có cùng giá trị số nhưng đó không tự là cùng thực thể.

**Hỏi nối tiếp:** “Bạn chưa xếp lớp thì mã lớp có để trống được không?” Đây là khóa ngoại, không phải khóa chính. Có thể để NULL nếu thiết kế cột cho phép và nghiệp vụ chấp nhận chưa xếp lớp. NOT NULL buộc có giá trị; giá trị khác NULL phải thỏa ràng buộc tham chiếu đang áp dụng. Nhiều học sinh được cùng mã lớp; đó là quan hệ một lớp–nhiều học sinh.

**Tự luyện:** vẽ bảng Lop và HocSinh. **Hướng giải:** HocSinh.id là khóa chính; HocSinh.lop_id tham chiếu Lop.id; không dùng tên làm khóa chính chỉ vì ví dụ chưa thấy trùng tên.

## Cài đặt MySQL & Workbench
**Tình huống:** Workbench mở được nhưng kết nối thất bại. Workbench là client; MySQL server phải chạy, đúng host/port, tài khoản và quyền. Phân biệt sai mật khẩu, server không chạy, firewall và database chưa tồn tại bằng thông báo lỗi.
```sql
SELECT VERSION();
SELECT DATABASE();
SHOW TABLES;
```
**Tự luyện:** kết nối lab, kiểm tra database hiện tại rồi mới chạy truy vấn. **Hướng giải:** không dùng tài khoản root trong ứng dụng chỉ vì dễ kết nối; cấp quyền tối thiểu phù hợp. Không import script có DROP DATABASE vào nơi cần giữ dữ liệu; sao lưu không thay thế việc xác nhận đúng database đích.

## Câu lệnh SELECT cơ bản
**Tình huống:** nhập tên O'Reilly làm hỏng SQL. Chuỗi có dấu nháy cần được truyền qua tham số của driver, không ghép chuỗi SQL bằng phép cộng hoặc f-string. Cú pháp placeholder tùy driver; không chép nhầm giữa các thư viện.
```sql
SELECT id, name
FROM students
WHERE name IS NOT NULL
ORDER BY name, id
LIMIT 20;
```
**Tự luyện:** lọc tên, sắp xếp ổn định và phân trang lab. **Hướng giải:** NULL được kiểm tra bằng IS NULL/IS NOT NULL, không bằng `= NULL`. Kết quả không có ORDER BY không được đảm bảo thứ tự; SELECT * tiện khám phá nhưng API nên chọn cột cần dùng và tránh lộ cột nhạy cảm.

## JOIN nhiều bảng
**Hỏi thực tế:** “Tìm học viên chưa ghi danh khóa nào bằng LEFT JOIN?” Bắt đầu từ học viên, giữ tất cả học viên rồi lọc phía ghi danh không khớp. Đừng đổi thành tìm khóa chưa có học viên: đó là bài toán ngược.
```sql
SELECT s.id, s.name
FROM students AS s
LEFT JOIN enrollments AS e ON e.student_id = s.id
WHERE e.student_id IS NULL;
```
**Tự luyện:** tạo học viên A chưa ghi danh, B có hai ghi danh, C có một ghi danh. **Hướng giải:** truy vấn trên chỉ trả A; INNER JOIN không thể giữ A. LEFT JOIN giữ bảng trái, cột bên phải NULL khi không khớp. Khi lọc trạng thái ghi danh, điều kiện trong ON và trong WHERE có thể tạo kết quả khác nhau; kiểm tra bằng dữ liệu không có dòng khớp.

## GROUP BY & Aggregate Function
**Tình huống:** đếm học viên theo khóa nhưng khóa rỗng vẫn có số 1. Sau LEFT JOIN, COUNT(*) đếm cả hàng bên trái chưa khớp; COUNT(e.id) chỉ đếm id phía ghi danh không NULL.
```sql
SELECT c.id, c.title, COUNT(e.id) AS student_count
FROM courses AS c
LEFT JOIN enrollments AS e ON e.course_id = c.id
GROUP BY c.id, c.title;
```
**Tự luyện:** khóa có 0, 1, 3 ghi danh và dữ liệu bị nhân dòng bởi JOIN khác. **Hướng giải:** đếm ở đúng mức dữ liệu hoặc dùng subquery tổng hợp trước; không thêm DISTINCT vô điều kiện chỉ để che JOIN sai. WHERE lọc hàng trước nhóm; HAVING lọc kết quả nhóm. AVG bỏ NULL nên phải nêu rõ cách xử lý người chưa có điểm.

## Subquery & View
**Tình huống:** cần tìm học viên không có ghi danh mà không muốn nhân dòng. NOT EXISTS thể hiện trực tiếp điều kiện không tồn tại.
```sql
SELECT s.id, s.name
FROM students AS s
WHERE NOT EXISTS (
    SELECT 1 FROM enrollments AS e WHERE e.student_id = s.id
);
```
**Tự luyện:** đối chiếu kết quả với bài LEFT JOIN. **Hướng giải:** hai cách đúng phải cho cùng tập học viên trên dữ liệu lab. Cẩn thận NOT IN khi subquery có NULL; View là truy vấn có tên, không mặc nhiên là bảng sao chép được cập nhật sẵn hoặc biện pháp tăng tốc mọi truy vấn.

## Chuẩn hoá dữ liệu (1NF-3NF)
**Tình huống:** lưu nhiều tên khóa trong một ô khiến sửa/tìm rất khó. Tách thực thể và quan hệ theo phụ thuộc dữ liệu: học viên, khóa, ghi danh. Khóa ghép của ghi danh hoặc unique(student_id, course_id) ngăn đăng ký trùng theo quy tắc nghiệp vụ.

**Tự luyện:** từ bảng gồm student_id, student_name, course_id, course_title và teacher_name, chỉ ra việc sửa tên khóa phải sửa nhiều dòng. **Hướng giải:** đưa tên khóa vào bảng courses, nối bằng course_id; tiếp tục xem giảng viên có định danh riêng không. Chuẩn hóa dựa phụ thuộc hàm, không chỉ dựa cảm giác “tách nhiều bảng là tốt”. Đo hiệu năng trước khi phi chuẩn hóa có chủ đích.

## Thiết kế ERD
**Tình huống:** chưa rõ quan hệ học viên–khóa là 1-N hay N-N. Một học viên học nhiều khóa, một khóa có nhiều học viên nên cần bảng ghi danh ở giữa. Ghi cả tính bắt buộc/tùy chọn và quy tắc xóa.

**Tự luyện:** xác định khóa chính, khóa ngoại và unique cho users, courses, enrollments. **Hướng giải:** mô tả điều gì xảy ra khi khóa đã có điểm bị xóa; không mặc định CASCADE phù hợp mọi dữ liệu lịch sử. Chỉ số hoặc khóa duy nhất hỗ trợ tính toàn vẹn, còn quyền ai được đọc/sửa vẫn phải được ứng dụng kiểm soát.

## Dự án: Thiết kế CSDL website học trực tuyến
**Bài thực hành:** thiết kế học viên, khóa, ghi danh, quiz và kết quả cho một lab. Viết truy vấn danh sách chưa ghi danh, số học viên mỗi khóa và điểm theo quy tắc đã chọn. Chưa nộp bài khác điểm 0; không biến thiếu dữ liệu thành kết luận trượt.

**Tự luyện:** tạo dữ liệu rỗng, trùng, khóa có hai học viên, một học viên làm nhiều lượt và một người chưa làm. **Hướng giải:** xác nhận quy tắc lấy điểm đầu/cuối/cao nhất/trung bình trước khi viết AVG. Thử transaction bằng rollback trong lab; kiểm tra cả bản ghi con. Đối chiếu tổng báo cáo với truy vấn độc lập để phát hiện nhân dòng do JOIN.

# Tài liệu tham khảo
https://dev.mysql.com/doc/refman/8.4/en/tutorial.html
