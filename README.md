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

> Backend cũ viết bằng PHP đã được thay bằng FastAPI. Migration đã đạt parity 100%;
> mã nguồn PHP/vanilla-JS cũ đã được gỡ bỏ khỏi thư mục làm việc
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
└── docker-compose.yml
```

---

## Cách chạy

Có 2 cách. **Docker** để chạy thử nhanh trên máy bất kỳ (dữ liệu mẫu). **Windows local** là cách dùng
hằng ngày khi phát triển và khi demo với dữ liệu thật.

| Cách | Cần cài | Giao diện | API + Swagger | MySQL |
|---|---|---|---|---|
| Docker | Docker Desktop | <http://localhost:8088> | <http://localhost:8080/docs> | `localhost:3307` |
| Windows local | Python 3.12+, Node.js 18+, MySQL 8.4 | <http://localhost:5173> | <http://127.0.0.1:8080/docs> | `localhost:3306` |

---

### Cách 1 — Docker (nhanh nhất)

```bash
docker compose up -d --build
```

MySQL tự tạo bảng + nạp dữ liệu mẫu; backend tự chạy `alembic upgrade head` khi khởi động.

Nạp thêm dữ liệu demo (tuỳ chọn, chạy theo đúng thứ tự):

```bash
docker compose exec backend python training/seed_documents.py              # tài liệu mẫu cho AI Tutor
docker compose exec backend python training/seed_result_answers.py         # chi tiết câu trả lời cho kết quả quiz cũ
docker compose exec backend python training/seed_learning_data.py          # thêm lượt làm quiz + tiến độ học
docker compose exec backend python training/fix_report_data.py             # chỉnh ngày tháng cho trang Báo cáo
docker compose exec backend python training/lesson_docs/seed_lesson_docs.py  # gắn PDF tài liệu cho bài học
```

Dùng AI thật (Gemini): điền `LLM_API_KEY` trong `docker-compose.yml` rồi chạy lại `docker compose up -d`.
Để trống thì AI chạy chế độ offline (trích xuất từ tài liệu, kém hơn).

Dừng: `docker compose down` (thêm `-v` để xoá luôn dữ liệu).

---

### Cách 2 — Windows local

#### Lần đầu tiên (cài đặt)

**1. CSDL.** Tạo database `studyonline_db` (utf8mb4) trên MySQL 8.4, rồi import lần lượt:

```powershell
mysql -u root -p -e "CREATE DATABASE studyonline_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
mysql -u root -p studyonline_db < database/studyonline_db.sql
mysql -u root -p studyonline_db < database/migration_add_payments.sql
mysql -u root -p studyonline_db < database/sample_data.sql
```

**2. Backend.**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env           # rồi sửa DB_PASS, LLM_API_KEY (Gemini), VNPAY_* nếu có
.venv\Scripts\python -m alembic upgrade head
```

Các biến quan trọng trong `backend/.env`:

| Biến | Ý nghĩa |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` | Kết nối MySQL (mặc định `127.0.0.1:3306`, user `root`) |
| `LLM_PROVIDER`, `LLM_API_KEY` | `gemini` + khoá Gemini; để trống khoá -> AI chạy offline |
| `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET` | Khoá VNPay Sandbox; để trống -> nút thanh toán báo "chưa cấu hình" |
| `PAYMENT_MOCK` | `true` = thanh toán giả lập, dùng khi demo không có mạng |

**3. Frontend.**

```powershell
cd frontend
npm install
echo VITE_API_BASE_URL=http://127.0.0.1:8080 > .env
```

**4. Dữ liệu demo (tuỳ chọn).** Chạy trong thư mục `backend`, đúng thứ tự như ở Cách 1:

```powershell
.venv\Scripts\python training/seed_documents.py
.venv\Scripts\python training/seed_result_answers.py
.venv\Scripts\python training/seed_learning_data.py
.venv\Scripts\python training/fix_report_data.py
.venv\Scripts\python training/lesson_docs/seed_lesson_docs.py
.venv\Scripts\python training/seed_extra_courses.py      # thêm khóa Tiếng Anh, Toán rời rạc
```

PDF tài liệu bài học nằm sẵn trong `backend/training/lesson_docs/pdf/`. Muốn sửa nội dung: chỉnh file `.md`
trong `backend/training/lesson_docs/content/` rồi chạy `python training/lesson_docs/build_pdfs.py` (cần Chrome
hoặc Edge) để dựng lại.

#### Các lần sau (chạy hằng ngày)

**Bước 1 — bật MySQL.** Nếu MySQL được cài dạng service Windows (tên mặc định `MySQL84`), mở PowerShell
bằng **Run as Administrator**:

```powershell
net start MySQL84
```

**Bước 2 — bật backend + frontend** (PowerShell thường, tại thư mục gốc dự án):

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

Script mở các cửa sổ PowerShell riêng cho Backend (`:8080`) và Frontend (`:5173`). Cổng nào đã có
chương trình chạy thì bỏ qua. Nếu cổng 3306 còn trống, script tự bật một MySQL riêng với dữ liệu ở
`backend/data/mysql-data` (chỉ dùng khi không cài MySQL dạng service).

**Bước 3 — mở <http://localhost:5173>** và đăng nhập bằng tài khoản mẫu bên dưới.

**Tắt:**

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-dev.ps1
```

