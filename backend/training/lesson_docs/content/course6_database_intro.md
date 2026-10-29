=== LESSON 46 ===
## Mục tiêu bài học
- Phân biệt cơ sở dữ liệu và hệ quản trị cơ sở dữ liệu.
- Mô tả bảng, hàng, cột, khóa chính và khóa ngoại.
- Nhận biết quan hệ một-một, một-nhiều và nhiều-nhiều.
- Phân biệt các nhóm câu lệnh SQL trong tài liệu.

## 1. Cơ sở dữ liệu là gì
Cơ sở dữ liệu (CSDL, database) là tập hợp dữ liệu có tổ chức, được lưu trữ có cấu trúc để dễ dàng truy xuất, cập nhật và quản
lý. Hệ quản trị cơ sở dữ liệu (DBMS — Database Management System) là phần mềm trung gian cho phép người dùng/ứng
dụng tương tác với dữ liệu mà không cần thao tác trực tiếp lên file lưu trữ vật lý.
## 2. CSDL quan hệ (Relational Database)
CSDL quan hệ tổ chức dữ liệu thành các bảng (table) gồm hàng (row/record) và cột (column/field), các bảng có thể liên kết
với nhau thông qua khóa (key). MySQL, PostgreSQL, SQL Server, Oracle là các hệ quản trị CSDL quan hệ phổ biến, đều dùng
ngôn ngữ SQL (Structured Query Language) để thao tác dữ liệu.
## 3. Khóa chính và khóa ngoại
Khóa chính (Primary Key) là một hoặc nhiều cột có giá trị duy nhất, không được trùng và không được rỗng (NULL), dùng để
định danh chính xác từng hàng trong bảng — ví dụ cột id tự động tăng. Khóa ngoại (Foreign Key) là cột trong một bảng
tham chiếu tới khóa chính của bảng khác, dùng để thiết lập mối quan hệ giữa các bảng, đảm bảo tính toàn vẹn dữ liệu (ví dụ
không thể thêm một đơn hàng với mã khách hàng không tồn tại).
## 4. Các loại quan hệ giữa bảng
Quan hệ một-một (1-1): mỗi hàng ở bảng A tương ứng đúng một hàng ở bảng B, ví dụ bảng Người dùng và bảng Hồ sơ chi
tiết. Quan hệ một-nhiều (1-N): một hàng ở bảng A liên kết với nhiều hàng ở bảng B, ví dụ một Khách hàng có nhiều Đơn
hàng — đây là loại quan hệ phổ biến nhất. Quan hệ nhiều-nhiều (N-N): cần một bảng trung gian (junction table) chứa hai
khóa ngoại trỏ tới cả hai bảng liên quan, ví dụ Học viên và Khóa học (một học viên học nhiều khóa, một khóa có nhiều học
viên) cần thêm bảng Ghi_danh ở giữa.
## 5. SQL và phân loại câu lệnh
SQL chia thành các nhóm câu lệnh: DDL (Data Definition Language — CREATE, ALTER, DROP: định nghĩa/thay đổi cấu trúc
bảng), DML (Data Manipulation Language — SELECT, INSERT, UPDATE, DELETE: thao tác dữ liệu), DCL (Data Control Language
— GRANT, REVOKE: phân quyền truy cập), TCL (Transaction Control Language — COMMIT, ROLLBACK: quản lý giao dịch).
## 6. Mở rộng: NoSQL và khi nào không chọn CSDL quan hệ
Ngoài CSDL quan hệ, còn có CSDL NoSQL (MongoDB, Redis, Cassandra) không tổ chức dữ liệu theo bảng cố định, phù hợp
khi dữ liệu có cấu trúc linh hoạt thay đổi liên tục, cần mở rộng theo chiều ngang (horizontal scaling) ở quy mô cực lớn, hoặc
chỉ cần lưu trữ khóa-giá trị đơn giản tốc độ cao. Với hầu hết ứng dụng web/quản lý thông thường (như hệ thống LMS học
trực tuyến), CSDL quan hệ vẫn là lựa chọn phù hợp và phổ biến nhất nhờ tính nhất quán dữ liệu chặt chẽ (ACID).

## Câu hỏi ôn tập và bài tập vận dụng
1. Phân biệt CSDL và DBMS. MySQL thuộc loại nào?
2. Vì sao khóa chính phải duy nhất và không NULL?
3. Thiết kế ba bảng học viên, khóa học và ghi danh: xác định khóa chính, khóa ngoại và loại quan hệ.
4. Phân loại CREATE, INSERT, GRANT và COMMIT theo chức năng.
5. Nêu một trường hợp cần cân nhắc lưu trữ khóa-giá trị thay cho bảng quan hệ.
