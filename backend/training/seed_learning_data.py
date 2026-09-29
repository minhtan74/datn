"""(TÙY CHỌN – chỉ để DEMO) Làm dày dữ liệu học tập & kiểm tra cho trang Phân tích học tập.

Script làm 4 việc (chạy lại nhiều lần vẫn an toàn — phần nào đã có thì bỏ qua):
  1. Thêm câu hỏi cho các quiz 1–6 để mỗi chủ đề có 3–4 câu (trước đây chỉ 1 câu).
  2. Chuẩn hoá tên chủ đề của quiz 13/14 cho trùng với quiz 1/2 -> điểm được gộp theo chủ đề.
  3. Sinh thêm lượt làm quiz cho mọi học viên đã ghi danh (3–4 lượt/quiz, điểm tiến bộ dần,
     mỗi học viên có chủ đề mạnh/yếu riêng) kèm chi tiết từng câu (result_answers).
  4. Bổ sung tiến độ bài học (lesson_progress) theo tỉ lệ hoàn thành riêng của từng học viên.

    python training/seed_learning_data.py
"""
import hashlib
import os
import random
from datetime import datetime, timedelta

import pymysql

DB = dict(host=os.environ.get("DB_HOST", "127.0.0.1"), port=int(os.environ.get("DB_PORT", "3306")),
          user=os.environ.get("DB_USER", "root"), password=os.environ.get("DB_PASS", ""),
          database=os.environ.get("DB_NAME", "studyonline_db"), charset="utf8mb4")

# Số lượt làm mỗi quiz mà mỗi học viên cần có sau khi seed
TARGET_ATTEMPTS = (3, 4)
WINDOW_START = datetime(2026, 7, 1, 8, 0)
WINDOW_END = datetime(2026, 9, 27, 21, 0)

# Câu hỏi bổ sung: (topic, độ khó, nội dung, đáp án đúng, [3 đáp án sai], giải thích)
PY_TOPICS = {"fn": "Hàm (Functions)", "dt": "Kiểu dữ liệu (Data Types)", "op": "Toán tử (Operators)",
             "lp": "Vòng lặp (Loops)", "if": "Câu lệnh điều kiện (If-Else)", "oop": "Lập trình hướng đối tượng (OOP)"}
JS_TOPICS = {"es6": "Biến & ES6", "dom": "DOM", "dt": "Kiểu dữ liệu (Data Types)", "fn": "Hàm (Functions)",
             "as": "Bất đồng bộ (Async)", "ev": "Sự kiện (Events)"}

