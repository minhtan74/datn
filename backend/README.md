# StudyOnline — Backend (FastAPI)

REST API viết bằng **FastAPI + SQLAlchemy + MySQL**, thay cho bản PHP cũ
(`legacy-backend-php/`). Giữ nguyên "hợp đồng" HTTP: đường dẫn `/api/...`,
tham số query, phong bì JSON `{success, message?, ...data}` và thông điệp lỗi
tiếng Việt — nên frontend React chạy được mà gần như không phải sửa.

## Yêu cầu

- Python 3.11+ (đã test 3.13)
- MySQL 8.x với database `studyonline_db` (import từ `../database/*.sql`)

## Cài đặt & chạy

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env        # sửa DB_* cho khớp máy bạn (mặc định cổng 3306)

# chạy dev
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

- API: `http://127.0.0.1:8080`
- Swagger tự sinh: `http://127.0.0.1:8080/docs`
- Health: `GET /api/health`

Frontend trỏ tới backend qua `frontend/.env`:
`VITE_API_BASE_URL=http://127.0.0.1:8080`

## Cấu trúc

```
backend/
├── app/
│   ├── main.py              # tạo FastAPI, CORS, exception handler (phong bì lỗi), mount /uploads, gắn router
│   ├── core/
│   │   ├── config.py        # đọc .env (pydantic-settings)
│   │   ├── database.py      # engine + SessionLocal + helper q_all/q_one/execute (SQL thô, bám sát bản PHP)
│   │   ├── security.py      # JWT HS256 (giữ secret + payload như PHP), bcrypt + fallback plaintext seed
│   │   ├── dependencies.py  # get_current_user / require_roles(...)  (thay JwtMiddleware/RoleMiddleware)
│   │   └── responses.py     # ok(), ApiError, ApiJSONResponse (Decimal->"x.xx", datetime->"Y-m-d H:i:s")
│   ├── models/__init__.py   # SQLAlchemy models (cho Alembic + phase 4+)
│   └── routers/             # auth, users, courses, chapters, lessons, quizzes,
│                            #   enrollments, payments, progress, uploads, reports
├── alembic/                 # 0001_baseline đã stamp; migration bảng AI thêm ở phase sau
├── tests/
│   ├── parity_check.py      # so sánh từng byte phản hồi GET: PHP(:8001) vs FastAPI(:8080)
│   └── smoke_writes.py      # luồng ghi CRUD + học tập trên FastAPI, tự dọn dữ liệu
└── uploads/                 # video/ảnh/PDF do người dùng tải lên (served tại /uploads)
```

## Kiểm thử

```powershell
# 1. chạy legacy PHP song song để đối chiếu:
cd ..\legacy-backend-php ; php -S 127.0.0.1:8001 -t public
# 2. chạy FastAPI ở :8080
# 3. so sánh:
cd ..\backend
.\.venv\Scripts\python.exe tests\parity_check.py     # 37/37 PASS
.\.venv\Scripts\python.exe tests\smoke_writes.py     # 32/32 PASS
```

## Ghi chú migration (PHP -> FastAPI)

- Mật khẩu: `verify_password` chấp nhận cả plaintext (dữ liệu seed `123456`) lẫn bcrypt.
- JWT payload giữ khoá `id` (không phải `user_id`) + `fullname/email/role` để frontend không đổi.
- Quy ước route giữ nguyên kiểu bản PHP: 1 URL / resource, phân biệt bằng method + query
  (`?id=`, `?course_id=`, `?weekly=1`, `?ids_only=1`), `id` nằm trong body khi `PUT`.
- Side effect được port đúng: `POST /api/progress` tự enroll; `POST /api/payments` mock-complete + enroll.
- `GET /api/reports/summary` chỉ cho admin (đề bài bỏ Admin khỏi phạm vi chính — endpoint vẫn giữ, không phát triển thêm).

Danh sách endpoint: xem `../docs/api.md`.

## Endpoint mới (Phase 4–5)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/analytics/overview?course_id=` | Điểm quiz TB + mức năng lực + tỷ lệ hoàn thành + thời gian học + số lần làm quiz |
| GET | `/api/analytics/topics?course_id=` | Điểm theo chủ đề `[{topic, avg_score, status}]` + `weak_topics` / `strong_topics` |
| GET | `/api/analytics/quiz-progress?quiz_id=` | So sánh các lần làm cùng 1 quiz (`improvement` = lần cuối − lần đầu) |
| GET | `/api/recommendations?course_id=` | Gợi ý hiện tại (tính realtime) + `history` 10 dòng gần nhất |
| POST | `/api/recommendations/refresh` | Tính lại + **lưu** 1 dòng `recommendations` + snapshot `learning_analytics` |

