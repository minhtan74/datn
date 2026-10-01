# Hướng Dẫn Chạy Dự Án StudyOnline 🚀

Hệ thống gồm 2 phần:
1. **Backend** — REST API viết bằng **Python / FastAPI** (đã thay cho bản PHP cũ).
2. **Frontend** — SPA **React + Vite**.

Có 2 cách chạy: **Docker** (nhanh) hoặc **thủ công** (dev).

---

## 🐳 Cách 1 — Docker Compose (khuyên dùng để demo)

Yêu cầu: Docker Desktop.

```bash
docker compose up -d --build
```

- Giao diện: **http://localhost:8088**
- API + Swagger: **http://localhost:8080/docs**

MySQL tự nạp cấu trúc bảng + dữ liệu mẫu; backend tự chạy `alembic upgrade head`.

Nạp thêm dữ liệu AI mẫu (tuỳ chọn):

```bash
docker compose exec backend python training/seed_documents.py
docker compose exec backend python training/seed_result_answers.py
docker compose exec backend python training/seed_learning_data.py
docker compose exec backend python training/fix_report_data.py
docker compose exec backend python training/lesson_docs/seed_lesson_docs.py
```

Dừng: `docker compose down` (thêm `-v` để xoá luôn dữ liệu).

---

## 🔧 Cách 2 — Chạy thủ công (dev)

### Bước 1: Cơ sở dữ liệu (MySQL)

Tạo database `studyonline_db` (mã hoá `utf8mb4_unicode_ci`), import lần lượt:

1. `database/studyonline_db.sql`
2. `database/migration_add_payments.sql`
3. `database/sample_data.sql`

### Bước 2: Backend (FastAPI)

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -r requirements.txt
# Linux/macOS:
# source .venv/bin/activate && pip install -r requirements.txt

copy .env.example .env          # (Windows)  — rồi sửa DB_HOST/DB_PORT/DB_USER/DB_PASS
python -m alembic upgrade head  # tạo các bảng AI (0002–0006)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

API chạy tại **http://localhost:8080**.

> Lưu ý: `backend/.env` mặc định `DB_PORT=3306`. Sửa lại nếu MySQL của bạn dùng cổng khác.

### Bước 3: Frontend (React + Vite)

```bash
cd frontend
npm install
# tạo file .env:
echo VITE_API_BASE_URL=http://127.0.0.1:8080 > .env
npm run dev
```

Vite chạy tại **http://localhost:5173**.

### Bước 4 (tuỳ chọn): dữ liệu AI mẫu

```bash
cd backend
.venv\Scripts\python training\seed_documents.py        # 3 tài liệu cho AI Tutor (khóa 1 & 2)
.venv\Scripts\python training\seed_result_answers.py   # để trang "Phân tích học tập" có dữ liệu
.venv\Scripts\python training\seed_learning_data.py     # thêm câu hỏi/chủ đề, nhiều lượt làm quiz & tiến độ bài học
.venv\Scripts\python training\fix_report_data.py        # sửa ngày tháng cho trang Báo cáo (chạy SAU seed_learning_data)
.venv\Scripts\python training\lesson_docs\seed_lesson_docs.py   # gắn PDF tài liệu cho các bài học (bài nào đã có PDF thật thì giữ nguyên)
```

> PDF của 52 bài nằm sẵn trong `backend/training/lesson_docs/pdf/`. Muốn sửa nội dung: chỉnh file `.md` trong `training/lesson_docs/content/` rồi chạy `python training\lesson_docs\build_pdfs.py` (cần Chrome/Edge) để dựng lại.

---

## 🔑 Tài khoản Thử nghiệm (mật khẩu chung: `123456`)

| Vai trò | Email | Quyền chính |
|---|---|---|
| **Giảng viên** | `an.nguyen@studyonline.vn` / `binh.tran@studyonline.vn` | Quản lý khóa học, bài học, chương, quiz; tải tài liệu AI Tutor; dùng AI Quiz Generator |
| **Học viên** | `em.hoang@gmail.com` / `phuong.vu@gmail.com` | Học bài, làm quiz, xem tiến độ & phân tích học tập, nhận gợi ý, hỏi AI Tutor |
| **Admin** | `admin@gmail.com` | (giữ nguyên từ bản gốc, ngoài phạm vi chính của đồ án) |

---

## 🧪 Kiểm thử backend

```bash
cd backend
.venv\Scripts\python -m pytest              # 17 test API (tự dọn dữ liệu)
.venv\Scripts\python tests\smoke_writes.py  # luồng ghi CRUD + học tập
```

---

## 💳 Thanh toán VNPay Sandbox

Khóa học có phí được thanh toán qua **VNPay Sandbox** (môi trường thử, không trừ tiền thật).

