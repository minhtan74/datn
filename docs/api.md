# Tham chiếu API — StudyOnline (FastAPI)

Base URL (dev): `http://127.0.0.1:8080` · Swagger tự sinh: `/docs`

## Quy ước chung

- **Xác thực:** header `Authorization: Bearer <JWT>` (HS256, hết hạn 7 ngày).
- **Phong bì phản hồi:**
  - Thành công: `{"success": true, "message"?: "...", ...dữ liệu}` — HTTP 200
  - Lỗi: `{"success": false, "message": "<tiếng Việt>"}` — HTTP = mã lỗi (400/401/403/404/409/422/500)
- **Kiểu dữ liệu:** `DECIMAL` trả về dạng chuỗi `"599000.00"`, `DATETIME` dạng `"YYYY-MM-DD HH:MM:SS"`.
- **Quy ước route (giữ từ bản PHP):** một URL cho mỗi tài nguyên; phân biệt bằng
  HTTP method + query string; `id` nằm trong **body** khi `PUT`, trong **query** khi `DELETE`.

---

## 1. Auth — `/api/auth`

| Method | Path | Auth | Body / Query | Ghi chú |
|---|---|---|---|---|
| POST | `/login` | – | `{email, password}` | → `{token, user}`; chấp nhận mật khẩu plaintext (seed) hoặc bcrypt |
| POST | `/register` | – | `{fullname, email, password, confirm_password}` | luôn tạo vai trò `student` |
| POST | `/logout` | – | – | không trạng thái, chỉ trả success |
| GET | `/me` | ✔ | – | `{user:{id,fullname,email,role}}` |
| POST | `/change-password` | ✔ | `{old_password, new_password}` | mật khẩu mới ≥ 6 ký tự |

Đăng ký công khai chỉ dành cho học viên, kể cả khi client tự gửi thêm `role`.
Admin cấp tài khoản Giảng viên qua `POST /api/users` với `role="teacher"` và mật khẩu ban đầu;
giảng viên đăng nhập rồi đổi mật khẩu qua `/api/auth/change-password`.

## 2. Users — `/api/users`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/users` | admin/teacher | `?id=` → chi tiết (teacher chỉ xem chính mình); không id → danh sách |
| POST | `/api/users` | admin | `{fullname,email,password,role}` |
| PUT | `/api/users` | đăng nhập | non-admin chỉ sửa chính mình, không đổi vai trò của mình |
| DELETE | `/api/users?id=` | admin | không tự xoá tài khoản mình |

