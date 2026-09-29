-- =========================================================
-- SEED DATA cho STUDYONLINE_DB
-- Chủ đề: Nền tảng học lập trình trực tuyến
-- Cách dùng: Chạy SAU KHI đã chạy studyonline_db.sql
--            và migration_add_payments.sql
-- =========================================================

USE studyonline_db;

SET FOREIGN_KEY_CHECKS = 0;

-- (Admin id = 1 đã được tạo sẵn trong studyonline_db.sql)

-- =========================================================
-- 1. USERS  (id 2 -> 15)
-- =========================================================

INSERT INTO users (fullname, email, password, role, avatar, bio, is_active) VALUES
-- Giảng viên (id 2-5)
('Nguyễn Văn An',   'an.nguyen@studyonline.vn',   '123456', 'teacher', 'avatars/teacher_an.jpg',
 'Giảng viên Python với 8 năm kinh nghiệm phát triển backend.', 1),
('Trần Thị Bình',   'binh.tran@studyonline.vn',   '123456', 'teacher', 'avatars/teacher_binh.jpg',
 'Frontend Developer, chuyên JavaScript, React và UI/UX.', 1),
('Lê Văn Cường',    'cuong.le@studyonline.vn',    '123456', 'teacher', 'avatars/teacher_cuong.jpg',
 'Kỹ sư backend Java, từng làm việc tại nhiều dự án doanh nghiệp lớn.', 1),
('Phạm Thị Duyên',  'duyen.pham@studyonline.vn',  '123456', 'teacher', 'avatars/teacher_duyen.jpg',
 'Chuyên gia cơ sở dữ liệu, quản trị hệ thống MySQL/PostgreSQL.', 1),

-- Học viên (id 6-15)
('Hoàng Văn Em',    'em.hoang@gmail.com',    '123456', 'student', 'avatars/student_em.jpg',    'Sinh viên năm 3, đam mê lập trình web.', 1),
('Vũ Thị Phương',   'phuong.vu@gmail.com',   '123456', 'student', 'avatars/student_phuong.jpg', 'Đang chuyển ngành sang IT.', 1),
('Đặng Văn Giang',  'giang.dang@gmail.com',  '123456', 'student', 'avatars/student_giang.jpg',  'Học lập trình để tự động hoá công việc.', 1),
('Bùi Thị Hoa',     'hoa.bui@gmail.com',     '123456', 'student', 'avatars/student_hoa.jpg',    'Yêu thích thiết kế web và giao diện.', 1),
('Đỗ Văn Khôi',     'khoi.do@gmail.com',     '123456', 'student', 'avatars/student_khoi.jpg',   'Mới bắt đầu học lập trình.', 1),
('Ngô Thị Lan',     'lan.ngo@gmail.com',     '123456', 'student', 'avatars/student_lan.jpg',    'Sinh viên CNTT năm 2.', 1),
('Dương Văn Minh',  'minh.duong@gmail.com',  '123456', 'student', 'avatars/student_minh.jpg',   'Muốn trở thành Fullstack Developer.', 1),
('Lý Thị Ngọc',     'ngoc.ly@gmail.com',     '123456', 'student', 'avatars/student_ngoc.jpg',   'Đang ôn thi chứng chỉ lập trình.', 1),
('Phan Văn Phúc',   'phuc.phan@gmail.com',   '123456', 'student', 'avatars/student_phuc.jpg',   'Tự học lập trình qua các khoá online.', 0),
('Trịnh Thị Quỳnh', 'quynh.trinh@gmail.com', '123456', 'student', 'avatars/student_quynh.jpg',  'Yêu thích cơ sở dữ liệu và phân tích số liệu.', 1);

-- =========================================================
-- 2. COURSES  (id 1 -> 6)
-- =========================================================

INSERT INTO courses (teacher_id, title, slug, description, thumbnail, price, level, status) VALUES
(2, 'Python Cơ Bản Cho Người Mới Bắt Đầu', 'python-co-ban',
 'Khoá học giúp bạn nắm vững cú pháp Python, cấu trúc điều khiển, hàm và lập trình hướng đối tượng cơ bản.',
 'thumbnails/python-co-ban.jpg', 599000, 'beginner', 'published'),