EXTRA_QUESTIONS = {
    1: [
        (PY_TOPICS["fn"], "easy", "Từ khoá nào dùng để trả về giá trị từ một hàm Python?", "return",
         ["exit", "continue", "pass"], "return kết thúc hàm và trả giá trị cho nơi gọi."),
        (PY_TOPICS["fn"], "medium", "Với def f(a, b=2): return a * b, lời gọi f(3) trả về gì?", "6",
         ["3", "5", "Báo lỗi thiếu tham số"], "b có giá trị mặc định 2 nên f(3) = 3 * 2 = 6."),
        (PY_TOPICS["fn"], "medium", "Biểu thức lambda nào tính bình phương của x?", "lambda x: x ** 2",
         ["lambda: x ** 2", "def x: x ** 2", "lambda x -> x * x"], "Cú pháp: lambda <tham số>: <biểu thức>."),
        (PY_TOPICS["dt"], "medium", "Kiểu dữ liệu nào là bất biến (immutable)?", "tuple",
         ["list", "dict", "set"], "tuple không thể thay đổi sau khi tạo."),
        (PY_TOPICS["dt"], "easy", "len({'a': 1, 'b': 2}) trả về bao nhiêu?", "2",
         ["1", "4", "Báo lỗi"], "len của dict là số cặp key-value."),
        (PY_TOPICS["op"], "easy", "Biểu thức 7 // 2 trong Python cho kết quả gì?", "3",
         ["3.5", "4", "1"], "// là phép chia lấy phần nguyên."),
        (PY_TOPICS["op"], "easy", "Biểu thức 2 ** 3 cho kết quả gì?", "8",
         ["6", "9", "5"], "** là phép luỹ thừa: 2^3 = 8."),
        (PY_TOPICS["op"], "easy", "Biểu thức 7 % 3 cho kết quả gì?", "1",
         ["2", "0", "2.33"], "% là phép chia lấy dư."),
        (PY_TOPICS["lp"], "easy", "range(1, 5) sinh ra dãy số nào?", "1, 2, 3, 4",
         ["1, 2, 3, 4, 5", "0, 1, 2, 3, 4", "2, 3, 4, 5"], "range không bao gồm giá trị kết thúc."),
        (PY_TOPICS["lp"], "easy", "Lệnh nào thoát khỏi vòng lặp ngay lập tức?", "break",
         ["continue", "pass", "else"], "break dừng vòng lặp gần nhất."),
        (PY_TOPICS["lp"], "medium", "Vòng lặp while True: cần lệnh gì bên trong để có thể dừng?", "break",
         ["pass", "continue", "else"], "Điều kiện luôn đúng nên phải dùng break để thoát."),
        (PY_TOPICS["if"], "easy", "Từ khoá nào dùng cho nhánh 'ngược lại nếu' trong Python?", "elif",
         ["elseif", "else if", "ifelse"], "Python dùng elif."),
        (PY_TOPICS["if"], "medium", "Với x = 5, biểu thức 'A' if x > 3 else 'B' có giá trị gì?", "'A'",
         ["'B'", "True", "Báo lỗi cú pháp"], "Điều kiện x > 3 đúng nên trả 'A'."),
        (PY_TOPICS["if"], "medium", "Khối lệnh trong câu if của Python được xác định bằng gì?", "Thụt lề (indentation)",
         ["Dấu ngoặc nhọn {}", "Từ khoá end", "Dấu chấm phẩy"], "Python dùng thụt lề để xác định khối lệnh."),
        (PY_TOPICS["oop"], "easy", "Từ khoá nào dùng để định nghĩa lớp trong Python?", "class",
         ["def", "object", "struct"], "class <Tên>: định nghĩa một lớp."),
        (PY_TOPICS["oop"], "medium", "Phương thức khởi tạo của lớp Python có tên là gì?", "__init__",
         ["__new__", "constructor", "init"], "__init__ được gọi khi tạo đối tượng."),
        (PY_TOPICS["oop"], "medium", "Tham số đầu tiên của phương thức thể hiện (instance method) thường là?", "self",
         ["this", "cls", "me"], "self tham chiếu tới đối tượng hiện tại."),
    ],
    2: [
        (JS_TOPICS["es6"], "medium", "let khác var ở điểm nào?", "let có phạm vi khối (block scope)",
         ["let là hằng số", "var có phạm vi khối", "Không có khác biệt"], "let/const có block scope, var có function scope."),
        (JS_TOPICS["es6"], "medium", "Cú pháp destructuring nào lấy thuộc tính a từ object o?", "const { a } = o",
         ["const [a] = o", "const a = { o }", "const o = { a }"], "Destructuring object dùng dấu {}."),
        (JS_TOPICS["es6"], "easy", "Template literal trong ES6 dùng ký tự nào?", "Dấu backtick (`)",
         ["Dấu nháy đơn (')", "Dấu nháy kép (\")", "Dấu gạch chéo (/)"], "`Xin chào ${ten}`."),
        (JS_TOPICS["dom"], "easy", "Thuộc tính nào thay đổi nội dung văn bản của phần tử?", "textContent",
         ["value", "style", "id"], "textContent đặt/lấy văn bản bên trong phần tử."),
        (JS_TOPICS["dom"], "medium", "document.querySelector('.box') trả về gì?", "Phần tử đầu tiên có class box",
         ["Tất cả phần tử có class box", "Phần tử có id box", "Thẻ <box>"], "querySelector trả về phần tử khớp đầu tiên."),
        (JS_TOPICS["dt"], "medium", "Kết quả của '5' + 3 trong JavaScript là gì?", "'53'",
         ["8", "NaN", "Báo lỗi"], "Cộng chuỗi với số sẽ nối chuỗi."),
        (JS_TOPICS["dt"], "easy", "Array.isArray([]) trả về gì?", "true",
         ["false", "'array'", "undefined"], "[] là một mảng."),
        (JS_TOPICS["fn"], "medium", "Phương thức mảng nào gọi callback cho mỗi phần tử và trả về mảng mới?", "map",
         ["forEach", "find", "some"], "map biến đổi từng phần tử thành mảng mới."),
        (JS_TOPICS["fn"], "easy", "Hàm không có lệnh return sẽ trả về gì?", "undefined",
         ["null", "0", "false"], "Mặc định hàm trả về undefined."),
        (JS_TOPICS["as"], "easy", "Từ khoá nào dùng để chờ một Promise trong hàm async?", "await",
         ["wait", "then", "yield"], "await tạm dừng tới khi Promise hoàn thành."),
        (JS_TOPICS["as"], "medium", "Phương thức nào dùng để xử lý lỗi của Promise?", ".catch()",
         [".then()", ".finally()", ".error()"], ".catch nhận lỗi khi Promise bị reject."),
        (JS_TOPICS["as"], "hard", "console.log(1); setTimeout(() => console.log(2)); console.log(3); in ra thứ tự nào?",
         "1 3 2", ["1 2 3", "2 1 3", "3 2 1"], "Callback của setTimeout chạy sau khi call stack rỗng."),
        (JS_TOPICS["ev"], "easy", "Phương thức nào gắn trình xử lý sự kiện cho phần tử?", "addEventListener",
         ["attachEvent", "onEvent", "listen"], "element.addEventListener('click', handler)."),
        (JS_TOPICS["ev"], "medium", "event.preventDefault() dùng để làm gì?", "Chặn hành vi mặc định của trình duyệt",
         ["Dừng lan truyền sự kiện", "Xoá sự kiện", "Gắn lại sự kiện"], "Ví dụ: chặn form tự submit."),
        (JS_TOPICS["ev"], "medium", "Sự kiện nào xảy ra khi người dùng gửi form?", "submit",
         ["click", "change", "send"], "Form phát sự kiện submit."),
    ],
    3: [
        ("Kế thừa (Inheritance)", "easy", "Từ khoá nào dùng để gọi constructor của lớp cha?", "super",
         ["this", "parent", "base"], "super(...) gọi constructor lớp cha."),
        ("Kế thừa (Inheritance)", "medium", "Ghi đè phương thức (override) yêu cầu điều gì?", "Cùng tên và cùng danh sách tham số",
         ["Khác danh sách tham số", "Phương thức phải static", "Phương thức phải private"], "Override giữ nguyên chữ ký phương thức."),
        ("Xử lý ngoại lệ (Exceptions)", "easy", "Khối nào luôn được thực thi dù có ngoại lệ hay không?", "finally",
         ["catch", "throw", "try"], "finally luôn chạy sau try/catch."),
        ("Xử lý ngoại lệ (Exceptions)", "medium", "Từ khoá nào khai báo phương thức có thể ném ngoại lệ?", "throws",
         ["throw", "try", "catch"], "throws đặt ở chữ ký phương thức."),
        ("Xử lý ngoại lệ (Exceptions)", "medium", "ArithmeticException xảy ra khi nào?", "Chia số nguyên cho 0",
         ["Truy cập đối tượng null", "Vượt chỉ số mảng", "Ép kiểu sai"], "Ví dụ: int x = 5 / 0;"),
        ("Collection Framework", "easy", "Collection nào không cho phép phần tử trùng lặp?", "HashSet",
         ["ArrayList", "LinkedList", "Vector"], "Set không chứa phần tử trùng."),
        ("Collection Framework", "easy", "Phương thức nào thêm phần tử vào ArrayList?", "add()",
         ["put()", "push()", "insert()"], "list.add(x)."),
        ("Collection Framework", "easy", "Lấy giá trị theo key trong HashMap dùng phương thức nào?", "get(key)",
         ["find(key)", "value(key)", "at(key)"], "map.get(key)."),
        ("OOP cơ bản", "medium", "Tính đóng gói (encapsulation) thường dùng access modifier nào cho thuộc tính?", "private",
         ["public", "static", "final"], "Thuộc tính private, truy cập qua getter/setter."),
        ("OOP cơ bản", "easy", "Từ khoá nào dùng để tạo một đối tượng mới?", "new",
         ["create", "make", "init"], "new ClassName()."),
        ("OOP cơ bản", "medium", "Lớp abstract có đặc điểm gì?", "Không thể tạo đối tượng trực tiếp",
         ["Không được có phương thức", "Phải là final", "Chỉ chứa hằng số"], "Lớp abstract chỉ dùng để kế thừa."),
    ],
    4: [
        ("HTML cơ bản", "easy", "Thẻ nào dùng để chèn hình ảnh?", "<img>",
         ["<image>", "<pic>", "<src>"], "<img src=\"...\" alt=\"...\">."),
        ("HTML cơ bản", "easy", "Thuộc tính nào của <img> hiển thị văn bản thay thế?", "alt",
         ["title", "src", "name"], "alt hiển thị khi ảnh lỗi và hỗ trợ trình đọc màn hình."),
        ("CSS cơ bản", "easy", "Selector nào chọn phần tử có id là main?", "#main",
         [".main", "main", "*main"], "# chọn theo id, . chọn theo class."),
        ("CSS cơ bản", "easy", "Thuộc tính nào đổi kích thước chữ?", "font-size",
         ["text-size", "font-style", "size"], "font-size: 16px;"),
        ("Flexbox & Layout", "medium", "Với display: flex, thuộc tính nào căn giữa theo trục phụ?", "align-items",
         ["justify-content", "flex-wrap", "order"], "align-items căn theo trục phụ (cross axis)."),
        ("Flexbox & Layout", "easy", "flex-direction: column có tác dụng gì?", "Xếp các phần tử theo cột",
         ["Xếp các phần tử theo hàng", "Đảo ngược thứ tự", "Ẩn phần tử"], "Trục chính chuyển thành chiều dọc."),
        ("Responsive Design", "medium", "Thẻ meta nào cần có để trang hiển thị đúng trên điện thoại?", "viewport",
         ["charset", "description", "robots"], "<meta name=\"viewport\" content=\"width=device-width\">."),
        ("Responsive Design", "medium", "@media (max-width: 768px) áp dụng khi nào?", "Màn hình rộng tối đa 768px",
         ["Màn hình rộng tối thiểu 768px", "Chỉ khi rộng đúng 768px", "Luôn luôn áp dụng"], "max-width: ≤ 768px."),
        ("HTML ngữ nghĩa (Semantic)", "easy", "Thẻ nào dùng cho khu vực điều hướng?", "<nav>",
         ["<div>", "<span>", "<menu-bar>"], "<nav> chứa các liên kết điều hướng."),
        ("HTML ngữ nghĩa (Semantic)", "medium", "Thẻ nào chứa nội dung chính, duy nhất của trang?", "<main>",
         ["<section>", "<article>", "<body>"], "Mỗi trang chỉ có một <main>."),
    ],
    5: [
        ("Hooks", "medium", "Mảng dependency rỗng [] trong useEffect có nghĩa là gì?", "Chỉ chạy một lần sau lần render đầu",
         ["Chạy sau mọi lần render", "Không bao giờ chạy", "Chỉ chạy khi unmount"], "Không phụ thuộc gì nên chỉ chạy lúc mount."),
        ("Hooks", "easy", "Hook nào dùng để đọc giá trị từ Context?", "useContext",
         ["useRef", "useMemo", "useState"], "useContext(MyContext)."),
        ("Props & State", "easy", "Cách cập nhật state đúng với const [count, setCount] = useState(0)?", "setCount(count + 1)",
         ["count = count + 1", "this.count++", "state.count = 1"], "Luôn cập nhật qua hàm setter."),
        ("Props & State", "easy", "Dữ liệu truyền từ component cha xuống con thông qua?", "props",
         ["state", "ref", "key"], "props là đầu vào của component."),
        ("Props & State", "medium", "Khi state thay đổi, React sẽ làm gì?", "Render lại component",
         ["Tải lại toàn bộ trang", "Không làm gì", "Xoá component"], "State đổi -> re-render."),
        ("JSX", "easy", "Trong JSX, thuộc tính class của HTML được viết là?", "className",
         ["class", "cssClass", "styleClass"], "class là từ khoá của JS nên JSX dùng className."),
        ("JSX", "easy", "Nhúng biểu thức JavaScript trong JSX dùng ký hiệu nào?", "{ }",
         ["( )", "[ ]", "< >"], "Ví dụ: <p>{name}</p>."),
        ("Routing", "easy", "Component nào tạo liên kết không tải lại trang trong React Router?", "<Link>",
         ["<a>", "<Route>", "<Href>"], "<Link to=\"/path\">."),
        ("Routing", "medium", "Hook nào lấy tham số động trên URL trong React Router?", "useParams",
         ["useQuery", "useUrl", "useRoute"], "const { id } = useParams()."),
    ],
    6: [
        ("Truy vấn SQL (SQL Queries)", "easy", "Mệnh đề nào dùng để lọc các dòng?", "WHERE",
         ["ORDER BY", "GROUP BY", "FROM"], "WHERE lọc dòng trước khi nhóm."),
        ("Truy vấn SQL (SQL Queries)", "easy", "Sắp xếp giảm dần dùng cú pháp nào?", "ORDER BY cot DESC",
         ["SORT cot DESC", "ORDER DESC BY cot", "DESC ORDER cot"], "ORDER BY ... DESC."),
        ("JOIN", "easy", "INNER JOIN trả về những dòng nào?", "Chỉ các dòng khớp ở cả hai bảng",
         ["Tất cả dòng của bảng trái", "Tất cả dòng của bảng phải", "Tích Descartes"], "Chỉ giữ cặp dòng thoả điều kiện ON."),
        ("JOIN", "medium", "Loại JOIN nào tạo ra tích Descartes?", "CROSS JOIN",
         ["LEFT JOIN", "SELF JOIN", "INNER JOIN"], "CROSS JOIN ghép mọi dòng với mọi dòng."),
        ("Thiết kế CSDL (DB Design)", "easy", "Khoá chính (primary key) có đặc điểm gì?", "Duy nhất và không NULL",
         ["Cho phép trùng lặp", "Có thể NULL", "Chỉ là kiểu chuỗi"], "Khoá chính định danh duy nhất mỗi dòng."),
        ("Thiết kế CSDL (DB Design)", "medium", "Quan hệ nhiều-nhiều thường được cài đặt bằng cách nào?", "Dùng bảng trung gian",
         ["Một khoá ngoại", "Gộp hai bảng", "Dùng trigger"], "Ví dụ: enrollments nối users và courses."),
        ("Hàm tổng hợp (Aggregate)", "medium", "Mệnh đề nào lọc nhóm sau GROUP BY?", "HAVING",
         ["WHERE", "FILTER", "LIMIT"], "HAVING lọc trên kết quả tổng hợp."),
        ("Hàm tổng hợp (Aggregate)", "easy", "Hàm nào tính giá trị trung bình?", "AVG()",
         ["MEAN()", "SUM()", "MEDIAN()"], "AVG(cot)."),
        ("Chuẩn hoá (Normalization)", "medium", "Dạng chuẩn 1NF yêu cầu điều gì?", "Mọi giá trị là nguyên tố (atomic)",
         ["Không có phụ thuộc bắc cầu", "Không có phụ thuộc bộ phận", "Phải có khoá ngoại"], "Mỗi ô chỉ chứa một giá trị."),
        ("Chuẩn hoá (Normalization)", "hard", "Dạng chuẩn 2NF loại bỏ loại phụ thuộc nào?", "Phụ thuộc bộ phận vào khoá",
         ["Phụ thuộc bắc cầu", "Giá trị lặp trong một ô", "Phụ thuộc vào khoá chính"], "Thuộc tính không khoá phải phụ thuộc toàn bộ khoá."),
    ],
}

