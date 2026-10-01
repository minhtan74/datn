=== LESSON 47 ===
## Mục tiêu bài học
- Phân biệt MySQL Server và MySQL Workbench
- Cài đặt MySQL và kết nối bằng Workbench
- Tạo database, bảng đầu tiên và kiểm tra kết nối

## 1. Các thành phần
MySQL Server là thành phần lưu trữ và xử lý dữ liệu, mặc định lắng nghe ở cổng 3306. MySQL Workbench là công cụ giao diện đồ họa để viết truy vấn, quản lý bảng và vẽ sơ đồ ERD. Tài khoản quản trị mặc định của MySQL có tên là `root`, mật khẩu do bạn đặt lúc cài.

## 2. Các bước cài đặt
1. Tải MySQL Installer từ trang chủ MySQL và chọn MySQL Server cùng MySQL Workbench.
2. Đặt mật khẩu cho tài khoản `root` và ghi nhớ cổng (mặc định 3306).
3. Đảm bảo dịch vụ MySQL đang chạy (trên Windows xem trong Services).
4. Mở Workbench, tạo kết nối mới tới `127.0.0.1:3306`, kiểm tra bằng Test Connection.

Lưu ý: nếu máy đã có MySQL khác (như XAMPP) dùng cổng 3306, hãy đổi một trong hai sang cổng khác, ví dụ 3307, để tránh xung đột.

## 3. Tạo database và bảng đầu tiên
Bộ ký tự nên dùng là `utf8mb4` để lưu được tiếng Việt và emoji.

```sql
CREATE DATABASE hoc_truc_tuyen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hoc_truc_tuyen;

CREATE TABLE hoc_vien (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ho_ten VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE,
  ngay_dang_ky DATE
);

SHOW TABLES;
DESCRIBE hoc_vien;
```

## 4. Kiểu dữ liệu thường dùng
Kiểu `INT` lưu số nguyên, `DECIMAL` lưu số thực chính xác thường dùng cho tiền tệ. Kiểu `VARCHAR` lưu chuỗi có độ dài thay đổi, `TEXT` lưu đoạn văn bản dài. Kiểu `DATE` lưu ngày, `DATETIME` và `TIMESTAMP` lưu cả ngày và giờ. Thuộc tính `AUTO_INCREMENT` tự tăng giá trị khoá chính khi thêm bản ghi mới.

## Tóm tắt
- MySQL Server lưu và xử lý dữ liệu (cổng 3306); Workbench là công cụ giao diện.
- Dùng `utf8mb4` để lưu tiếng Việt.
- `CREATE DATABASE`, `CREATE TABLE`, `SHOW TABLES`, `DESCRIBE` là các lệnh nền tảng.

## Bài tập vận dụng
1. Cài MySQL và Workbench, chụp lại kết nối thành công.
2. Tạo database và bảng `khoa_hoc` gồm id, tên, giá, ngày tạo.
3. Giải thích vì sao tiền tệ nên lưu bằng DECIMAL thay cho FLOAT.

=== LESSON 48 ===
## Mục tiêu bài học
- Viết câu lệnh SELECT truy vấn dữ liệu từ một bảng
- Lọc bằng WHERE, sắp xếp bằng ORDER BY, giới hạn bằng LIMIT
- Dùng các toán tử LIKE, IN, BETWEEN, IS NULL

## 1. Câu lệnh SELECT
Câu lệnh `SELECT` dùng để truy vấn, lấy dữ liệu từ một hoặc nhiều bảng. Ví dụ `SELECT name, price FROM products` lấy hai cột tên và giá của mọi sản phẩm. Dấu `*` trong `SELECT *` nghĩa là lấy tất cả các cột. Có thể đặt tên gọi khác cho cột bằng `AS`.

```sql
SELECT ho_ten, email FROM hoc_vien;
SELECT ho_ten AS ten, YEAR(ngay_dang_ky) AS nam FROM hoc_vien;
```

## 2. Lọc dữ liệu với WHERE
Mệnh đề `WHERE` dùng để lọc, chỉ giữ lại các bản ghi thoả điều kiện. Có thể kết hợp nhiều điều kiện bằng `AND`, `OR`, `NOT`.