(3, 'JavaScript Từ Zero Đến Hero', 'javascript-tu-zero-den-hero',
 'Học JavaScript từ cơ bản đến nâng cao: DOM, sự kiện, ES6+, bất đồng bộ và xây dựng ứng dụng thực tế.',
 'thumbnails/javascript-hero.jpg', 699000, 'beginner', 'published'),

(4, 'Lập Trình Java Căn Bản', 'lap-trinh-java-can-ban',
 'Nắm vững Java: cú pháp, OOP, xử lý ngoại lệ và Collection Framework để xây dựng ứng dụng backend.',
 'thumbnails/java-can-ban.jpg', 799000, 'intermediate', 'published'),

(3, 'HTML & CSS Nhập Môn', 'html-css-nhap-mon',
 'Khoá học miễn phí giúp bạn xây dựng nền tảng HTML, CSS và thiết kế giao diện responsive.',
 'thumbnails/html-css.jpg', 0, 'beginner', 'published'),

(3, 'ReactJS Chuyên Sâu', 'reactjs-chuyen-sau',
 'Xây dựng ứng dụng thực tế với ReactJS: Hooks nâng cao, quản lý state, tối ưu hiệu năng.',
 'thumbnails/reactjs-pro.jpg', 899000, 'advanced', 'published'),

(5, 'MySQL & Thiết Kế Cơ Sở Dữ Liệu', 'mysql-thiet-ke-csdl',
 'Học cách thiết kế cơ sở dữ liệu chuẩn hoá và viết truy vấn SQL hiệu quả với MySQL.',
 'thumbnails/mysql-database.jpg', 499000, 'intermediate', 'published');

-- =========================================================
-- 3. CHAPTERS  (id 1 -> 18)
-- =========================================================

INSERT INTO chapters (course_id, chapter_name, order_index) VALUES
-- Course 1: Python (chapters 1-3)
(1, 'Làm Quen Với Python', 1),
(1, 'Cấu Trúc Điều Khiển & Hàm', 2),
(1, 'Lập Trình Hướng Đối Tượng Cơ Bản', 3),

-- Course 2: JavaScript (chapters 4-6)
(2, 'Nhập Môn JavaScript', 1),
(2, 'DOM & Xử Lý Sự Kiện', 2),
(2, 'JavaScript Hiện Đại (ES6+)', 3),

-- Course 3: Java (chapters 7-9)
(3, 'Cú Pháp Cơ Bản Java', 1),
(3, 'Lập Trình Hướng Đối Tượng Trong Java', 2),
(3, 'Xử Lý Ngoại Lệ & Collection', 3),

-- Course 4: HTML/CSS (chapters 10-12)
(4, 'HTML Cơ Bản', 1),
(4, 'CSS Cơ Bản', 2),
(4, 'Responsive Design', 3),

-- Course 5: ReactJS (chapters 13-15)
(5, 'React Cơ Bản', 1),
(5, 'State Management & Hooks Nâng Cao', 2),
(5, 'Xây Dựng Ứng Dụng Thực Tế', 3),

-- Course 6: MySQL (chapters 16-18)
(6, 'Nhập Môn Cơ Sở Dữ Liệu', 1),
(6, 'Truy Vấn SQL Nâng Cao', 2),
(6, 'Thiết Kế Database Chuẩn Hoá', 3);

-- =========================================================
-- 4. LESSONS  (id 1 -> 54)
-- =========================================================

INSERT INTO lessons (chapter_id, title, description, video_url, document_url, duration, order_index, is_free, status) VALUES
-- Chapter 1: Làm Quen Với Python (lessons 1-3)
(1, 'Cài đặt Python & IDE', 'Hướng dẫn cài đặt Python và VS Code.', 'videos/py_01.mp4', 'docs/py_01.pdf', 600, 1, 1, 'published'),
(1, 'Biến và kiểu dữ liệu', 'Tìm hiểu về biến, kiểu dữ liệu cơ bản trong Python.', 'videos/py_02.mp4', 'docs/py_02.pdf', 720, 2, 0, 'published'),
(1, 'Toán tử trong Python', 'Các loại toán tử số học, so sánh, logic.', 'videos/py_03.mp4', 'docs/py_03.pdf', 540, 3, 0, 'published'),

