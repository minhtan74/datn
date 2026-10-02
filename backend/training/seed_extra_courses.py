"""(DEMO) Tạo các khóa học bổ sung: mỗi khóa 3 chương x 3 bài + 1 bài kiểm tra chính thức.

    python training/seed_extra_courses.py

Chạy lại nhiều lần vẫn an toàn: khóa đã có (theo slug) thì không tạo trùng.
Sau khi chạy: dựng PDF tài liệu bài học rồi gắn vào bài (nội dung ở lesson_docs/content/course<N>_*.md,
mỗi bài bắt đầu bằng "=== LESSON <id> ===" với id in ra bên dưới):
    python training/lesson_docs/build_pdfs.py <id các bài>
    python training/lesson_docs/seed_lesson_docs.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, execute, q_all, q_one  # noqa: E402

LESSONS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lesson_docs", "lessons.json")

# Mỗi khóa: thông tin khóa, chapters = [(tên chương, [(tên bài, mô tả, thời lượng giây), ...])],
# questions = [(câu hỏi, A, B, C, D, đáp án, chủ đề = tên bài, độ khó, giải thích)]
COURSES = [
    {
        "title": "Tiếng Anh Giao Tiếp Cơ Bản",
        "slug": "tieng-anh-giao-tiep-co-ban",
        "description": "Phát âm, ngữ pháp nền tảng và mẫu câu giao tiếp hằng ngày cho người mới bắt đầu học tiếng Anh.",
        "price": 399000,
        "level": "beginner",
        "teacher_email": "duyen.pham@studyonline.vn",
        "media_prefix": "eng",
        "chapters": [
            ("Phát Âm & Chào Hỏi", [
                ("Bảng chữ cái và phát âm cơ bản", "26 chữ cái, nguyên âm, phụ âm và cách đánh vần tên.", 540),
                ("Chào hỏi và giới thiệu bản thân", "Mẫu câu chào hỏi, hỏi tên, quê quán, nghề nghiệp.", 600),
                ("Số đếm, ngày tháng và thời gian", "Số đếm, số thứ tự, thứ trong tuần, tháng và cách nói giờ.", 580),
            ]),
            ("Ngữ Pháp Nền Tảng", [
                ("Động từ to be và đại từ nhân xưng", "Cách chia am/is/are, câu khẳng định, phủ định, nghi vấn.", 620),
                ("Thì hiện tại đơn", "Diễn tả thói quen, sự thật; chia động từ ngôi thứ ba số ít.", 650),
                ("Thì hiện tại tiếp diễn", "Diễn tả hành động đang xảy ra; so sánh với hiện tại đơn.", 630),
            ]),
            ("Giao Tiếp Theo Tình Huống", [
                ("Hỏi đường và phương tiện đi lại", "Hỏi và chỉ đường, giới từ chỉ vị trí, phương tiện giao thông.", 560),
                ("Mua sắm và gọi món", "Hỏi giá, chọn kích cỡ, gọi món và thanh toán ở nhà hàng.", 600),
                ("Sở thích và kế hoạch", "Nói về sở thích với like + V-ing; kế hoạch với be going to và will.", 610),
            ]),
        ],
        "quiz_title": "Kiểm tra Tiếng Anh giao tiếp cơ bản",
        "questions": [
            ("Chữ cái nào sau đây là NGUYÊN ÂM trong tiếng Anh?", "B", "E", "G", "K", "B",
             "Bảng chữ cái và phát âm cơ bản", "easy", "5 nguyên âm là A, E, I, O, U."),
            ("Câu nào dùng để hỏi tên một người lần đầu gặp mặt?", "How old are you?", "What's your name?",
             "Where are you?", "How are you doing?", "B", "Chào hỏi và giới thiệu bản thân", "easy",
             "What's your name? = Bạn tên là gì?"),
            ("\"It's a quarter past seven\" nghĩa là mấy giờ?", "6:45", "7:15", "7:30", "7:45", "B",
             "Số đếm, ngày tháng và thời gian", "medium", "a quarter past = hơn 15 phút -> 7:15."),
            ("Chọn từ đúng: \"She ___ a student.\"", "am", "are", "is", "be", "C",
             "Động từ to be và đại từ nhân xưng", "easy", "Chủ ngữ ngôi thứ ba số ít (she) đi với is."),
            ("Câu phủ định đúng của \"They are teachers.\" là:", "They not are teachers.", "They aren't teachers.",
             "They don't teachers.", "They isn't teachers.", "B", "Động từ to be và đại từ nhân xưng", "medium",
             "Phủ định của to be: thêm not sau are -> aren't."),
            ("Chọn dạng đúng: \"My brother ___ football every Sunday.\"", "play", "plays", "is play", "playing", "B",
             "Thì hiện tại đơn", "easy", "Thói quen -> hiện tại đơn; chủ ngữ số ít thêm -s: plays."),
            ("Câu hỏi đúng của thì hiện tại đơn là:", "Does he likes coffee?", "Do he like coffee?",
             "Does he like coffee?", "Is he like coffee?", "C", "Thì hiện tại đơn", "medium",
             "Does + chủ ngữ số ít + động từ nguyên mẫu (không thêm -s)."),
            ("\"Look! The children ___ in the garden.\" Chọn đáp án đúng.", "play", "plays", "are playing",
             "is playing", "C", "Thì hiện tại tiếp diễn", "medium",
             "Look! báo hiệu hành động đang xảy ra -> hiện tại tiếp diễn; children số nhiều -> are playing."),
            ("Bạn muốn hỏi giá một chiếc áo. Câu nào phù hợp nhất?", "How many is this shirt?",
             "How much is this shirt?", "What price you want?", "How long is this shirt?", "B",
             "Mua sắm và gọi món", "medium", "Hỏi giá dùng How much is/are ...?"),
            ("Chọn câu đúng nói về kế hoạch ĐÃ quyết định từ trước:",
             "I will visit my grandparents tomorrow, I just decided.",
             "I am going to visit my grandparents this weekend.", "I going to visit my grandparents.",
             "I will to visit my grandparents.", "B", "Sở thích và kế hoạch", "hard",
             "Kế hoạch đã định trước dùng be going to + V; will dùng cho quyết định tức thời."),
        ],
    },
    {
        "title": "Toán Rời Rạc Cho Lập Trình Viên",
        "slug": "toan-roi-rac-cho-lap-trinh-vien",
        "description": "Logic, tập hợp, tổ hợp, đệ quy và lý thuyết đồ thị — nền tảng toán học cho thuật toán và lập trình.",
        "price": 449000,
        "level": "intermediate",
        "teacher_email": "cuong.le@studyonline.vn",
        "media_prefix": "math",
        "chapters": [
            ("Logic & Tập Hợp", [
                ("Mệnh đề và các phép toán logic", "Mệnh đề, phủ định, hội, tuyển, kéo theo, tương đương; bảng chân trị.", 620),
                ("Vị từ, lượng từ và phương pháp chứng minh", "Lượng từ với mọi / tồn tại, phủ định lượng từ, chứng minh trực tiếp và phản chứng.", 660),
                ("Tập hợp và các phép toán tập hợp", "Hợp, giao, hiệu, phần bù, tập con, tập lũy thừa, tích Descartes.", 600),
            ]),
            ("Tổ Hợp & Đệ Quy", [
                ("Quy tắc cộng và quy tắc nhân", "Hai quy tắc đếm cơ bản và nguyên lý bù trừ cho hai tập hợp.", 580),
                ("Hoán vị, chỉnh hợp và tổ hợp", "Đếm các cách sắp xếp và chọn phần tử có / không quan tâm thứ tự.", 640),
                ("Quy nạp toán học và hệ thức truy hồi", "Chứng minh bằng quy nạp; dãy truy hồi và liên hệ với hàm đệ quy.", 670),
            ]),
            ("Đồ Thị & Cây", [
                ("Đồ thị và cách biểu diễn", "Đỉnh, cạnh, bậc, định lý bắt tay; ma trận kề và danh sách kề.", 610),
                ("Duyệt đồ thị và đường đi ngắn nhất", "BFS, DFS và thuật toán Dijkstra trên đồ thị có trọng số.", 700),
                ("Cây và cây khung nhỏ nhất", "Tính chất của cây, cây khung, thuật toán Kruskal và Prim.", 650),
            ]),
        ],
        "quiz_title": "Kiểm tra Toán rời rạc cơ bản",
        "questions": [
            ("Mệnh đề kéo theo p → q SAI trong trường hợp nào?", "p đúng, q đúng", "p đúng, q sai",
             "p sai, q đúng", "p sai, q sai", "B", "Mệnh đề và các phép toán logic", "easy",
             "p → q chỉ sai khi giả thiết p đúng mà kết luận q sai."),
            ("Phủ định của mệnh đề \"∀x, P(x)\" là:", "∀x, ¬P(x)", "∃x, P(x)", "∃x, ¬P(x)", "¬∃x, P(x)", "C",
             "Vị từ, lượng từ và phương pháp chứng minh", "medium",
             "Phủ định đổi ∀ thành ∃ và phủ định vị từ: ¬∀x P(x) ≡ ∃x ¬P(x)."),
            ("Tập hợp A có 4 phần tử. Tập lũy thừa P(A) có bao nhiêu phần tử?", "4", "8", "16", "24", "C",
             "Tập hợp và các phép toán tập hợp", "medium", "Tập n phần tử có 2^n tập con: 2^4 = 16."),
            ("Biển số gồm 2 chữ cái (26 chữ) rồi 3 chữ số (0–9), cho phép lặp. Có bao nhiêu biển số?",
             "676 000", "6 760", "17 576 000", "1 000", "A", "Quy tắc cộng và quy tắc nhân", "medium",
             "Quy tắc nhân: 26 · 26 · 10 · 10 · 10 = 676 000."),
            ("Giá trị của C(5, 2) là:", "10", "20", "25", "60", "A", "Hoán vị, chỉnh hợp và tổ hợp", "easy",
             "C(5, 2) = 5! / (2! · 3!) = 10."),
            ("Có bao nhiêu cách chọn 3 trong 5 bạn rồi xếp vào 3 ghế khác nhau (có thứ tự)?", "10", "60", "125", "15",
             "B", "Hoán vị, chỉnh hợp và tổ hợp", "medium",
             "Chọn có thứ tự, không lặp -> chỉnh hợp A(5, 3) = 5 · 4 · 3 = 60."),
            ("Dãy a(n) = 2·a(n−1) + 1 với a(0) = 1. Giá trị a(4) là:", "15", "16", "31", "17", "C",
             "Quy nạp toán học và hệ thức truy hồi", "hard",
             "a(1)=3, a(2)=7, a(3)=15, a(4)=31 (tổng quát a(n) = 2^(n+1) − 1)."),
            ("Đồ thị vô hướng có 5 đỉnh với bậc lần lượt 3, 3, 2, 2, 2. Đồ thị có bao nhiêu cạnh?", "5", "6", "12",
             "10", "B", "Đồ thị và cách biểu diễn", "medium",
             "Định lý bắt tay: tổng bậc = 2 · số cạnh -> 12 = 2m -> m = 6."),
            ("Thuật toán Dijkstra có thể cho kết quả SAI khi đồ thị có:", "cạnh trọng số âm", "chu trình",
             "nhiều hơn 1000 đỉnh", "cạnh vô hướng", "A", "Duyệt đồ thị và đường đi ngắn nhất", "hard",
             "Dijkstra giả định trọng số không âm; có cạnh âm phải dùng Bellman–Ford."),
            ("Một cây có 10 đỉnh thì có bao nhiêu cạnh?", "8", "9", "10", "11", "B", "Cây và cây khung nhỏ nhất",
             "easy", "Cây n đỉnh luôn có đúng n − 1 cạnh."),
        ],
    },
]


# Tạo 1 khóa (nếu chưa có) và trả về id khóa
def create_course(db, spec: dict) -> int:
    course = q_one(db, "SELECT id FROM courses WHERE slug = :s", s=spec["slug"])
    if course:
        print(f"Khóa '{spec['title']}' đã có (id {course['id']}), không tạo lại.")
        return course["id"]
    teacher = q_one(db, "SELECT id FROM users WHERE email = :e", e=spec["teacher_email"]) or q_one(
        db, "SELECT id FROM users WHERE role = 'teacher' ORDER BY id LIMIT 1"
    )
    cid = execute(
        db,
        "INSERT INTO courses (teacher_id, title, slug, description, thumbnail, price, level, status) "
        "VALUES (:t, :title, :slug, :d, '', :p, :lvl, 'published')",
        t=teacher["id"], title=spec["title"], slug=spec["slug"], d=spec["description"],
        p=spec["price"], lvl=spec["level"],
    ).lastrowid
    n = 0
    for ch_no, (ch_name, lessons) in enumerate(spec["chapters"], 1):
        ch_id = execute(
            db, "INSERT INTO chapters (course_id, chapter_name, order_index) VALUES (:c, :n, :o)",
            c=cid, n=ch_name, o=ch_no,
        ).lastrowid
        for ls_no, (title, desc, dur) in enumerate(lessons, 1):
            n += 1
            # Video / tài liệu tạm dạng đường dẫn mẫu như các khóa khác; seed_lesson_docs.py gắn PDF thật sau
            execute(
                db,
                "INSERT INTO lessons (chapter_id, title, description, video_url, document_url, duration, "
                "order_index, is_free, status) VALUES (:ch, :t, :d, :v, :doc, :dur, :o, :free, 'published')",
                ch=ch_id, t=title, d=desc, v=f"videos/{spec['media_prefix']}_{n:02d}.mp4",
                doc=f"docs/{spec['media_prefix']}_{n:02d}.pdf", dur=dur, o=ls_no, free=1 if n <= 2 else 0,
            )
    qid = execute(
        db, "INSERT INTO quizzes (course_id, title, grading_method) VALUES (:c, :t, 'highest')",
        c=cid, t=spec["quiz_title"],
    ).lastrowid
    for i, (content, a, b, c, d, ans, topic, diff, expl) in enumerate(spec["questions"], 1):
        execute(
            db,
            "INSERT INTO questions (quiz_id, content, option_a, option_b, option_c, option_d, correct_answer, "
            "topic, difficulty, explanation, order_index) "
            "VALUES (:q, :content, :a, :b, :c, :d, :ans, :topic, :diff, :expl, :o)",
            q=qid, content=content, a=a, b=b, c=c, d=d, ans=ans, topic=topic, diff=diff, expl=expl, o=i,
        )
    print(f"Đã tạo khóa '{spec['title']}' (id {cid}) + quiz {qid} ({len(spec['questions'])} câu).")
    return cid


# Ghi thông tin các bài của khóa vào lessons.json để build_pdfs.py dựng tài liệu
def write_lessons_json(db, cid: int, title: str) -> list[int]:
    rows = q_all(
        db,
        "SELECT l.id, l.title, l.description, l.order_index AS lesson_no, ch.id AS chapter_id, "
        "ch.chapter_name, ch.order_index AS chapter_no FROM lessons l JOIN chapters ch ON ch.id = l.chapter_id "
        "WHERE ch.course_id = :c ORDER BY ch.order_index, l.order_index",
        c=cid,
    )
    ids = {r["id"] for r in rows}
    meta = [m for m in json.load(open(LESSONS_JSON, encoding="utf-8")) if m["lesson_id"] not in ids]
    meta += [
        {
            "lesson_id": r["id"], "course_id": cid, "course_title": title,
            "chapter_no": r["chapter_no"], "chapter_id": r["chapter_id"], "chapter_name": r["chapter_name"],
            "lesson_no": r["lesson_no"], "title": r["title"], "description": r["description"], "needs_doc": True,
        }
        for r in rows
    ]
    with open(LESSONS_JSON, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return [r["id"] for r in rows]


def main() -> None:
    db = SessionLocal()
    try:
        for spec in COURSES:
            cid = create_course(db, spec)
            ids = write_lessons_json(db, cid, spec["title"])
            print(f"  Id các bài: {' '.join(map(str, ids))}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