- Bảng thêm: `learning_analytics`, `result_answers`, `recommendations` (Alembic 0002–0004, additive).
- Cột thêm cho `questions`: `topic`, `difficulty`, `explanation` (nullable).
- `POST /api/quizzes/submit` nay ghi thêm `result_answers` (chi tiết đúng/sai từng câu) — envelope phản hồi không đổi.
- `training/seed_result_answers.py` (TÙY CHỌN, chỉ demo): sinh `result_answers` khớp điểm cho các `results` seed cũ để dashboard phân tích topic có dữ liệu ngay.

## Endpoint mới (Phase 6 — RAG AI Tutor)

| Method | Path | Quyền | Mô tả |
|---|---|---|---|
| POST | `/api/ai/documents` | teacher/admin | multipart `file`+`course_id`+`lesson_id?`+`title?` → tải + trích xuất + chia đoạn + embed + lưu |
| GET | `/api/ai/documents?course_id=` | teacher/admin | danh sách tài liệu + trạng thái + số đoạn |
| DELETE | `/api/ai/documents?id=` | teacher/admin | xóa tài liệu (chunks cascade) + xóa file |
| POST | `/api/ai/chat` | đăng nhập | `{course_id, lesson_id?, conversation_id?, message}` → `{answer, sources[], conversation_id}` |
| GET | `/api/ai/conversations?course_id=` | đăng nhập | hội thoại của người dùng |
| GET | `/api/ai/conversations/{id}` | đăng nhập | tin nhắn trong hội thoại |
| DELETE | `/api/ai/conversations/{id}` | đăng nhập | xóa hội thoại |
| GET | `/api/ai/status` | đăng nhập | provider LLM + model embedding đang dùng |

**Kiến trúc RAG** (`app/ai/`):
- Vector store = MySQL (`document_chunks.embedding` JSON) + cosine bằng numpy — **không cần vector DB ngoài**.
- Embedding: `fastembed` (ONNX, không PyTorch), model đa ngữ `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều).
- Truy hồi lai: `0.55 · cosine(embedding) + 0.45 · trùng từ khóa`.
- LLM: `model_manager` gọi Gemini/OpenAI qua REST nếu đặt `LLM_API_KEY`; **không có key → chế độ trích xuất (extractive)** chạy offline khi demo.
- Chống lạc đề / bịa: cosine tốt nhất `< 0.55` → trả đúng câu *"Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."*; câu trả lời luôn kèm `sources` (tài liệu + trang) đã đưa vào ngữ cảnh.
- `training/sample_docs/` + `python training/seed_documents.py` — nạp sẵn 3 tài liệu mẫu cho khóa 1 & 2 để AI Tutor chạy ngay.

## Endpoint mới (Phase 9 — AI Quiz Generator)

| Method | Path | Quyền | Mô tả |
|---|---|---|---|
| POST | `/api/ai/generate-quiz` | teacher/admin | `{course_id, lesson_id?, number_of_questions, difficulty}` → `{questions[], meta}` — **preview, KHÔNG lưu** |
| POST | `/api/ai/quiz/approve` | teacher/admin | `{course_id, lesson_id?, title, questions[]}` → tạo `quizzes` (source='ai') + `questions` |

- Ngữ cảnh lấy từ RAG chunks của khóa/bài học. Có `LLM_API_KEY` → prompt JSON nghiêm ngặt + tự sửa/retry; không có → **heuristic điền chỗ trống** từ câu trong tài liệu (chạy offline).
- JSON hỏng sau 2 lần thử → báo lỗi rõ ràng, **không lưu**.

## Fine-tuning (Phase 7–8)

Xem `training/README.md`. Tóm tắt:
- `python training/prepare_dataset.py` → `dataset/{train,validation,test}.jsonl` (~303 ví dụ instruction/input/output).
- `python training/train_lora.py` — QLoRA (PEFT+TRL), **chạy trên Colab**, xuất LoRA adapter → đặt `LORA_ADAPTER_PATH` trong `.env`.
- `python training/evaluate.py --provider hf|gemini --label ...` — bảng số liệu Base vs Fine-tuned.

## Migration

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head      # lên 0006
.\.venv\Scripts\python.exe -m alembic current
```

| Rev | Nội dung |
|---|---|
| 0001_baseline | mốc schema hiện có (stamp) |
| 0002_analytics | `questions` +topic/difficulty/explanation · bảng `learning_analytics` |
| 0003_result_answers | bảng `result_answers` |
| 0004_recommendations | bảng `recommendations` |
| 0005_rag_tables | `documents`, `document_chunks`, `ai_conversations`, `ai_messages` |
| 0006_quiz_source_lesson | `quizzes` +`lesson_id` +`source` (manual/ai) |