-- Chapter 2: Cấu Trúc Điều Khiển & Hàm (lessons 4-6)
(2, 'Câu lệnh if - else', 'Cấu trúc rẽ nhánh trong Python.', 'videos/py_04.mp4', 'docs/py_04.pdf', 660, 1, 0, 'published'),
(2, 'Vòng lặp for, while', 'Cách sử dụng vòng lặp trong Python.', 'videos/py_05.mp4', 'docs/py_05.pdf', 780, 2, 0, 'published'),
(2, 'Định nghĩa và sử dụng hàm', 'Cách viết hàm, tham số, giá trị trả về.', 'videos/py_06.mp4', 'docs/py_06.pdf', 700, 3, 0, 'published'),

-- Chapter 3: OOP cơ bản (lessons 7-9)
(3, 'Class và Object', 'Khái niệm lớp và đối tượng trong Python.', 'videos/py_07.mp4', 'docs/py_07.pdf', 800, 1, 0, 'published'),
(3, 'Kế thừa (Inheritance)', 'Tính kế thừa trong lập trình hướng đối tượng.', 'videos/py_08.mp4', 'docs/py_08.pdf', 750, 2, 0, 'published'),
(3, 'Dự án nhỏ: Quản lý sinh viên', 'Áp dụng OOP xây dựng chương trình quản lý sinh viên.', 'videos/py_09.mp4', 'docs/py_09.pdf', 900, 3, 0, 'published'),

-- Chapter 4: Nhập Môn JavaScript (lessons 10-12)
(4, 'JavaScript là gì?', 'Giới thiệu tổng quan về JavaScript.', 'videos/js_01.mp4', 'docs/js_01.pdf', 500, 1, 1, 'published'),
(4, 'Biến, kiểu dữ liệu & toán tử', 'Var, let, const và các kiểu dữ liệu trong JS.', 'videos/js_02.mp4', 'docs/js_02.pdf', 650, 2, 0, 'published'),
(4, 'Hàm trong JavaScript', 'Function declaration, function expression, arrow function.', 'videos/js_03.mp4', 'docs/js_03.pdf', 700, 3, 0, 'published'),

-- Chapter 5: DOM & Sự kiện (lessons 13-15)
(5, 'Tổng quan về DOM', 'DOM là gì và cách thao tác với DOM.', 'videos/js_04.mp4', 'docs/js_04.pdf', 620, 1, 0, 'published'),
(5, 'Xử lý sự kiện click, submit', 'Event listener và xử lý sự kiện người dùng.', 'videos/js_05.mp4', 'docs/js_05.pdf', 680, 2, 0, 'published'),
(5, 'Dự án: To-do List', 'Xây dựng ứng dụng to-do list bằng JavaScript thuần.', 'videos/js_06.mp4', 'docs/js_06.pdf', 900, 3, 0, 'published'),

-- Chapter 6: ES6+ (lessons 16-18)
(6, 'Arrow function & Destructuring', 'Cú pháp ES6 giúp code ngắn gọn hơn.', 'videos/js_07.mp4', 'docs/js_07.pdf', 640, 1, 0, 'published'),
(6, 'Promise & Async/Await', 'Xử lý bất đồng bộ trong JavaScript.', 'videos/js_08.mp4', 'docs/js_08.pdf', 760, 2, 0, 'published'),
(6, 'Module & Fetch API', 'Import/export module và gọi API bằng fetch.', 'videos/js_09.mp4', 'docs/js_09.pdf', 700, 3, 0, 'published'),