```sql
SELECT * FROM khoa_hoc WHERE gia > 500000 AND trang_thai = 'published';
```

## 3. Các toán tử trong WHERE
Toán tử `LIKE` tìm theo mẫu, ký tự `%` đại diện cho chuỗi bất kỳ. Toán tử `IN` kiểm tra giá trị có nằm trong danh sách, `BETWEEN` kiểm tra giá trị nằm trong một khoảng. Để kiểm tra giá trị rỗng phải dùng `IS NULL`, không dùng dấu bằng.

```sql
SELECT * FROM hoc_vien WHERE ho_ten LIKE 'Nguyễn%';
SELECT * FROM khoa_hoc WHERE id IN (1, 3, 5);
SELECT * FROM khoa_hoc WHERE gia BETWEEN 100000 AND 500000;
SELECT * FROM hoc_vien WHERE email IS NULL;
```

## 4. Sắp xếp và giới hạn kết quả
Mệnh đề `ORDER BY` sắp xếp kết quả tăng dần (`ASC`) hoặc giảm dần (`DESC`). Từ khoá `DISTINCT` loại bỏ các dòng trùng lặp trong kết quả. Mệnh đề `LIMIT` giới hạn số dòng trả về, ví dụ `LIMIT 10` lấy 10 dòng đầu.

```sql
SELECT DISTINCT trinh_do FROM khoa_hoc;
SELECT * FROM khoa_hoc ORDER BY gia DESC LIMIT 5;
```

## Tóm tắt
- `SELECT cột FROM bảng` lấy dữ liệu; `*` lấy mọi cột.
- `WHERE` lọc dòng; `LIKE`, `IN`, `BETWEEN`, `IS NULL` là các toán tử phổ biến.
- `ORDER BY` sắp xếp, `LIMIT` giới hạn, `DISTINCT` bỏ trùng.

## Bài tập vận dụng
1. Lấy 5 khoá học có giá cao nhất.
2. Tìm các học viên có họ tên bắt đầu bằng chữ "Trần".
3. Giải thích vì sao phải dùng `IS NULL` thay vì `= NULL`.

=== LESSON 49 ===
## Mục tiêu bài học
- Hiểu phép JOIN và khi nào cần kết nối nhiều bảng
- Phân biệt INNER JOIN, LEFT JOIN và RIGHT JOIN
- Viết truy vấn kết nối từ ba bảng trở lên

## 1. JOIN là gì
JOIN là phép kết nối dùng để lấy dữ liệu từ nhiều bảng dựa trên cột liên quan, thường là khoá ngoại. Ví dụ kết nối bảng `lessons` với bảng `chapters` qua điều kiện `lessons.chapter_id = chapters.id`.

## 2. Phân biệt INNER JOIN và LEFT JOIN
`INNER JOIN` chỉ trả về các dòng có giá trị khớp ở cả hai bảng. `LEFT JOIN` trả về mọi dòng của bảng bên trái, các cột của bảng bên phải là `NULL` khi không có dòng khớp. `RIGHT JOIN` ngược lại với `LEFT JOIN`, giữ mọi dòng của bảng bên phải.

```sql
-- Khoá học kèm tên giảng viên
SELECT c.title, u.fullname
FROM courses c
INNER JOIN users u ON u.id = c.teacher_id;

-- Mọi khoá học, kể cả khoá chưa có học viên ghi danh
SELECT c.title, COUNT(e.id) AS so_hoc_vien
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.id
GROUP BY c.id, c.title;
```

## 3. Kết nối nhiều bảng
Có thể nối tiếp nhiều `JOIN` trong một truy vấn.

```sql
SELECT u.fullname, c.title, l.title AS bai_hoc
FROM users u
JOIN enrollments e ON e.user_id = u.id
JOIN courses c     ON c.id = e.course_id
JOIN chapters ch   ON ch.course_id = c.id
JOIN lessons l     ON l.chapter_id = ch.id;
```

