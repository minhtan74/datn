## MySQL — Học thêm về truy vấn, ràng buộc và giao dịch
Tài liệu bổ sung cho SELECT, JOIN, GROUP BY, view, chuẩn hóa và dự án CSDL học trực tuyến. Ví dụ dành cho MySQL 8.4 và bảng InnoDB; thực hành trong database thử.

## Mục tiêu học thêm
- Giải thích tác động của JOIN tới số dòng và thống kê
- Thiết kế ràng buộc chống dữ liệu trùng hoặc mất liên kết
- Sử dụng giao dịch cho thao tác có nhiều bước phụ thuộc

## 1. JOIN không chỉ ghép cột
Một khóa có nhiều học viên và nhiều bài học. Nếu JOIN cùng lúc hai quan hệ một-nhiều, số dòng có thể bị nhân lên. Với 3 học viên và 4 bài, kết quả có thể là 12 dòng chứ không phải 7.
```sql
SELECT c.id, COUNT(DISTINCT e.user_id) AS students,
       COUNT(DISTINCT l.id) AS lessons
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.id
LEFT JOIN chapters ch ON ch.course_id = c.id
LEFT JOIN lessons l ON l.chapter_id = ch.id
GROUP BY c.id;
```
DISTINCT phù hợp khi đếm mã duy nhất; không dùng SUM(DISTINCT amount) để chữa lỗi nhân dòng vì hai khoản tiền hợp lệ cùng giá trị sẽ bị gộp mất. Khi tính doanh thu cùng số bài, tổng hợp payments và lessons riêng trước rồi JOIN các kết quả tổng hợp.

## 2. NULL và điều kiện lọc
NULL biểu thị thiếu giá trị, không phải số 0 hay chuỗi rỗng. Dùng IS NULL, không dùng = NULL. COUNT(*) đếm dòng; COUNT(column) bỏ qua giá trị NULL.
Với LEFT JOIN, đưa điều kiện bảng phải xuống WHERE có thể loại các dòng không có bản ghi khớp, làm mất ý nghĩa giữ bảng trái.
```sql
SELECT c.id, COUNT(p.id) AS completed_payments
FROM courses c
LEFT JOIN payments p
  ON p.course_id = c.id AND p.status = 'completed'
GROUP BY c.id;
```
Khóa không có giao dịch thành công vẫn xuất hiện với số đếm 0. Nếu chuyển p.status='completed' xuống WHERE, khóa đó thường biến mất khỏi kết quả.

## 3. Khóa và chuẩn hóa
Một bản ghi ghi danh cần UNIQUE(user_id, course_id) để không ghi danh trùng. Kiểm tra trước bằng SELECT trong ứng dụng không đủ khi hai request chạy đồng thời; ràng buộc database là lớp bảo vệ cuối cùng.
Chuẩn hóa giảm dư thừa và lỗi cập nhật. Trong bảng ghi danh, tên khóa phụ thuộc course_id chứ không phụ thuộc toàn bộ cặp học viên/khóa; nên lưu tên tại courses. Tuy nhiên, lịch sử thanh toán có thể cần lưu giá mua tại thời điểm giao dịch để giá khóa thay đổi không làm sai lịch sử. Không xóa mọi dữ liệu lặp một cách máy móc: cần phân biệt dư thừa với snapshot nghiệp vụ.

## 4. Giao dịch và đồng thời
Khi xác nhận thanh toán, cập nhật trạng thái đơn và tạo quyền học cần được thực hiện nhất quán. Ví dụ dưới đây minh họa, cần điều chỉnh tên cột và xử lý ràng buộc theo schema thật:
```sql
START TRANSACTION;
SELECT id, user_id, course_id, status
FROM payments WHERE id = 123 FOR UPDATE;
-- Ứng dụng kiểm tra trạng thái, số tiền và tính hợp lệ trước khi tiếp tục.
UPDATE payments SET status = 'completed' WHERE id = 123 AND status = 'pending';
-- Ứng dụng chỉ thêm ghi danh khi đủ điều kiện nghiệp vụ.
COMMIT;
```
Không chạy nguyên ví dụ trên để xác nhận giao dịch thật. Luồng đầy đủ phải thêm ghi danh trong cùng giao dịch, xử lý lỗi bằng rollback và bảo đảm callback lặp không tạo quyền học trùng. FOR UPDATE cần giao dịch đang mở và engine hỗ trợ khóa hàng như InnoDB. Giao dịch không thay thế việc kiểm tra chữ ký thanh toán.

## 5. Chỉ mục và kế hoạch thực thi
Chỉ mục giúp một số truy vấn tìm/lọc/sắp xếp nhưng tăng chi phí ghi và dung lượng. Chỉ mục ghép cần xem thứ tự cột phù hợp với điều kiện truy vấn. Dùng EXPLAIN trước khi thêm chỉ mục và đo trên dữ liệu có kích thước phù hợp; bảng rất nhỏ không chứng minh được lợi ích rõ ràng.

## Bài tập và lời giải định hướng
1. Dễ: phân biệt COUNT(*) và COUNT(p.id) trong LEFT JOIN. Khóa chưa có thanh toán vẫn có một dòng kết quả JOIN, nhưng p.id là NULL nên COUNT(p.id)=0.
2. Trung bình: thống kê khóa không có học viên. LEFT JOIN enrollments và GROUP BY khóa, HAVING COUNT(e.id)=0; không đặt điều kiện khiến bảng trái bị loại.
3. Khó: hai callback đồng thời xác nhận cùng đơn. Thiết kế giao dịch khóa đơn, kiểm tra trạng thái và UNIQUE cho ghi danh; callback sau thấy đơn hoàn tất thì trả kết quả nhất quán, không tạo lại.

## Tiêu chí tự đánh giá và nguồn
Kiểm tra dữ liệu rỗng, khóa không có học viên, giao dịch cùng giá trị, callback lặp và lỗi giữa hai bước ghi. Giải thích được lý do COUNT bị nhân và chứng minh rollback không để đơn hoàn tất mà thiếu quyền học.
https://dev.mysql.com/doc/refman/8.4/en/join.html
https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html
https://dev.mysql.com/doc/refman/8.4/en/explain.html