-- Chapter 7: Cú pháp cơ bản Java (lessons 19-21)
(7, 'Cài đặt JDK & IntelliJ', 'Chuẩn bị môi trường lập trình Java.', 'videos/java_01.mp4', 'docs/java_01.pdf', 600, 1, 1, 'published'),
(7, 'Biến, kiểu dữ liệu trong Java', 'Kiểu dữ liệu nguyên thuỷ và tham chiếu.', 'videos/java_02.mp4', 'docs/java_02.pdf', 650, 2, 0, 'published'),
(7, 'Cấu trúc điều khiển', 'If-else, switch-case, vòng lặp trong Java.', 'videos/java_03.mp4', 'docs/java_03.pdf', 700, 3, 0, 'published'),

-- Chapter 8: OOP Java (lessons 22-24)
(8, 'Class, Object, Constructor', 'Khái niệm lớp, đối tượng và constructor.', 'videos/java_04.mp4', 'docs/java_04.pdf', 750, 1, 0, 'published'),
(8, 'Kế thừa & Đa hình', 'Inheritance và Polymorphism trong Java.', 'videos/java_05.mp4', 'docs/java_05.pdf', 800, 2, 0, 'published'),
(8, 'Interface & Abstract Class', 'Sự khác biệt và cách sử dụng interface, abstract class.', 'videos/java_06.mp4', 'docs/java_06.pdf', 780, 3, 0, 'published'),

-- Chapter 9: Exception & Collection (lessons 25-27)
(9, 'Try-catch & Custom Exception', 'Xử lý ngoại lệ trong Java.', 'videos/java_07.mp4', 'docs/java_07.pdf', 640, 1, 0, 'published'),
(9, 'ArrayList & HashMap', 'Làm việc với Collection Framework.', 'videos/java_08.mp4', 'docs/java_08.pdf', 700, 2, 0, 'published'),
(9, 'Dự án: Quản lý sản phẩm', 'Ứng dụng console quản lý sản phẩm bằng Java.', 'videos/java_09.mp4', 'docs/java_09.pdf', 900, 3, 0, 'published'),

-- Chapter 10: HTML cơ bản (lessons 28-30)
(10, 'Cấu trúc tài liệu HTML', 'Thẻ HTML cơ bản và cấu trúc trang.', 'videos/html_01.mp4', 'docs/html_01.pdf', 500, 1, 1, 'published'),
(10, 'Form và bảng biểu', 'Thẻ form, input, table trong HTML.', 'videos/html_02.mp4', 'docs/html_02.pdf', 600, 2, 1, 'published'),
(10, 'Semantic HTML', 'Các thẻ ngữ nghĩa: header, section, article...', 'videos/html_03.mp4', 'docs/html_03.pdf', 550, 3, 0, 'published'),

-- Chapter 11: CSS cơ bản (lessons 31-33)
(11, 'Selector & thuộc tính CSS', 'Cách chọn phần tử và áp dụng style.', 'videos/css_01.mp4', 'docs/css_01.pdf', 620, 1, 0, 'published'),
(11, 'Box Model & Flexbox', 'Hiểu về box model và bố cục Flexbox.', 'videos/css_02.mp4', 'docs/css_02.pdf', 700, 2, 0, 'published'),
(11, 'CSS Grid', 'Xây dựng bố cục bằng CSS Grid.', 'videos/css_03.mp4', 'docs/css_03.pdf', 680, 3, 0, 'published'),

-- Chapter 12: Responsive Design (lessons 34-36)
(12, 'Media Query', 'Thiết kế responsive với media query.', 'videos/css_04.mp4', 'docs/css_04.pdf', 640, 1, 0, 'published'),
(12, 'Mobile First Design', 'Nguyên tắc thiết kế ưu tiên mobile.', 'videos/css_05.mp4', 'docs/css_05.pdf', 600, 2, 0, 'published'),
(12, 'Dự án: Landing Page Responsive', 'Xây dựng landing page hoàn chỉnh, responsive.', 'videos/css_06.mp4', 'docs/css_06.pdf', 900, 3, 0, 'published'),