## 4. Mẹo khi dùng JOIN
Luôn đặt bí danh cho bảng (`courses c`) và ghi rõ bí danh trước tên cột để tránh nhập nhằng. Điều kiện kết nối đặt ở mệnh đề `ON`. Dùng `LEFT JOIN` để tìm dữ liệu "không có": thêm điều kiện `WHERE bảng_phải.id IS NULL`, ví dụ khoá học chưa có học viên nào.

## Tóm tắt
- JOIN kết nối bảng theo cột liên quan (thường là khoá ngoại).
- `INNER JOIN` chỉ giữ dòng khớp; `LEFT JOIN` giữ mọi dòng bảng trái.
- Đặt bí danh bảng và điều kiện `ON` rõ ràng.

## Bài tập vận dụng
1. Liệt kê tên khoá học cùng tên giảng viên phụ trách.
2. Tìm các khoá học chưa có học viên nào (dùng LEFT JOIN và IS NULL).
3. Viết truy vấn liệt kê học viên, khoá học và số bài học trong khoá đó.

=== LESSON 50 ===
## Mục tiêu bài học
- Sử dụng các hàm tổng hợp COUNT, SUM, AVG, MIN, MAX
- Gom nhóm dữ liệu bằng GROUP BY
- Phân biệt WHERE và HAVING

## 1. Hàm tổng hợp
Hàm tổng hợp (aggregate function) là hàm tính toán trên một nhóm dòng và trả về một giá trị duy nhất. Các hàm phổ biến gồm `COUNT` (đếm), `SUM` (tính tổng), `AVG` (trung bình), `MIN` (nhỏ nhất) và `MAX` (lớn nhất).

## 2. Hàm COUNT
Hàm `COUNT` dùng để đếm số dòng trong kết quả truy vấn. `COUNT(*)` đếm mọi dòng, còn `COUNT(tên_cột)` chỉ đếm các dòng có giá trị khác `NULL` ở cột đó. Ví dụ `SELECT COUNT(*) FROM hoc_vien` cho biết bảng có bao nhiêu học viên.

```sql
SELECT COUNT(*) AS tong, AVG(gia) AS gia_tb, MAX(gia) AS gia_cao_nhat
FROM khoa_hoc;
```

## 3. GROUP BY
Mệnh đề `GROUP BY` dùng để gom các dòng có cùng giá trị thành nhóm, thường đi cùng hàm tổng hợp. Ví dụ đếm số học viên của từng khoá học:

```sql
SELECT course_id, COUNT(*) AS so_hoc_vien
FROM enrollments
GROUP BY course_id;
```

## 4. Phân biệt WHERE và HAVING
Điểm khác nhau giữa WHERE và HAVING là thời điểm lọc dữ liệu. `WHERE` lọc từng dòng trước khi gom nhóm và không dùng được hàm tổng hợp. `HAVING` lọc các nhóm sau khi đã `GROUP BY` và dùng được hàm tổng hợp, ví dụ `HAVING COUNT(*) > 5`.

```sql
SELECT course_id, COUNT(*) AS so_hoc_vien
FROM enrollments
WHERE enroll_date >= '2026-01-01'
GROUP BY course_id
HAVING COUNT(*) >= 5
ORDER BY so_hoc_vien DESC;
```

Thứ tự viết các mệnh đề: `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`.

## Tóm tắt
- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` tính toán trên nhóm dòng; `COUNT(*)` đếm cả dòng NULL.
- `GROUP BY` gom nhóm; `HAVING` lọc nhóm, `WHERE` lọc dòng.
- Giữ đúng thứ tự các mệnh đề khi viết truy vấn.

## Bài tập vận dụng
1. Đếm số bài học của từng khoá học.
2. Tính điểm trung bình quiz của từng học viên và chỉ giữ người có trung bình từ 5 trở lên.
3. Giải thích khác biệt giữa `WHERE` và `HAVING` kèm ví dụ.

=== LESSON 51 ===
## Mục tiêu bài học
- Viết truy vấn con (subquery) trong WHERE, FROM và SELECT
- Tạo và sử dụng View
- Hiểu khi nào nên dùng subquery, JOIN hay View

## 1. Truy vấn con
Subquery (truy vấn con) là câu truy vấn đặt bên trong một câu truy vấn khác. Truy vấn con có thể nằm trong `WHERE`, `FROM` hoặc `SELECT`. Ví dụ tìm sản phẩm có giá cao hơn giá trung bình:

```sql
SELECT title, price
FROM courses
WHERE price > (SELECT AVG(price) FROM courses);
```

## 2. Truy vấn con với IN và EXISTS
`IN` so sánh với danh sách giá trị do truy vấn con trả về; `EXISTS` kiểm tra truy vấn con có trả về dòng nào không, thường nhanh hơn khi chỉ cần biết có hay không.

```sql
-- Học viên đã ghi danh ít nhất một khoá
SELECT fullname FROM users u
WHERE EXISTS (SELECT 1 FROM enrollments e WHERE e.user_id = u.id);