# Đổi tên chủ đề của quiz 13/14 cho trùng với quiz 1/2 để gộp điểm theo chủ đề
TOPIC_RENAMES = {
    13: {"Biến và kiểu dữ liệu": PY_TOPICS["dt"], "Toán tử": PY_TOPICS["op"], "Vòng lặp": PY_TOPICS["lp"],
         "Cấu trúc điều khiển": PY_TOPICS["if"], "Lập trình hướng đối tượng": PY_TOPICS["oop"]},
    14: {"Kiểu dữ liệu": JS_TOPICS["dt"], "Hàm và arrow function": JS_TOPICS["fn"],
         "Bất đồng bộ": JS_TOPICS["as"], "Sự kiện": JS_TOPICS["ev"]},
}


# Số ngẫu nhiên tất định theo khoá -> chạy lại cho cùng kết quả
def rng_for(*key) -> random.Random:
    return random.Random(int(hashlib.md5(":".join(map(str, key)).encode()).hexdigest(), 16))


# Bước 1: thêm câu hỏi (bỏ qua câu đã tồn tại), xáo vị trí đáp án đúng giữa A–D
def add_questions(cur) -> int:
    added = 0
    for quiz_id, items in EXTRA_QUESTIONS.items():
        cur.execute("SELECT content FROM questions WHERE quiz_id=%s", (quiz_id,))
        existing = {r["content"] for r in cur.fetchall()}
        cur.execute("SELECT COALESCE(MAX(order_index), 0) AS m FROM questions WHERE quiz_id=%s", (quiz_id,))
        order = int(cur.fetchone()["m"])
        for topic, diff, content, right, wrongs, expl in items:
            if content in existing:
                continue
            opts = [right, *wrongs]
            rng_for("opts", content).shuffle(opts)
            letter = "ABCD"[opts.index(right)]
            order += 1
            cur.execute(
                "INSERT INTO questions (quiz_id, content, option_a, option_b, option_c, option_d, "
                "correct_answer, topic, difficulty, explanation, order_index) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (quiz_id, content, *opts, letter, topic, diff, expl, order),
            )
            added += 1
    return added