1. Đăng ký tài khoản test tại https://sandbox.vnpayment.vn/devreg/ — VNPay gửi email
   gồm **vnp_TmnCode** và **vnp_HashSecret**.
2. Điền vào `backend/.env` rồi **khởi động lại backend**:
   ```ini
   VNPAY_TMN_CODE=<mã website>
   VNPAY_HASH_SECRET=<chuỗi bí mật>
   ```
   (Docker: đặt 2 biến này trong môi trường hoặc file `.env` cạnh `docker-compose.yml`.)
3. Mở web bằng đúng địa chỉ trong `FRONTEND_URL` (mặc định **http://localhost:5173**) —
   VNPay trả về địa chỉ này, mở bằng `127.0.0.1` sẽ bị mất phiên đăng nhập.
4. Học viên → Khám phá khóa học → Đăng ký khóa có phí → **Thanh toán qua VNPay**.
   Thẻ test (ngân hàng **NCB**):

   | Số thẻ | Tên chủ thẻ | Ngày phát hành | OTP |
   |---|---|---|---|
   | `9704198526191432198` | `NGUYEN VAN A` | `07/15` | `123456` |

Luồng xử lý: tạo đơn `pending` → chuyển sang VNPay → VNPay đưa trình duyệt về
`/api/payments/vnpay/return` → backend **kiểm tra chữ ký HMAC-SHA512 + số tiền** →
thành công: đơn `completed` (đã thanh toán) + ghi danh; thất bại/hủy: đơn `failed`, không ghi danh
→ chuyển về trang `/student/payment-result`.

`/api/payments/vnpay/ipn` là URL IPN (VNPay gọi thẳng server) — chỉ dùng được khi backend có
địa chỉ công khai (khai báo trên trang merchant VNPay); chạy local thì dựa vào return URL.

**Đối soát đơn "đang chờ"** (học viên trả tiền xong nhưng đóng tab trước khi quay về web):
- Admin → **Quản lý Giao dịch** → tab *Đang chờ* → bấm đơn → **Kiểm tra với VNPay**, hoặc nút
  **Đối soát N đơn đang chờ**. Hệ thống hỏi VNPay (API `querydr`): đã trả tiền → hoàn tất + ghi danh;
  quá hạn mà chưa trả → thất bại.
- Backend tự đối soát các đơn quá hạn mỗi `PAYMENT_RECONCILE_INTERVAL` giây (mặc định 300, `0` = tắt).
- Khi học viên mua lại một khóa còn đơn đang chờ, hệ thống hỏi VNPay về đơn cũ trước khi tạo đơn mới.

**Hoàn tiền** (admin → Quản lý Giao dịch → bấm đơn *Thành công* → **↩️ Hoàn tiền**):
- Hoàn toàn phần qua API `refund` của VNPay (đơn giả lập cũ: chỉ ghi nhận thủ công); bắt buộc nhập lý do.
- Tùy chọn **Thu hồi quyền học** (mặc định bật): xóa ghi danh, **giữ** điểm quiz & tiến độ (hiện lại nếu mua lại).
- VNPay từ chối thì đơn giữ nguyên. Đơn đã hoàn không tính vào doanh thu.

---

## 🤖 Cấu hình AI (tuỳ chọn)

Mặc định AI chạy **offline** (RAG dùng trích xuất, Quiz dùng heuristic) — demo được ngay
mà không cần khoá API. Để dùng LLM thật, sửa `backend/.env`:

```ini
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
LLM_API_KEY=<khoá của bạn>
```

Các lựa chọn khác:

| Nhà cung cấp | Cấu hình |
|---|---|
| OpenAI | `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini`, `LLM_API_KEY=sk-...` |
| Claude | `LLM_PROVIDER=claude`, `LLM_MODEL=claude-haiku-4-5-20251001`, `LLM_API_KEY=sk-ant-...` |
| Ollama (chạy trên máy, offline, không cần khoá) | `LLM_PROVIDER=openai`, `LLM_MODEL=qwen2.5:7b`, `LLM_BASE_URL=http://localhost:11434/v1` |
| Groq / DeepSeek / OpenRouter | `LLM_PROVIDER=openai` + `LLM_BASE_URL` của dịch vụ + khoá (xem `backend/.env.example`) |

Dùng Ollama: cài từ ollama.com, chạy `ollama pull qwen2.5:7b` một lần, giữ Ollama chạy nền rồi
khởi động lại backend. Máy dưới 16GB RAM nên dùng `qwen2.5:3b`.

Fine-tune AI Quiz Generator (LoRA/QLoRA) chạy trên Google Colab — xem
`backend/training/README.md`.

---
*Chúc bạn chạy dự án thành công!*