> `stop-dev.ps1` tắt MỌI chương trình đang chiếm cổng 3306 / 8080 / 5173. Nếu MySQL chạy dạng service,
> nên tắt MySQL bằng `net stop MySQL84` (quyền Administrator) thay vì để script tắt cưỡng bức.

#### Lỗi hay gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Backend báo cổng 8080 đang bận | Còn backend cũ chạy ngầm: chạy `stop-dev.ps1` rồi bật lại |
| Đăng nhập báo lỗi kết nối / 500 | MySQL chưa chạy: kiểm tra Bước 1 |
| AI Tutor trả lời kiểu trích câu + "Trợ giảng AI đang tạm gián đoạn" | Thiếu `LLM_API_KEY` hoặc Gemini hết lượt gọi trong ngày |
| Sửa `.env` nhưng không có tác dụng | Tắt hẳn cửa sổ Backend rồi bật lại (`--reload` chỉ tự khởi động lại khi sửa file `.py`) |

---

## Tài khoản mẫu (mật khẩu chung `123456`)

| Vai trò | Email | Quyền chính |
|---|---|---|
| Admin | `admin@gmail.com` | Quản lý người dùng, khóa học, giao dịch (đối soát, hoàn tiền), báo cáo |
| Giảng viên | `an.nguyen@studyonline.vn`, `binh.tran@studyonline.vn` | Quản lý khóa / chương / bài / quiz; tải tài liệu cho AI Tutor; sinh đề bằng AI; nhập đề từ Word |
| Học viên | `em.hoang@gmail.com`, `phuong.vu@gmail.com` | Học bài, làm quiz, xem tiến độ & phân tích, nhận gợi ý, hỏi AI Tutor |

---

## Kiểm thử

Chạy trong thư mục `backend`. Test API có ghi rồi tự dọn dữ liệu — nên trỏ vào một database thử
(đặt `DB_PORT` / `DB_NAME` khác) thay vì database đang chứa dữ liệu thật.

```powershell
.venv\Scripts\python -m pytest                              # test API + test nhập đề Word
.venv\Scripts\python tests/smoke_writes.py                  # luồng ghi CRUD + học tập
.venv\Scripts\python training/rag_eval/evaluate_rag.py      # đánh giá AI Tutor trên 124 câu hỏi
```

Kết quả đánh giá AI Tutor được lưu ở `backend/training/rag_eval/results/`.

---

## Cấu hình AI (tuỳ chọn)

Không có khoá API, AI chạy **offline**: AI Tutor trả lời bằng cách trích câu từ tài liệu, sinh đề tạo câu
điền chỗ trống. Demo được ngay nhưng chất lượng thấp hơn. Để dùng LLM thật, sửa `backend/.env`:

```ini
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
LLM_API_KEY=<khoá của bạn>
```

| Nhà cung cấp | Cấu hình |
|---|---|
| Gemini (đang dùng) | `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-3.1-flash-lite`, `LLM_API_KEY=...` |
| OpenAI | `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`, `LLM_API_KEY=sk-...` |
| Claude | `LLM_PROVIDER=claude`, `LLM_MODEL=claude-haiku-4-5-20251001`, `LLM_API_KEY=sk-ant-...` |
| Ollama (chạy trên máy, không cần khoá) | `LLM_PROVIDER=openai`, `LLM_MODEL=qwen2.5:7b`, `LLM_BASE_URL=http://localhost:11434/v1` |
| Groq / DeepSeek / OpenRouter | `LLM_PROVIDER=openai` + `LLM_BASE_URL` của dịch vụ + khoá (xem `backend/.env.example`) |