-- Khoá học có ít nhất một quiz
SELECT title FROM courses
WHERE id IN (SELECT course_id FROM quizzes);
```

## 3. View
View là bảng ảo được tạo từ kết quả của một câu truy vấn, khai báo bằng `CREATE VIEW`. View không lưu dữ liệu riêng mà lấy dữ liệu từ các bảng gốc mỗi khi được truy vấn. View giúp đơn giản hoá truy vấn phức tạp và giới hạn cột mà người dùng được xem.

```sql
CREATE VIEW v_thong_ke_khoa_hoc AS
SELECT c.id, c.title, COUNT(e.id) AS so_hoc_vien
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.id
GROUP BY c.id, c.title;

SELECT * FROM v_thong_ke_khoa_hoc WHERE so_hoc_vien > 0;
DROP VIEW v_thong_ke_khoa_hoc;
```

## 4. Chọn cách viết phù hợp
Dùng JOIN khi cần lấy cột từ nhiều bảng; dùng subquery khi cần so sánh với kết quả tổng hợp hoặc kiểm tra tồn tại; dùng View khi một truy vấn được dùng lại nhiều lần hoặc cần ẩn bớt dữ liệu nhạy cảm. Với dữ liệu lớn nên kiểm tra kế hoạch thực thi bằng `EXPLAIN`.

## Tóm tắt
- Subquery là truy vấn lồng trong `WHERE`, `FROM` hoặc `SELECT`.
- `IN` so với danh sách; `EXISTS` kiểm tra tồn tại.
- View là bảng ảo không lưu dữ liệu, giúp đơn giản hoá và hạn chế quyền xem.

## Bài tập vận dụng
1. Tìm các khoá học có giá cao hơn giá trung bình bằng subquery.
2. Tạo view liệt kê học viên kèm số khoá học đã ghi danh.
3. Giải thích View có lưu dữ liệu riêng hay không.

=== LESSON 52 ===
## Mục tiêu bài học
- Hiểu vì sao cần chuẩn hoá dữ liệu
- Phân biệt các dạng chuẩn 1NF, 2NF và 3NF
- Áp dụng chuẩn hoá để tách một bảng thành nhiều bảng

## 1. Chuẩn hoá là gì
Chuẩn hoá (normalization) là quá trình tổ chức bảng để giảm dư thừa dữ liệu và tránh lỗi cập nhật. Dư thừa dữ liệu gây ra các dị thường (anomaly) khi thêm, sửa và xoá: ví dụ lưu tên khoá học lặp lại ở hàng nghìn dòng thì sửa tên phải sửa từng dòng. Các dạng chuẩn thường dùng là 1NF, 2NF và 3NF.

## 2. Dạng chuẩn 1NF
Bảng đạt dạng chuẩn 1NF khi mọi cột chỉ chứa giá trị nguyên tố, không có nhóm lặp. Ví dụ cột số điện thoại chứa nhiều số cách nhau bởi dấu phẩy là vi phạm 1NF; cần tách thành các dòng hoặc bảng riêng.

## 3. Dạng chuẩn 2NF
Bảng đạt dạng chuẩn 2NF khi đạt 1NF và mọi cột không khoá phụ thuộc đầy đủ vào toàn bộ khoá chính. 2NF chỉ cần xét khi khoá chính gồm nhiều cột, loại bỏ phụ thuộc vào một phần của khoá.

Ví dụ bảng `dang_ky(ma_hv, ma_khoa, ten_khoa, ngay)` có khoá chính (ma_hv, ma_khoa): cột `ten_khoa` chỉ phụ thuộc `ma_khoa` nên vi phạm 2NF. Tách `ten_khoa` ra bảng `khoa_hoc`.

## 4. Dạng chuẩn 3NF
Bảng đạt dạng chuẩn 3NF khi đạt 2NF và không có phụ thuộc bắc cầu giữa các cột không khoá. Phụ thuộc bắc cầu nghĩa là cột C phụ thuộc cột B, còn cột B lại phụ thuộc khoá chính A.

Ví dụ bảng `hoc_vien(ma_hv, ten, ma_lop, ten_lop)`: `ten_lop` phụ thuộc `ma_lop`, còn `ma_lop` phụ thuộc `ma_hv` nên có phụ thuộc bắc cầu. Tách bảng `lop(ma_lop, ten_lop)`.

```sql
CREATE TABLE lop (ma_lop INT PRIMARY KEY, ten_lop VARCHAR(100));
CREATE TABLE hoc_vien (
  ma_hv INT PRIMARY KEY, ten VARCHAR(100),
  ma_lop INT, FOREIGN KEY (ma_lop) REFERENCES lop(ma_lop)
);
```

## Lưu ý
Chuẩn hoá quá mức có thể làm truy vấn phải JOIN nhiều bảng. Trong thực tế đôi khi cố ý phi chuẩn hoá một phần để tăng tốc độ đọc, nhưng cần hiểu rõ đánh đổi.

## Tóm tắt
- Chuẩn hoá giảm dư thừa và tránh dị thường khi thêm, sửa, xoá.
- 1NF: giá trị nguyên tố; 2NF: không phụ thuộc một phần vào khoá; 3NF: không phụ thuộc bắc cầu.
- Tách bảng và nối lại bằng khoá ngoại.

## Bài tập vận dụng
1. Cho bảng đơn hàng lưu nhiều sản phẩm trong một ô; đưa về 1NF.
2. Chỉ ra phụ thuộc bắc cầu trong bảng `nhan_vien(ma_nv, ten, ma_pb, ten_pb)` và tách bảng.
3. Nêu một trường hợp nên phi chuẩn hoá và lý do.

=== LESSON 53 ===
## Mục tiêu bài học
- Hiểu ERD và các thành phần thực thể, thuộc tính, liên kết
- Xác định các kiểu liên kết 1-1, 1-N, N-N
- Chuyển ERD thành các bảng trong MySQL

## 1. Sơ đồ ERD
ERD (Entity Relationship Diagram) là sơ đồ thực thể - liên kết dùng để mô hình hoá cơ sở dữ liệu trước khi tạo bảng. Thực thể (entity) là đối tượng cần lưu trữ, ví dụ học viên hoặc khoá học. Thuộc tính là đặc điểm của thực thể (họ tên, email). Liên kết thể hiện mối quan hệ giữa các thực thể.

## 2. Các kiểu liên kết
Các kiểu liên kết gồm một - một (1-1), một - nhiều (1-N) và nhiều - nhiều (N-N).
- **1-1**: mỗi người dùng có một hồ sơ.
- **1-N**: một giảng viên phụ trách nhiều khoá học, mỗi khoá thuộc một giảng viên.
- **N-N**: một học viên học nhiều khoá và một khoá có nhiều học viên.

## 3. Chuyển ERD sang bảng
- Liên kết 1-N: đặt khoá ngoại ở phía "nhiều" (`courses.teacher_id` tham chiếu `users.id`).
- Liên kết N-N: tách thành một bảng trung gian chứa hai khoá ngoại, ví dụ bảng `enrollments` gồm `user_id` và `course_id`.
- Liên kết 1-1: đặt khoá ngoại có ràng buộc `UNIQUE`, hoặc gộp hai bảng.

```sql
CREATE TABLE enrollments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  course_id INT NOT NULL,
  enroll_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, course_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