## 3. Courses / Chapters / Lessons

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/courses` | – | `?id=` → chi tiết (kèm `teacher_name`); danh sách sắp theo id DESC |
| POST/PUT/DELETE | `/api/courses` | admin/teacher | POST `{title,description,thumbnail}`; PUT `{id,...}`; DELETE `?id=` |
| GET | `/api/chapters` | – | **bắt buộc** `?course_id=` hoặc `?id=`; mỗi chương kèm `review_quiz_id`, `review_question_count` |
| POST/PUT/DELETE | `/api/chapters` | admin/teacher | POST `{course_id,chapter_name}` |
| POST | `/api/chapters/review` | admin/teacher | `{chapter_id}` → `{quiz_id}` — lấy/tạo bộ câu hỏi ôn tập của chương (quiz có `chapter_id`, mỗi chương 1 bộ); câu hỏi quản lý qua `/api/quizzes/questions` |
| GET | `/api/lessons` | – | **bắt buộc** `?chapter_id=` hoặc `?id=`; mỗi bài kèm `review_quiz_id`, `review_question_count` |
| POST/PUT/DELETE | `/api/lessons` | admin/teacher | POST `{chapter_id,title,description,video_url,document_url}` |
| POST | `/api/lessons/review` | admin/teacher | `{lesson_id}` → `{quiz_id}` — lấy/tạo bộ câu hỏi ôn tập theo kiến thức của bài (quiz có `review_lesson_id`, mỗi bài 1 bộ) |

## 4. Quizzes — `/api/quizzes`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/quizzes` | – | `?id=` / `?course_id=` / tất cả; mỗi quiz kèm `question_count`, `source` manual/ai, `chapter_id` + `chapter_name` (ôn tập chương), `review_lesson_id` (+ `review_lesson_title` khi `?id=`) (ôn tập bài), `duration`/`passing_score`/`max_attempts` (NULL = không giới hạn). `?id=` chỉ đọc thông tin, không tạo lượt: khi đăng nhập kèm `my_attempts`, `can_attempt`, `is_preview`. Danh sách và chi tiết của học viên kèm `my_status`: `in_progress`, `remaining_sec`, `attempts_used` (gồm cả lượt hết hạn/chưa nộp), `attempts_left`, `submitted`, `graded_percent`, `passed`. Frontend dùng số lượt đã dùng để phân biệt Chưa làm với Chưa nộp; bộ lọc `status` trên trang `/quiz` được xử lý ở frontend |
| POST/PUT/DELETE | `/api/quizzes` | admin/teacher | POST `{course_id,title,description,duration?,passing_score?,max_attempts?}` (phút / % / số lần; trống hoặc 0 = không giới hạn) |
| GET | `/api/quizzes/questions` | – | **bắt buộc** `?quiz_id=` hoặc `?id=`. Với `quiz_id`, frontend chỉ gọi khi bấm Bắt đầu/Tiếp tục; học viên tạo hoặc tiếp tục lượt, nhận `attempt_token`, `attempts_used`; đề có giờ thêm `time_limit_sec`, `remaining_sec`. `resume_only=1` chỉ tiếp tục lượt còn hiệu lực, 403 nếu đã kết thúc (không tạo lượt mới). 403 khi hết lượt hoặc không có quyền; giảng viên chủ khóa/admin xem thử không tạo lượt |
| POST/PUT/DELETE | `/api/quizzes/questions` | admin/teacher | `{quiz_id,content,option_a..d,correct_answer,order_index}` |
| POST | `/api/quizzes/submit` | ✔ | `{quiz_id, answers:{"<question_id>":"A".."D"}}` → chấm điểm + `details[]` + `passed` (null nếu không đặt điểm đạt) + `answers_revealed`, `attempts_used`, `attempts_left`. Đề có `max_attempts`: chưa tới lượt cuối thì `details[].correct_answer = null` (chỉ báo đúng/sai); ghi `results` + `result_answers`. Đề có giờ cần `attempt_token` (HMAC, hạn = thời gian + 60s); hết lượt → 403 |

## 5. Enrollments — `/api/enrollments`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/enrollments` | ✔ | `?course_id=` → `{enrolled}` · `?ids_only=1` → `{data:[course_id]}` · else theo vai trò |
| POST | `/api/enrollments` | ✔ | `{course_id}`; 409 nếu đã đăng ký |
| DELETE | `/api/enrollments?course_id=` | ✔ | huỷ đăng ký |

## 6. Payments (mock) — `/api/payments`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/payments` | ✔ | theo vai trò (admin all / teacher theo khóa dạy / student của mình) |
| POST | `/api/payments` | ✔ | `{course_id}`; khóa 0đ → ghi danh; khóa có phí → 400, yêu cầu thanh toán qua VNPay |
| POST | `/api/payments/vnpay/create` | ✔ | `{course_id}`; tạo đơn `pending`, trả `payment_url` để chuyển sang VNPay; chỉ ghi danh sau khi xác nhận thanh toán |
| GET | `/api/payments/check?course_id=` | ✔ | `{has_paid, enrolled}` |

## 7. Progress — `/api/progress`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/progress` | ✔ | `?course_id=` → `[lesson_id đã hoàn thành]` · `?weekly=1` → 7 ngày · `?recent=1&limit=` → hoạt động gần đây · else tổng hợp theo khóa |
| POST | `/api/progress` | ✔ | `{lesson_id, watched_sec, is_completed}`; tự động enroll nếu chưa |

## 8. Reports — `/api/reports`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/reports/summary?range=` | admin | `range = today\|7d\|30d\|1y`; tổng quan doanh thu / top khóa / gần đây |

## 9. Uploads — `/api/upload`

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| POST | `/api/upload` | ✔ | multipart `file` + `type` (`video\|image\|document`); giới hạn 500MB / 5MB / 20MB → `{url}` |