Dùng Ollama: cài từ ollama.com, chạy `ollama pull qwen2.5:7b` một lần, giữ Ollama chạy nền rồi khởi động
lại backend. Máy dưới 16 GB RAM nên dùng `qwen2.5:3b`.

Sửa `.env` xong phải tắt hẳn cửa sổ Backend rồi bật lại. Fine-tune AI Quiz Generator (LoRA/QLoRA) chạy trên
Google Colab — xem `backend/training/README.md`.

---

## Thanh toán VNPay Sandbox

Khóa có phí thanh toán qua **VNPay Sandbox** (môi trường thử, không trừ tiền thật).

1. Đăng ký tài khoản test tại <https://sandbox.vnpayment.vn/devreg/> — VNPay gửi email gồm
   **vnp_TmnCode** và **vnp_HashSecret**.
2. Điền vào `backend/.env` rồi khởi động lại backend:
   ```ini
   VNPAY_TMN_CODE=<mã website>
   VNPAY_HASH_SECRET=<chuỗi bí mật>
   ```
   (Docker: đặt 2 biến này trong môi trường hoặc file `.env` cạnh `docker-compose.yml`.)
3. Mở web bằng đúng địa chỉ trong `FRONTEND_URL` (mặc định <http://localhost:5173>). VNPay trả về địa chỉ
   này; mở bằng `127.0.0.1` sẽ mất phiên đăng nhập.
4. Học viên → Khám phá khóa học → Đăng ký khóa có phí → **Thanh toán qua VNPay**. Thẻ test (ngân hàng **NCB**):

   | Số thẻ | Tên chủ thẻ | Ngày phát hành | OTP |
   |---|---|---|---|
   | `9704198526191432198` | `NGUYEN VAN A` | `07/15` | `123456` |

Không có mạng khi demo: đặt `PAYMENT_MOCK=true` để dùng thanh toán giả lập.

**Luồng xử lý:** tạo đơn `pending` → chuyển sang VNPay → VNPay đưa trình duyệt về
`/api/payments/vnpay/return` → backend kiểm tra **chữ ký HMAC-SHA512 + số tiền** → thành công: đơn
`completed` + ghi danh; thất bại / huỷ: đơn `failed`, không ghi danh → chuyển về `/student/payment-result`.
`/api/payments/vnpay/ipn` là URL IPN (VNPay gọi thẳng server), chỉ dùng được khi backend có địa chỉ công khai;
chạy local thì dựa vào return URL.

**Đối soát đơn "đang chờ"** (học viên trả tiền xong nhưng đóng tab trước khi quay về web):
- Admin → **Quản lý Giao dịch** → tab *Đang chờ* → bấm đơn → **Kiểm tra với VNPay**, hoặc nút
  **Đối soát N đơn đang chờ**. Hệ thống hỏi VNPay (API `querydr`): đã trả tiền → hoàn tất + ghi danh;
  quá hạn mà chưa trả → thất bại.
- Backend tự đối soát đơn quá hạn mỗi `PAYMENT_RECONCILE_INTERVAL` giây (mặc định 300, `0` = tắt).
- Học viên mua lại một khóa còn đơn đang chờ: hệ thống hỏi VNPay về đơn cũ trước khi tạo đơn mới.

**Hoàn tiền** (Admin → Quản lý Giao dịch → bấm đơn *Thành công* → **Hoàn tiền**):
- Hoàn toàn phần qua API `refund` của VNPay (đơn giả lập cũ chỉ ghi nhận thủ công); bắt buộc nhập lý do.
- Tuỳ chọn **Thu hồi quyền học** (mặc định bật): xoá ghi danh, **giữ** điểm quiz và tiến độ (hiện lại nếu mua lại).
- VNPay từ chối thì đơn giữ nguyên. Đơn đã hoàn không tính vào doanh thu.

---

## Tài liệu

| File | Nội dung |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Kiến trúc tổng thể, luồng xác thực, quyết định thiết kế |
| [docs/rag.md](docs/rag.md) | RAG AI Tutor: ingest, retrieval, đánh giá |
| [docs/fine-tuning.md](docs/fine-tuning.md) | Dataset, LoRA/QLoRA, đánh giá Base vs Fine-tuned |
| [docs/recommendation.md](docs/recommendation.md) | Learning Analytics + Rule Engine + vòng lặp cá nhân hoá |
| [docs/api.md](docs/api.md) | Tham chiếu toàn bộ endpoint + schema CSDL |
| [backend/README.md](backend/README.md) | Chi tiết backend |
| [backend/training/README.md](backend/training/README.md) | Hướng dẫn fine-tune trên Colab |