## 4. Quy trình thiết kế
Liệt kê thực thể từ yêu cầu bài toán, xác định thuộc tính và khoá chính, xác định liên kết giữa các thực thể, vẽ ERD (có thể dùng Workbench hoặc draw.io), kiểm tra chuẩn hoá đến 3NF rồi mới tạo bảng.

## Tóm tắt
- ERD gồm thực thể, thuộc tính và liên kết.
- 1-N đặt khoá ngoại phía nhiều; N-N cần bảng trung gian.
- Thiết kế ERD và chuẩn hoá trước khi tạo bảng.

## Bài tập vận dụng
1. Vẽ ERD cho hệ thống thư viện gồm sách, độc giả và phiếu mượn.
2. Chuyển ERD đó thành các câu lệnh CREATE TABLE có khoá ngoại.
3. Giải thích vì sao liên kết nhiều - nhiều cần bảng trung gian.

=== LESSON 54 ===
## Mục tiêu bài học
- Thiết kế cơ sở dữ liệu hoàn chỉnh cho website học trực tuyến
- Áp dụng ERD, chuẩn hoá và khoá ngoại vào một hệ thống thực tế
- Viết một số truy vấn thống kê từ CSDL đã thiết kế

## 1. Yêu cầu hệ thống
Website cho phép giảng viên tạo khoá học gồm các chương và bài học, học viên ghi danh, học bài, làm quiz trắc nghiệm và theo dõi tiến độ; quản trị viên xem thống kê và thanh toán.