-- Chapter 13: React cơ bản (lessons 37-39)
(13, 'Giới thiệu React & JSX', 'React là gì, cách JSX hoạt động.', 'videos/react_01.mp4', 'docs/react_01.pdf', 600, 1, 1, 'published'),
(13, 'Component & Props', 'Xây dựng component và truyền dữ liệu qua props.', 'videos/react_02.mp4', 'docs/react_02.pdf', 700, 2, 0, 'published'),
(13, 'State & useState', 'Quản lý trạng thái component với useState.', 'videos/react_03.mp4', 'docs/react_03.pdf', 720, 3, 0, 'published'),

-- Chapter 14: Hooks nâng cao (lessons 40-42)
(14, 'useEffect & vòng đời component', 'Xử lý side-effect trong React.', 'videos/react_04.mp4', 'docs/react_04.pdf', 750, 1, 0, 'published'),
(14, 'useContext & useReducer', 'Quản lý state phức tạp với Context và Reducer.', 'videos/react_05.mp4', 'docs/react_05.pdf', 800, 2, 0, 'published'),
(14, 'Custom Hooks', 'Xây dựng custom hook để tái sử dụng logic.', 'videos/react_06.mp4', 'docs/react_06.pdf', 700, 3, 0, 'published'),

-- Chapter 15: Dự án thực tế (lessons 43-45)
(15, 'Kết nối API với Axios', 'Gọi API và xử lý dữ liệu trong React.', 'videos/react_07.mp4', 'docs/react_07.pdf', 780, 1, 0, 'published'),
(15, 'Routing với React Router', 'Điều hướng nhiều trang trong ứng dụng React.', 'videos/react_08.mp4', 'docs/react_08.pdf', 700, 2, 0, 'published'),
(15, 'Dự án: Trang quản lý khoá học', 'Xây dựng ứng dụng quản lý khoá học hoàn chỉnh.', 'videos/react_09.mp4', 'docs/react_09.pdf', 1000, 3, 0, 'published'),

-- Chapter 16: Nhập môn CSDL (lessons 46-48)
(16, 'Khái niệm cơ sở dữ liệu', 'CSDL quan hệ, bảng, khoá chính, khoá ngoại.', 'videos/sql_01.mp4', 'docs/sql_01.pdf', 550, 1, 1, 'published'),
(16, 'Cài đặt MySQL & Workbench', 'Hướng dẫn cài đặt công cụ làm việc với MySQL.', 'videos/sql_02.mp4', 'docs/sql_02.pdf', 500, 2, 1, 'published'),
(16, 'Câu lệnh SELECT cơ bản', 'Truy vấn dữ liệu cơ bản với SELECT.', 'videos/sql_03.mp4', 'docs/sql_03.pdf', 620, 3, 0, 'published'),

-- Chapter 17: SQL nâng cao (lessons 49-51)
(17, 'JOIN nhiều bảng', 'INNER JOIN, LEFT JOIN, RIGHT JOIN.', 'videos/sql_04.mp4', 'docs/sql_04.pdf', 700, 1, 0, 'published'),
(17, 'GROUP BY & Aggregate Function', 'Tổng hợp dữ liệu với GROUP BY, SUM, COUNT.', 'videos/sql_05.mp4', 'docs/sql_05.pdf', 680, 2, 0, 'published'),
(17, 'Subquery & View', 'Truy vấn con và tạo view trong MySQL.', 'videos/sql_06.mp4', 'docs/sql_06.pdf', 720, 3, 0, 'published'),

-- Chapter 18: Thiết kế chuẩn hoá (lessons 52-54)
(18, 'Chuẩn hoá dữ liệu (1NF-3NF)', 'Các dạng chuẩn hoá cơ sở dữ liệu.', 'videos/sql_07.mp4', 'docs/sql_07.pdf', 750, 1, 0, 'published'),
(18, 'Thiết kế ERD', 'Vẽ sơ đồ thực thể - quan hệ cho hệ thống.', 'videos/sql_08.mp4', 'docs/sql_08.pdf', 700, 2, 0, 'published'),
(18, 'Dự án: Thiết kế CSDL website học trực tuyến', 'Áp dụng kiến thức thiết kế CSDL cho một hệ thống thực tế.', 'videos/sql_09.mp4', 'docs/sql_09.pdf', 900, 3, 0, 'published');