## 10. Learning Analytics — `/api/analytics` *(mới)*

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/analytics/overview?course_id=` | ✔ | điểm quiz TB, `level`, % hoàn thành, thời gian học, số lần làm quiz |
| GET | `/api/analytics/topics?course_id=` | ✔ | `[{topic, avg_score, status}]` + `weak_topics` / `strong_topics` |
| GET | `/api/analytics/quiz-progress?quiz_id=` | ✔ | các lần làm + `improvement` |

## 11. Recommendation — `/api/recommendations` *(mới)*

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/recommendations?course_id=` | ✔ | `{current, history[]}` (current tính realtime) |
| POST | `/api/recommendations/refresh` | ✔ | tính lại + **lưu** + snapshot `learning_analytics` |
| POST | `/api/recommendations/study` | ✔ | `{topic_id}` hoặc `{course_id, knowledge_kind: "chapter"\|"lesson", unit_id}` → ghi mốc trước ôn, không tạo mốc trùng khi chưa có kết quả mới |
| GET | `/api/recommendations/progress` | ✔ | tối đa 10 mốc ôn chủ đề/chương/bài của chính học viên: `checkpoint_kind`, `before`, `after`, `difference_pct`, `same_questions`, `sufficient_data` |

Gợi ý chương/bài có `type: "review_knowledge"`, `knowledge_evidence` (mã, loại, tên, khóa, số đúng/tổng, tỷ lệ, nguồn kết quả), `action_url`, `action_label` và `practice_url`, `practice_label` khi còn bộ luyện hợp lệ. `current.based_on.knowledge` trả `{units[], unmapped_answers}`; căn cứ chương/bài dùng lượt mới nhất của từng bài qua các loại đề, độc lập cách tính điểm chính thức.

`GET /api/quizzes/knowledge-outline?course_id=` dành cho chủ khóa/admin, trả `{chapters[], lessons[]}`. POST/PUT `/api/quizzes/questions` và từng phần tử `questions[]` của `/api/ai/quiz/approve` nhận `knowledge_chapter_id`, `knowledge_lesson_id` (nullable); API kiểm tra khóa, chương và phạm vi bộ ôn. Sinh AI giữ chương của mỗi lô và giới hạn mã bài đề xuất trong phạm vi tài liệu đã chọn. Câu không rõ bài có thể chỉ gắn chương.

Nộp bài và đọc kết quả trả thêm `knowledge: {units[], unmapped_answers, min_questions, review_threshold}` của riêng lượt nộp; không làm lộ đáp án đang bị ẩn. Mã và tên chương/bài được lưu ở `result_answers` với `knowledge_version=2`; chỉnh câu hỏi không thay đổi kết quả cũ. Migration `0021_knowledge_scope` bổ sung các cột phân loại và bảng `knowledge_study_checkpoints`; dữ liệu cũ khôi phục được ghi version 1, phần không xác định vẫn để trống.