# Bước 2: chuẩn hoá tên chủ đề
def rename_topics(cur) -> int:
    changed = 0
    for quiz_id, mapping in TOPIC_RENAMES.items():
        for old, new in mapping.items():
            changed += cur.execute("UPDATE questions SET topic=%s WHERE quiz_id=%s AND topic=%s", (new, quiz_id, old))
    return changed


# Xác suất học viên trả lời đúng 1 câu: năng lực chung + độ mạnh/yếu theo chủ đề
# + tiến bộ theo số lượt làm − độ khó của câu
def p_correct(user_id: int, topic: str, difficulty: str, attempt_no: int) -> float:
    base = 0.45 + rng_for("base", user_id).random() * 0.35
    topic_bias = rng_for("topic", user_id, topic).uniform(-0.30, 0.20)
    diff_pen = {"easy": -0.05, "medium": 0.05, "hard": 0.15}.get(difficulty or "medium", 0.05)
    return max(0.08, min(0.97, base + topic_bias - diff_pen + 0.07 * attempt_no))


# Bước 3: sinh thêm lượt làm quiz cho từng (học viên, quiz của khoá đã ghi danh)
def add_attempts(cur) -> tuple[int, int]:
    n_results = n_answers = 0
    cur.execute(
        "SELECT e.user_id, q.id AS quiz_id FROM enrollments e "
        "JOIN users u ON u.id = e.user_id AND u.role = 'student' "
        "JOIN quizzes q ON q.course_id = e.course_id ORDER BY e.user_id, q.id"
    )
    pairs = cur.fetchall()
    for p in pairs:
        uid, qid = p["user_id"], p["quiz_id"]
        cur.execute("SELECT id, correct_answer, topic, difficulty FROM questions WHERE quiz_id=%s", (qid,))
        qs = cur.fetchall()
        if not qs:
            continue
        cur.execute("SELECT MIN(submit_time) AS first, COUNT(*) AS n FROM results WHERE user_id=%s AND quiz_id=%s",
                    (uid, qid))
        row = cur.fetchone()
        rng = rng_for("attempts", uid, qid)
        target = rng.randint(*TARGET_ATTEMPTS)
        need = target - int(row["n"])
        if need <= 0:
            continue
        # Lượt làm gần đây (tháng 9) được giữ là lượt mới nhất -> lượt seed nằm trước nó
        end = WINDOW_END
        if row["first"] and row["first"] > WINDOW_START + timedelta(days=30):
            end = row["first"] - timedelta(days=1)
        span = (end - WINDOW_START).total_seconds()
        times = sorted(WINDOW_START + timedelta(seconds=rng.random() * span) for _ in range(need))
        for i, t in enumerate(times):
            answers, score = [], 0
            for q in qs:
                ok = rng.random() < p_correct(uid, q["topic"], q["difficulty"], i)
                chosen = q["correct_answer"] if ok else rng.choice([c for c in "ABCD" if c != q["correct_answer"]])
                score += ok
                answers.append((q["id"], chosen, int(ok)))
            cur.execute("INSERT INTO results (user_id, quiz_id, score, total, submit_time) VALUES (%s,%s,%s,%s,%s)",
                        (uid, qid, score, len(qs), t.replace(microsecond=0)))
            rid = cur.lastrowid
            cur.executemany("INSERT INTO result_answers (result_id, question_id, chosen, is_correct) "
                            "VALUES (%s,%s,%s,%s)", [(rid, *a) for a in answers])
            n_results += 1
            n_answers += len(answers)
    return n_results, n_answers