-- =========================================================
-- 5. ENROLLMENTS
-- =========================================================

INSERT INTO enrollments (user_id, course_id) VALUES
(6, 1), (6, 2),
(7, 2), (7, 4),
(8, 1), (8, 3),
(9, 4), (9, 5),
(10, 1),
(11, 2), (11, 6),
(12, 3),
(13, 5), (13, 6),
(14, 4),
(15, 1), (15, 2), (15, 6);

-- =========================================================
-- 6. LESSON PROGRESS
-- =========================================================

INSERT INTO lesson_progress (user_id, lesson_id, is_completed, watched_sec, completed_at) VALUES
(6, 1, 1, 600, '2026-06-01 10:00:00'),
(6, 2, 1, 720, '2026-06-02 10:00:00'),
(6, 3, 0, 200, NULL),
(6, 10, 1, 500, '2026-06-05 09:00:00'),
(8, 1, 1, 600, '2026-05-20 08:30:00'),
(8, 4, 1, 660, '2026-05-21 08:30:00'),
(8, 19, 1, 600, '2026-06-10 14:00:00'),
(10, 1, 1, 600, '2026-06-15 20:00:00'),
(10, 2, 0, 300, NULL),
(15, 1, 1, 600, '2026-06-01 07:00:00'),
(15, 2, 1, 720, '2026-06-01 08:00:00'),
(15, 3, 1, 540, '2026-06-02 07:00:00'),
(15, 10, 1, 500, '2026-06-03 07:00:00'),
(11, 10, 1, 500, '2026-06-04 07:00:00'),
(11, 46, 1, 550, '2026-06-12 07:00:00');

-- =========================================================
-- 7. QUIZZES  (id 1 -> 6)
-- =========================================================

INSERT INTO quizzes (course_id, title, description) VALUES
(1, 'Kiểm tra kiến thức Python cơ bản', 'Bài kiểm tra tổng hợp về biến, cấu trúc điều khiển và hàm trong Python.'),
(2, 'Kiểm tra JavaScript nền tảng', 'Bài kiểm tra về biến, hàm, DOM và ES6+.'),
(3, 'Kiểm tra Java OOP', 'Bài kiểm tra về lớp, đối tượng, kế thừa trong Java.'),
(4, 'Kiểm tra HTML & CSS', 'Bài kiểm tra kiến thức HTML, CSS và responsive design.'),
(5, 'Kiểm tra ReactJS', 'Bài kiểm tra về component, props, state và hooks.'),
(6, 'Kiểm tra SQL căn bản', 'Bài kiểm tra về truy vấn SELECT, JOIN và thiết kế CSDL.');

-- =========================================================
-- 8. QUESTIONS  (id 1 -> 30)
-- =========================================================

INSERT INTO questions (quiz_id, content, option_a, option_b, option_c, option_d, correct_answer, order_index) VALUES
-- Quiz 1: Python
(1, 'Từ khoá nào dùng để định nghĩa hàm trong Python?', 'func', 'def', 'function', 'lambda', 'B', 1),
(1, 'Kiểu dữ liệu nào dùng để lưu danh sách có thể thay đổi trong Python?', 'tuple', 'set', 'list', 'dict', 'C', 2),
(1, 'Toán tử nào dùng để so sánh bằng trong Python?', '=', '==', '===', '!=', 'B', 3),
(1, 'Vòng lặp nào dùng để lặp qua từng phần tử của một danh sách?', 'while', 'for', 'do-while', 'repeat', 'B', 4),
(1, 'Kết quả của "print(type(3.14))" là gì?', 'int', 'str', 'float', 'bool', 'C', 5),