## 2. Các bảng chính
Các bảng chính gồm `users`, `courses`, `chapters`, `lessons`, `quizzes`, `questions` và `results`.
- `users(id, fullname, email, password, role)` với vai trò admin, teacher hoặc student.
- `courses(id, teacher_id, title, description, price, status)`.
- `chapters(id, course_id, chapter_name, order_index)` và `lessons(id, chapter_id, title, video_url, document_url, order_index)`.
- `quizzes(id, course_id, title)`, `questions(id, quiz_id, content, option_a..d, correct_answer)`.
- `results(id, user_id, quiz_id, score, total, submit_time)`.

## 3. Các liên kết
Bảng `enrollments` là bảng trung gian thể hiện quan hệ nhiều - nhiều giữa học viên và khoá học. Bảng `lessons` có khoá ngoại `chapter_id` tham chiếu tới bảng `chapters` theo quan hệ một - nhiều; `chapters` có khoá ngoại `course_id` tham chiếu `courses`. Bảng `lesson_progress(user_id, lesson_id, is_completed, watched_sec)` lưu tiến độ học của từng học viên trên từng bài.

## 4. Truy vấn thống kê mẫu

```sql
-- Số học viên của từng khoá học
SELECT c.title, COUNT(e.id) AS so_hoc_vien
FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id
GROUP BY c.id, c.title
ORDER BY so_hoc_vien DESC;

-- Điểm trung bình quiz của từng học viên
SELECT u.fullname, ROUND(AVG(r.score * 100.0 / r.total), 1) AS diem_tb
FROM results r JOIN users u ON u.id = r.user_id
GROUP BY u.id, u.fullname;

-- Tỉ lệ hoàn thành bài học của học viên trong một khoá
SELECT COUNT(DISTINCT CASE WHEN lp.is_completed = 1 THEN l.id END) * 100.0 / COUNT(DISTINCT l.id) AS ti_le
FROM chapters ch JOIN lessons l ON l.chapter_id = ch.id
LEFT JOIN lesson_progress lp ON lp.lesson_id = l.id AND lp.user_id = 6
WHERE ch.course_id = 1;
```

## Tóm tắt
- Hệ thống học trực tuyến xoay quanh người dùng, khoá học, chương, bài, quiz và kết quả.
- Liên kết nhiều - nhiều giữa học viên và khoá học dùng bảng `enrollments`.
- Các báo cáo thống kê dựa trên JOIN, GROUP BY và hàm tổng hợp.

## Bài tập vận dụng
1. Vẽ ERD đầy đủ cho hệ thống và tạo các bảng bằng MySQL.
2. Thêm bảng `payments` lưu giao dịch thanh toán khoá học và các khoá ngoại phù hợp.
3. Viết truy vấn tính doanh thu theo từng khoá học.
