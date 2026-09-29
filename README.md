# StudyOnline — Nền tảng học tập trực tuyến hỗ trợ cá nhân hoá học tập ứng dụng AI

Đồ án tốt nghiệp. Hệ thống LMS 2 vai trò (**Giảng viên** / **Học viên**) với ba trục AI:

1. **RAG AI Tutor** — hỏi đáp dựa trên tài liệu khóa học, có trích dẫn nguồn.
2. **AI Quiz Generator** — sinh câu hỏi trắc nghiệm từ tài liệu → giảng viên duyệt → lưu.
3. **Personalized Recommendation** — rule-based engine trên số liệu học tập thật.

| Lớp | Công nghệ |
|---|---|
| Frontend | React 18 · Vite · React Router · Axios · Chart.js |
| Backend | **FastAPI** · SQLAlchemy · Pydantic · Alembic · JWT (HS256) · bcrypt |
| CSDL | MySQL 8 |
| AI | fastembed (embedding ONNX, không cần PyTorch) · vector store trên MySQL · LLM qua REST (Gemini/OpenAI, tuỳ chọn) · LoRA/QLoRA (PEFT+TRL, fine-tune trên Colab) |

> Backend cũ viết bằng PHP đã được thay bằng FastAPI. Migration đã đạt parity 100%
> (xem [MIGRATION_PLAN.md](MIGRATION_PLAN.md)); mã nguồn PHP/vanilla-JS cũ đã được gỡ bỏ khỏi thư mục làm việc
> (vẫn còn trong lịch sử Git ở các commit trước migration nếu cần đối chiếu lại).

---

## Cấu trúc thư mục

```
studyonline/
├── frontend/            React + Vite (SPA)
│   └── src/  api/ services/ context/ hooks/ routes/ layouts/ components/ pages/
├── backend/            FastAPI
│   ├── app/
│   │   ├── main.py       khởi tạo app, CORS, exception handler, mount /uploads, gắn router
│   │   ├── core/         config · database · security · dependencies · responses
│   │   ├── models/       SQLAlchemy models
│   │   ├── routers/      auth, users, courses, chapters, lessons, quizzes,
│   │   │                 enrollments, payments, progress, uploads, reports,
│   │   │                 analytics, recommendations, ai
│   │   ├── services/     analytics_service
│   │   └── ai/           rag/ (loader·splitter·embeddings·vector_store·retriever·pipeline)
│   │                     model_manager · recommendation · quiz_generator
│   ├── alembic/          6 migration (0001 baseline → 0006)
│   ├── training/         dataset/ · prepare_dataset.py · train_lora.py · evaluate.py
│   │                     sample_docs/ · seed_documents.py · seed_result_answers.py
│   └── tests/            smoke_writes.py · test_api.py (pytest)
├── database/            studyonline_db.sql · migration_add_payments.sql · sample_data.sql
├── docs/               architecture · rag · fine-tuning · recommendation · api
├── docker-compose.yml
└── MIGRATION_PLAN.md    phân tích + kế hoạch migration PHP → FastAPI
```

---

## Cách chạy — Docker (nhanh nhất)

```bash
docker compose up -d --build
```

- Frontend: <http://localhost:8088>
- API + Swagger: <http://localhost:8080/docs>

MySQL tự khởi tạo schema + dữ liệu mẫu; backend tự chạy `alembic upgrade head`.

(Tuỳ chọn) nạp tài liệu mẫu cho AI Tutor và dữ liệu phân tích demo:

```bash
docker compose exec backend python training/seed_documents.py
docker compose exec backend python training/seed_result_answers.py
```

---

## Cách chạy — Windows (script có sẵn, khuyên dùng khi dev local)

Đã có sẵn MySQL local (không phải service Windows), venv backend và
`node_modules` frontend thì chỉ cần 2 lệnh sau, chạy tại thư mục gốc dự án:

```powershell
# Khởi động MySQL (port 3306) + Backend FastAPI (:8080) + Frontend Vite (:5173)
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1

# Dừng lại (tắt các process đang lắng nghe ở 3 port trên)
powershell -ExecutionPolicy Bypass -File .\stop-dev.ps1
```

`start-dev.ps1` mở 3 cửa sổ PowerShell riêng cho MySQL/Backend/Frontend; nếu
port nào đã có tiến trình chạy sẵn thì script bỏ qua bước khởi động port đó.
Đóng cửa sổ tương ứng (hoặc Ctrl+C bên trong) để tắt từng dịch vụ, hoặc dùng
`stop-dev.ps1` để tắt cả 3 cùng lúc.

Nếu máy chưa từng chạy dự án (chưa có venv/`.venv`, chưa có dữ liệu MySQL ở
`backend/data/mysql-data`, chưa `npm install`), làm theo phần **Dev (không
Docker)** bên dưới để khởi tạo lần đầu, sau đó các lần sau chỉ cần
`start-dev.ps1`.

---

## Cách chạy — Dev (không Docker)

### 1. CSDL
Tạo MySQL database `studyonline_db` (utf8mb4) rồi import theo thứ tự:
`database/studyonline_db.sql` → `migration_add_payments.sql` → `sample_data.sql`.

### 2. Backend
```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # Linux/macOS
cp .env.example .env          # sửa DB_* cho khớp máy
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

### 3. Frontend
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://127.0.0.1:8080" > .env
npm run dev        # http://localhost:5173
```

### 4. (Tuỳ chọn) dữ liệu AI mẫu
```bash
cd backend
.venv/Scripts/python training/seed_documents.py        # 3 tài liệu cho AI Tutor
.venv/Scripts/python training/seed_result_answers.py   # để dashboard phân tích có dữ liệu
```

---

## Tài khoản mẫu (mật khẩu chung `123456`)

| Vai trò | Email |
|---|---|
| Admin | `admin@gmail.com` |
| Giảng viên | `an.nguyen@studyonline.vn`, `binh.tran@studyonline.vn` |
| Học viên | `em.hoang@gmail.com`, `phuong.vu@gmail.com` |

---

## Kiểm thử

```bash
cd backend
.venv/Scripts/python -m pytest                       # 17 test API (in-process, tự dọn dữ liệu)
.venv/Scripts/python tests/smoke_writes.py           # luồng ghi CRUD + học tập
```

---

## Tài liệu

| File | Nội dung |
|---|---|
| [MIGRATION_PLAN.md](MIGRATION_PLAN.md) | Phân tích hệ thống cũ + bản đồ migration PHP → FastAPI |
| [docs/architecture.md](docs/architecture.md) | Kiến trúc tổng thể, luồng xác thực, quyết định thiết kế |
| [docs/rag.md](docs/rag.md) | RAG AI Tutor: ingest, retrieval, đánh giá |
| [docs/fine-tuning.md](docs/fine-tuning.md) | Dataset, LoRA/QLoRA, đánh giá Base vs Fine-tuned |
| [docs/recommendation.md](docs/recommendation.md) | Learning Analytics + Rule Engine + vòng lặp cá nhân hoá |
| [docs/api.md](docs/api.md) | Tham chiếu toàn bộ endpoint + schema CSDL |
| [backend/README.md](backend/README.md) | Chi tiết backend |
| [backend/training/README.md](backend/training/README.md) | Hướng dẫn fine-tune trên Colab |