-- Quiz 2: JavaScript
(2, 'Từ khoá nào dùng để khai báo biến không đổi trong ES6?', 'var', 'let', 'const', 'static', 'C', 1),
(2, 'Phương thức nào dùng để chọn phần tử theo id trong DOM?', 'querySelectorAll', 'getElementById', 'getElementByClass', 'find', 'B', 2),
(2, 'Kết quả của "typeof null" trong JavaScript là gì?', 'null', 'undefined', 'object', 'number', 'C', 3),
(2, 'Cú pháp nào là arrow function hợp lệ?', 'function() => {}', '() => {}', '=> function() {}', 'func => {}', 'B', 4),
(2, 'Promise có trạng thái nào sau khi hoàn thành thành công?', 'pending', 'fulfilled', 'rejected', 'idle', 'B', 5),

-- Quiz 3: Java
(3, 'Từ khoá nào dùng để kế thừa một lớp trong Java?', 'implements', 'extends', 'inherits', 'super', 'B', 1),
(3, 'Java hỗ trợ đa kế thừa với lớp thông qua?', 'class', 'interface', 'abstract class', 'không hỗ trợ', 'B', 2),
(3, 'Từ khoá nào dùng để bắt ngoại lệ trong Java?', 'catch', 'except', 'handle', 'rescue', 'A', 3),
(3, 'Cấu trúc dữ liệu nào lưu trữ theo dạng key-value trong Java?', 'ArrayList', 'HashMap', 'LinkedList', 'Stack', 'B', 4),
(3, 'Constructor trong Java có đặc điểm gì?', 'Có kiểu trả về', 'Trùng tên với lớp', 'Không thể overload', 'Là static', 'B', 5),

-- Quiz 4: HTML/CSS
(4, 'Thẻ nào dùng để tạo liên kết trong HTML?', '<link>', '<a>', '<href>', '<url>', 'B', 1),
(4, 'Thuộc tính CSS nào dùng để đổi màu chữ?', 'background-color', 'color', 'font-color', 'text-style', 'B', 2),
(4, 'Flexbox thuộc tính nào dùng để căn giữa theo trục chính?', 'align-items', 'justify-content', 'flex-direction', 'flex-wrap', 'B', 3),
(4, 'Media query dùng để làm gì?', 'Tối ưu SEO', 'Thiết kế responsive', 'Kết nối database', 'Xử lý sự kiện', 'B', 4),
(4, 'Thẻ HTML nào mang tính ngữ nghĩa (semantic)?', '<div>', '<span>', '<section>', '<b>', 'C', 5),

-- Quiz 5: ReactJS
(5, 'Hook nào dùng để quản lý state trong function component?', 'useEffect', 'useState', 'useRef', 'useMemo', 'B', 1),
(5, 'Props trong React có đặc điểm gì?', 'Có thể thay đổi trong component con', 'Chỉ đọc (read-only)', 'Chỉ dùng cho class component', 'Không truyền được dữ liệu', 'B', 2),
(5, 'Hook nào dùng để xử lý side-effect?', 'useState', 'useEffect', 'useContext', 'useCallback', 'B', 3),
(5, 'JSX là gì?', 'Một ngôn ngữ lập trình mới', 'Cú pháp mở rộng của JavaScript', 'Một framework CSS', 'Một cơ sở dữ liệu', 'B', 4),
(5, 'Thư viện nào thường dùng để định tuyến trong React?', 'Redux', 'Axios', 'React Router', 'Lodash', 'C', 5),

-- Quiz 6: SQL
(6, 'Câu lệnh nào dùng để truy vấn dữ liệu trong SQL?', 'GET', 'SELECT', 'FETCH', 'SHOW', 'B', 1),
(6, 'Loại JOIN nào trả về tất cả các dòng từ bảng bên trái?', 'INNER JOIN', 'RIGHT JOIN', 'LEFT JOIN', 'CROSS JOIN', 'C', 2),
(6, 'Khoá ngoại (foreign key) dùng để làm gì?', 'Tăng tốc truy vấn', 'Liên kết dữ liệu giữa 2 bảng', 'Mã hoá dữ liệu', 'Xoá dữ liệu tự động', 'B', 3),
(6, 'Hàm nào dùng để đếm số dòng trong SQL?', 'SUM()', 'COUNT()', 'TOTAL()', 'LEN()', 'B', 4),
(6, 'Dạng chuẩn nào yêu cầu loại bỏ sự phụ thuộc bắc cầu?', '1NF', '2NF', '3NF', 'BCNF', 'C', 5);

