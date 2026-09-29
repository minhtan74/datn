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
| GET | `/api/quizzes` | – | `?id=` / `?course_id=` / tất cả; mỗi quiz kèm `question_count`, `source` manual/ai, `chapter_id` + `chapter_name` (ôn tập chương), `review_lesson_id` (+ `review_lesson_title` khi `?id=`) (ôn tập bài), `duration`/`passing_score`/`max_attempts` (NULL = không giới hạn); `?id=` kèm `my_attempts` khi đăng nhập |
| POST/PUT/DELETE | `/api/quizzes` | admin/teacher | POST `{course_id,title,description,duration?,passing_score?,max_attempts?}` (phút / % / số lần; trống hoặc 0 = không giới hạn) |
| GET | `/api/quizzes/questions` | – | **bắt buộc** `?quiz_id=` hoặc `?id=`; học viên: 403 khi hết lượt, đề có giờ trả thêm `attempt_token` + `time_limit_sec` |
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
| POST | `/api/payments` | ✔ | `{course_id, method}` (`card\|bank_transfer\|momo\|zalopay`); khóa 0đ → enroll thẳng; có phí → tạo giao dịch `completed` (giả lập) + enroll |
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

## 12. AI — `/api/ai` *(mới)*

| Method | Path | Auth | Ghi chú |
|---|---|---|---|
| GET | `/api/ai/status` | ✔ | provider LLM + model embedding |
| POST | `/api/ai/documents` | teacher/admin | multipart `file`+`course_id`+`lesson_id?`+`title?` → tải + ingest |
| GET | `/api/ai/documents?course_id=` | teacher/admin | danh sách tài liệu + trạng thái |
| DELETE | `/api/ai/documents?id=` | teacher/admin | xoá tài liệu + chunk + file |
| POST | `/api/ai/chat` | ✔ | `{course_id, lesson_id?, conversation_id?, message}` → `{answer, sources[], conversation_id}` |
| GET | `/api/ai/conversations?course_id=` | ✔ | hội thoại của người dùng |
| GET | `/api/ai/conversations/{id}` | ✔ | các tin nhắn |
| DELETE | `/api/ai/conversations/{id}` | ✔ | xoá hội thoại |
| POST | `/api/ai/generate-quiz` | teacher/admin | `{course_id, lesson_id?, chapter_id?, number_of_questions, difficulty}` hoặc thay 2 trường cuối bằng `difficulty_mix: {easy, medium, hard}` (mỗi mức 0–20, tổng ≤ 30; `meta.distribution` = số câu sinh được mỗi mức). Mỗi câu kèm kết quả AI tự giải lại: `verified` = đáp án khớp, hoặc `verify: {answer, reason}` khi AI ra đáp án khác (`meta.verification` = số câu khớp / bị gắn cờ) → `{questions[], meta}` — **preview, KHÔNG lưu** |
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