# Bước 4: tiến độ bài học — mỗi học viên hoàn thành một tỉ lệ bài riêng, bài kế tiếp đang xem dở
def add_progress(cur) -> int:
    added = 0
    cur.execute("SELECT e.user_id, e.course_id FROM enrollments e "
                "JOIN users u ON u.id = e.user_id AND u.role = 'student'")
    for e in cur.fetchall():
        uid, cid = e["user_id"], e["course_id"]
        cur.execute("SELECT l.id, l.duration FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id "
                    "WHERE ch.course_id=%s ORDER BY ch.order_index, ch.id, l.order_index, l.id", (cid,))
        lessons = cur.fetchall()
        if not lessons:
            continue
        rng = rng_for("progress", uid, cid)
        n_done = round(len(lessons) * rng.uniform(0.35, 1.0))
        day = WINDOW_START + timedelta(days=rng.randint(0, 20))
        for idx, l in enumerate(lessons[: n_done + 1]):
            dur = int(l["duration"] or 0) or 900
            done = idx < n_done
            watched = int(dur * rng.uniform(0.9, 1.2)) if done else int(dur * rng.uniform(0.2, 0.7))
            day += timedelta(days=rng.randint(1, 4), hours=rng.randint(0, 8))
            added += cur.execute(
                "INSERT IGNORE INTO lesson_progress (user_id, lesson_id, is_completed, watched_sec, completed_at) "
                "VALUES (%s,%s,%s,%s,%s)",
                (uid, l["id"], int(done), watched, day if done else None),
            )
    return added


def main():
    conn = pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cur:
            q = add_questions(cur)
            t = rename_topics(cur)
            r, a = add_attempts(cur)
            p = add_progress(cur)
        conn.commit()
    finally:
        conn.close()
    print(f"Thêm {q} câu hỏi, chuẩn hoá {t} chủ đề, {r} lượt làm quiz ({a} câu trả lời), {p} dòng tiến độ bài học.")


if __name__ == "__main__":
    main()