-- =========================================================
-- 9. RESULTS
-- =========================================================

INSERT INTO results (user_id, quiz_id, score, total, submit_time) VALUES
(6, 1, 4, 5, '2026-06-10 11:00:00'),
(8, 1, 5, 5, '2026-06-11 09:00:00'),
(10, 1, 3, 5, '2026-06-16 21:00:00'),
(15, 1, 5, 5, '2026-06-03 08:00:00'),
(6, 2, 3, 5, '2026-06-12 12:00:00'),
(7, 2, 4, 5, '2026-06-13 10:00:00'),
(11, 2, 5, 5, '2026-06-14 15:00:00'),
(15, 2, 4, 5, '2026-06-04 09:00:00'),
(8, 3, 4, 5, '2026-06-15 10:00:00'),
(12, 3, 3, 5, '2026-06-17 14:00:00'),
(9, 4, 5, 5, '2026-06-18 16:00:00'),
(14, 4, 4, 5, '2026-06-19 17:00:00'),
(9, 5, 3, 5, '2026-06-20 18:00:00'),
(13, 5, 5, 5, '2026-06-21 19:00:00'),
(11, 6, 4, 5, '2026-06-22 10:00:00'),
(13, 6, 5, 5, '2026-06-23 11:00:00'),
(15, 6, 3, 5, '2026-06-24 12:00:00');

-- =========================================================
-- 10. PAYMENTS
-- =========================================================

INSERT INTO payments (user_id, course_id, amount, method, status, transaction_ref, note, paid_at) VALUES
(6, 1, 599000, 'momo',          'completed', 'TXN20260601001', 'Thanh toán khoá Python cơ bản', '2026-05-30 09:15:00'),
(6, 2, 699000, 'card',          'completed', 'TXN20260601002', 'Thanh toán khoá JavaScript',    '2026-05-30 09:20:00'),
(7, 2, 699000, 'bank_transfer', 'completed', 'TXN20260602001', NULL,                             '2026-06-01 10:00:00'),
(8, 1, 599000, 'zalopay',       'completed', 'TXN20260602002', NULL,                             '2026-05-19 08:00:00'),
(8, 3, 799000, 'card',          'completed', 'TXN20260603001', NULL,                             '2026-06-09 14:00:00'),
(9, 5, 899000, 'momo',          'pending',   'TXN20260604001', 'Đang chờ xác nhận thanh toán',   NULL),
(10, 1, 599000, 'card',         'completed', 'TXN20260605001', NULL,                             '2026-06-14 19:00:00'),
(11, 2, 699000, 'bank_transfer','completed', 'TXN20260606001', NULL,                             '2026-06-03 20:00:00'),
(11, 6, 499000, 'momo',         'completed', 'TXN20260606002', NULL,                             '2026-06-11 07:30:00'),
(12, 3, 799000, 'card',         'failed',    'TXN20260607001', 'Thẻ hết hạn mức, thanh toán thất bại', NULL),
(13, 5, 899000, 'zalopay',      'completed', 'TXN20260608001', NULL,                             '2026-06-19 09:00:00'),
(13, 6, 499000, 'card',         'completed', 'TXN20260608002', NULL,                             '2026-06-19 09:05:00'),
(15, 1, 599000, 'momo',         'completed', 'TXN20260609001', NULL,                             '2026-06-01 06:30:00'),
(15, 2, 699000, 'momo',         'completed', 'TXN20260609002', NULL,                             '2026-06-01 06:35:00'),
(15, 6, 499000, 'bank_transfer','refunded',  'TXN20260609003', 'Học viên yêu cầu hoàn tiền',      '2026-06-05 06:40:00');

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Seed data hoàn tất: đã thêm dữ liệu mẫu chủ đề học lập trình cho toàn bộ hệ thống.' AS result;