## 12. AI — `/api/ai` *(mới)*

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/ai/status` | ✔ | provider LLM + model embedding |
| POST | `/api/ai/documents` | teacher/admin | multipart `file`+`course_id`+`lesson_id?`+`title?` → tải + ingest |
| GET | `/api/ai/documents?course_id=` | teacher/admin | danh sách tài liệu + trạng thái |
| DELETE | `/api/ai/documents?id=` | teacher/admin | xoá tài liệu + chunk + file |
| POST | `/api/ai/chat` | ✔ | `{course_id, lesson_id?, conversation_id?, message}` → `{answer, sources[], conversation_id, used_context, needs_clarification, clarification_kind, response_status, error_code, retryable}`. `response_status`: ok/error/fallback. Lỗi LLM không có dự phòng: HTTP503, `success=false`, vẫn kèm `data.conversation_id` để gửi lại đúng hội thoại; dự phòng: HTTP200 có nguồn và nhãn fallback. Câu thiếu thông tin được hỏi lại, không gắn nguồn. Lịch sử giữ metadata khi tải lại. `conversation_id` phải cùng khóa/phạm vi bài học; `lesson_id` phải thuộc khóa được chọn |
| GET | `/api/ai/conversations?course_id=` | ✔ | hội thoại của người dùng |
| GET | `/api/ai/conversations/{id}` | ✔ | các tin nhắn |
| DELETE | `/api/ai/conversations/{id}` | ✔ | xoá hội thoại |
| POST | `/api/ai/generate-quiz` | teacher/admin | `{course_id, lesson_id?, chapter_id?, number_of_questions, difficulty}` hoặc thay 2 trường cuối bằng `difficulty_mix: {easy, medium, hard}` (mỗi mức 0–20, tổng ≤ 30; `meta.distribution` = số câu sinh được mỗi mức). Mỗi câu kèm kết quả AI tự giải lại: `verified` = đáp án khớp, hoặc `verify: {answer, reason}` khi AI ra đáp án khác (`meta.verification` = số câu khớp / bị gắn cờ) → `{questions[], meta}` — **preview, KHÔNG lưu** |
| POST | `/api/ai/generate-quiz/stream` | teacher/admin | Cùng body với endpoint trên. Trả `application/x-ndjson`, mỗi dòng một sự kiện: `status` (thông báo), `batch` (`difficulty`, `questions[]` chưa kiểm tra), `heartbeat`, `complete` (`data: {questions[], meta}` đã qua bước kiểm tra), hoặc `error` (`status`, `message`). Quyền truy cập được kiểm tra trước khi mở luồng. Lỗi sau khi mở luồng nằm trong sự kiện `error`; client cần nhận `complete` mới coi là hoàn tất. Không tự lưu quiz. |
| POST | `/api/ai/quiz/approve` | teacher/admin | `{course_id, lesson_id?, chapter_id?, review_lesson_id?, title, questions[], duration?, passing_score?, max_attempts?}` → tạo `quizzes` (`source='ai'`) + `questions`; có `chapter_id` / `review_lesson_id` thì thêm vào bộ ôn tập của chương / bài học (không cần `title`) |

---

## Cơ sở dữ liệu

**10 bảng LMS (giữ nguyên):** `users`, `courses`, `chapters`, `lessons`, `enrollments`,
`lesson_progress`, `quizzes`, `questions`, `results`, `payments`.

**6 bảng AI (thêm, additive — Alembic 0002–0006):**

| Bảng | Cột chính |
|---|---|
| `result_answers` | result_id, question_id, chosen, is_correct |
| `learning_analytics` | user_id, course_id, avg_quiz_score, completion_pct, completed_lessons, total_time_sec, quiz_attempts, weak_topics(JSON), strong_topics(JSON), **UNIQUE(user_id,course_id)** |
| `recommendations` | user_id, course_id?, level, summary, items(JSON), based_on(JSON), created_at |
| `documents` | course_id, lesson_id?, uploaded_by, title, filename, file_path, file_type, status, pages, chunk_count, error |
| `document_chunks` | document_id, course_id, lesson_id?, chunk_index, page, content, **embedding(JSON)**, token_count |
| `ai_conversations` | user_id, course_id?, lesson_id?, title, updated_at |
| `ai_messages` | conversation_id, role(user/assistant), content, sources(JSON) |

**Cột thêm cho bảng cũ:** `questions.topic` / `questions.difficulty` / `questions.explanation`;
`quizzes.lesson_id` / `quizzes.source` (`manual`/`ai`).

## Khôi phục mật khẩu

Giảng viên/Học viên liên hệ Admin quản lý để xác minh và cấp lại; Admin duy nhất dùng công cụ riêng trên máy chủ.
Không còn API công khai đặt lại mật khẩu bằng token/email. Xem [quy trình](password-recovery.md).

## An toàn giao dịch Admin

`POST /api/payments/reconcile-pending` nhận `{q, course_id, date_from, date_to}` và chỉ xử lý
đơn VNPay đang chờ khớp bộ lọc. `GET /api/payments/detail?id=...` chỉ dành cho Admin.
`POST /api/payments/refund-reconcile` nhận `{id}` để truy vấn kết quả hoàn tiền hoặc phục hồi phần cập nhật DB,
không gửi lại yêu cầu hoàn tiền. Xem [bản sửa mục 1–4](admin-fixes-1-4.md).
