# StudyOnline — Nền tảng học tập trực tuyến hỗ trợ cá nhân hoá học tập ứng dụng AI

Đồ án tốt nghiệp. Hệ thống LMS có 3 vai trò (**Admin**, **Giảng viên**, **Học viên**) với ba chức năng hỗ trợ học tập:

1. **RAG AI Tutor** — hỏi đáp dựa trên tài liệu khóa học, có trích dẫn nguồn.
2. **AI Quiz Generator** — sinh câu hỏi trắc nghiệm từ tài liệu → giảng viên duyệt → lưu.
3. **Personalized Recommendation** — phân tích đúng/sai theo chương, bài và chủ đề ở bài kiểm tra cuối khóa, kiểm tra chương và luyện bài; dẫn đến nội dung cần ôn, cập nhật theo kết quả mới và so sánh trước/sau. Xem [quy tắc gợi ý](docs/recommendation.md).

| Lớp | Công nghệ |
|---|---|
| Frontend | React 18 · Vite · React Router · Axios · Chart.js |
| Backend | **FastAPI** · SQLAlchemy · Pydantic · Alembic · JWT (HS256) · bcrypt |
| CSDL | MySQL 8 |
| AI | fastembed (embedding ONNX, không cần PyTorch) · vector store trên MySQL · Gemini/OpenAI qua REST, Claude qua SDK · công cụ nghiên cứu LoRA/QLoRA trên Colab |

> Backend hiện tại dùng FastAPI, thay cho backend PHP trước đây;
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
│   ├── alembic/          migration CSDL (0001 baseline → 0021)
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

Khi volume MySQL còn trống, Docker chạy các file SQL để tạo bảng và nạp dữ liệu mẫu.
Backend chạy `alembic upgrade head` khi khởi động để cập nhật schema. Volume đã có dữ liệu
thì các file SQL khởi tạo không chạy lại.

Nạp thêm dữ liệu demo (tuỳ chọn, chạy theo đúng thứ tự):

```bash
docker compose exec backend python training/seed_documents.py              # tài liệu mẫu cho AI Tutor
docker compose exec backend python training/seed_result_answers.py         # chi tiết câu trả lời cho kết quả quiz cũ
docker compose exec backend python training/seed_learning_data.py          # thêm lượt làm quiz + tiến độ học
docker compose exec backend python training/fix_report_data.py             # chỉnh ngày tháng cho trang Báo cáo
docker compose exec backend python training/lesson_docs/seed_lesson_docs.py  # gắn PDF tài liệu cho bài học
```

Dùng LLM (Gemini): điền `LLM_API_KEY` trong nhóm `backend.environment` của `docker-compose.yml`
rồi chạy lại `docker compose up -d`. Biến này hiện được khai báo trực tiếp trong Compose,
nên chỉ điền vào `backend/.env` hoặc `.env` ở thư mục gốc sẽ không thay thế giá trị đó.
Để trống thì AI dùng chế độ trích xuất từ tài liệu. Model embedding cần được tải ở lần dùng đầu tiên.

Dừng: `docker compose down` (thêm `-v` để xoá luôn dữ liệu).

---

### Cách 2 — Windows local

#### Lần đầu tiên (cài đặt)

**1. CSDL.** Bật MySQL 8.4 trước khi import. Các lệnh dưới đây chạy từ thư mục gốc dự án,
với `mysql` đã có trong `PATH`.

**Chỉ dùng cho lần khởi tạo dữ liệu demo:** `studyonline_db.sql` có lệnh
`DROP DATABASE IF EXISTS studyonline_db`, sẽ xóa database cùng tên rồi tạo lại.
Không chạy file này trên database cần giữ dữ liệu; `sample_data.sql` cũng không nên nạp lại nhiều lần.

Mở MySQL CLI từ PowerShell rồi import theo thứ tự (PowerShell không hỗ trợ cú pháp `< file.sql`):

```powershell
mysql -u root -p
```

Tại dấu nhắc `mysql>`, chạy:

```sql
SOURCE database/studyonline_db.sql;
SOURCE database/migration_add_payments.sql;
SOURCE database/sample_data.sql;
EXIT;
```

**2. Backend.**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env           # rồi sửa DB_PASS, LLM_API_KEY (Gemini), VNPAY_* nếu có
.venv\Scripts\python -m alembic upgrade head
```

Migration `0001` chỉ đánh dấu baseline, không tạo bảng ban đầu; cần import schema SQL
trước khi chạy Alembic. Nếu database đã được khởi tạo, chỉ cấu hình kết nối và chạy migration.

Các biến quan trọng trong `backend/.env`:

| Biến | Ý nghĩa |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS` | Kết nối MySQL (mặc định `127.0.0.1:3306`, user `root`) |
| `LLM_PROVIDER`, `LLM_API_KEY` | `gemini` + khoá Gemini; để trống khoá -> AI chạy offline |
| `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET` | Khoá VNPay Sandbox; để trống -> nút thanh toán báo "chưa cấu hình" |

**3. Frontend.**

```powershell
cd frontend
npm install
Set-Content -Path .env -Value 'VITE_API_BASE_URL=http://127.0.0.1:8080' -Encoding utf8
```

**4. Dữ liệu demo (tuỳ chọn).** Chạy trong thư mục `backend`, sau khi migration hoàn tất.
Các script này ghi dữ liệu; riêng `fix_report_data.py` còn chỉnh ngày tháng và xóa một số dữ liệu
để báo cáo demo nhất quán. Chỉ chạy trên database demo hoặc bản sao dữ liệu.

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

Script mở cửa sổ PowerShell riêng cho Backend (`:8080`) và Frontend (`:5173`).
**Chỉ MySQL được kiểm tra cổng trước khi chạy:** nếu cổng 3306 đã có chương trình lắng nghe,
script bỏ qua bước bật MySQL. Backend và frontend luôn được khởi động, nên tránh chạy script
nhiều lần khi chúng đang hoạt động; Vite có thể chọn cổng khác nếu 5173 đang bận.

Nếu cổng 3306 còn trống, script thử bật MySQL riêng từ `backend/data/mysql-data`.
Thư mục dữ liệu này phải được khởi tạo sẵn; script không tự tạo database hay import dữ liệu.
Đường dẫn MySQL trong script được cố định là `C:\Program Files\MySQL\MySQL Server 8.4`.
Với máy mới, nên bật MySQL service theo Bước 1; nếu cài ở vị trí khác, cần sửa đường dẫn trong script.

**Bước 3 — mở <http://localhost:5173>** và đăng nhập bằng tài khoản mẫu bên dưới.

**Tắt:** dùng `Ctrl+C` trong cửa sổ backend/frontend. Dừng MySQL service bằng
`net stop MySQL84` trong PowerShell Administrator. Nếu cần dừng các tiến trình theo cổng:

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

## Tài khoản mẫu (sau khi import SQL, mật khẩu chung `123456`)

| Vai trò | Email | Quyền chính |
|---|---|---|
| Admin | `admin@gmail.com` | Quản lý người dùng, khóa học, giao dịch (đối soát, hoàn tiền), báo cáo |
| Giảng viên | `an.nguyen@studyonline.vn`, `binh.tran@studyonline.vn` | Quản lý khóa / chương / bài / quiz; tải tài liệu cho AI Tutor; sinh đề bằng AI; nhập đề từ Word |
| Học viên | `em.hoang@gmail.com`, `phuong.vu@gmail.com` | Học bài, làm quiz, xem tiến độ & phân tích, nhận gợi ý, hỏi AI Tutor |

---

## Tài liệu khóa học

Đã bổ sung phần thực hành, lỗi thường gặp, hỏi đáp và hướng giải cho **101 bài thuộc 10 khóa nội dung**.
Mỗi bài trên web dùng PDF gốc kèm phụ lục mới; AI Tutor tra cứu được tài liệu bổ sung theo đúng khóa/bài.
Xem [mục lục PDF toàn khóa và kết quả kiểm tra](docs/hoan-thien-tai-lieu-2026-10-29.md)
và [nguồn Markdown, quy trình dựng/hoàn tác](backend/training/lesson_docs/edition_20261029/README.md).

## Kiểm thử

Học viên mở quiz sẽ được cấp một lượt làm. Mỗi lượt mới đảo thứ tự câu hỏi và phương án;
tải lại trang hoặc mở lại lượt chưa nộp giữ nguyên thứ tự và đáp án đã chọn trong cùng phiên trình duyệt.
Nội dung câu hỏi vẫn là bộ đề đã lưu, không sinh thêm bằng AI. Lịch sử hiển thị theo thứ tự của lượt đó.
Các lượt cũ trước migration `0018` giữ thứ tự ban đầu; giảng viên/admin xem và làm thử giữ thứ tự biên soạn.
Phép đảo ngẫu nhiên có thể tình cờ tạo thứ tự giống nhau, nhất là đề có ít câu.

Chạy trong thư mục `backend`. Test API cần MySQL đã có schema, migration và tài khoản mẫu.
Các test có ghi dữ liệu và có phần dọn dữ liệu; nên dùng MySQL demo riêng, cấu hình `DB_HOST` /
`DB_PORT` / `DB_NAME` tương ứng trước khi chạy. Các file SQL khởi tạo hiện cố định tên
`studyonline_db`, nên dùng instance MySQL riêng là cách tránh ảnh hưởng database đang sử dụng.

```powershell
.venv\Scripts\python -m pytest                              # test API + test nhập đề Word
.venv\Scripts\python tests/smoke_writes.py                  # luồng ghi CRUD + học tập
.venv\Scripts\python training/rag_eval/evaluate_rag.py      # đánh giá AI Tutor bằng bộ câu hỏi RAG
```

Kết quả đánh giá AI Tutor được lưu ở `backend/training/rag_eval/results/`.

---

## Cấu hình AI (tuỳ chọn)

Với Gemini/OpenAI/Claude, không có khóa API thì AI dùng chế độ **trích xuất**:
AI Tutor ghép câu từ tài liệu, sinh quiz dùng luật tạo câu điền chỗ trống ở mức dễ.
Offline không sinh câu trung bình/khó; yêu cầu chỉ gồm hai mức này sẽ bị từ chối,
yêu cầu hỗn hợp có câu dễ sẽ trả phần câu dễ sinh được và báo thiếu các mức còn lại.
Nếu tài liệu không đủ ba phương án nhiễu, câu điền chỗ trống đó bị bỏ qua.

Khi dùng LLM, mức dễ yêu cầu nhớ một kiến thức; trung bình yêu cầu hiểu hoặc áp dụng
một quy tắc; khó yêu cầu kết hợp nhiều kiến thức/điều kiện và suy luận nhiều bước.
AI giải lại cũng thẩm định mức tư duy; bản nháp hiển thị cảnh báo nếu khác mức yêu cầu.
Đây là mức dự kiến, giảng viên cần kiểm tra trước khi duyệt, chưa phải độ khó đo từ kết quả học viên.
Giao diện hiển thị bản nháp ngay khi nhận được từng nhóm câu, sau đó cập nhật kết quả AI tự kiểm tra.
Đề nhiều mức có tối đa 12 câu được gom vào một lượt sinh; đề lớn hơn chạy tối đa hai nhóm song song.
Nút duyệt chờ quá trình xử lý kết thúc; khi AI không kiểm tra được đáp án, bản nháp có cảnh báo để giảng viên xem lại.
Riêng `LLM_PROVIDER=openai` kèm `LLM_BASE_URL` vẫn bật gọi API dù không có khóa, để hỗ trợ
dịch vụ nội bộ như Ollama.

Để demo không có mạng, cần tải model embedding và nạp tài liệu vào RAG trước.
Lần dùng embedding đầu tiên có thể cần mạng để tải model; thiếu khóa LLM không có nghĩa là
hệ thống đã sẵn sàng chạy hoàn toàn offline. Để dùng LLM, sửa `backend/.env`:

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

Dùng Ollama: cài Ollama, tải model bằng `ollama pull qwen2.5:7b`, giữ Ollama chạy nền rồi khởi động
lại backend. Chọn model phù hợp với tài nguyên máy. Các tên model trong bảng là ví dụ cấu hình;
khả năng truy cập phụ thuộc nhà cung cấp và tài khoản API.

Sửa `.env` xong phải tắt hẳn cửa sổ Backend rồi bật lại. Fine-tune AI Quiz Generator (LoRA/QLoRA) chạy trên
Google Colab — xem `backend/training/README.md`.

Các script LoRA/QLoRA phục vụ huấn luyện và đánh giá riêng. Luồng gọi LLM hiện tại trong
`backend/app/ai/model_manager.py` chưa nạp adapter LoRA; chỉ đặt `LORA_ADAPTER_PATH`
không làm API sinh quiz chuyển sang model đã fine-tune.

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

Khóa có phí chỉ thanh toán qua VNPay; cần kết nối mạng để mở cổng thanh toán.

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

Ngày 13/10/2026: đã kiểm tra 290 PDF và tạo bộ 65 tài liệu theo cấu trúc bài giảng
Nguyên Lí HDH (183 trang), cập nhật 54 bài các môn còn lại trong database local và
lập lại chỉ mục RAG. Xem [báo cáo tạo lại PDF](docs/pdf-rebuild-20261013.md) và
[bộ PDF đóng gói](backend/training/lesson_docs/rebuilt/tai_lieu_theo_mau_hdh.zip).

Kiểm tra tài liệu học tập database local ngày 12/10/2026: đã bổ sung PDF cho 18 bài
Python/JavaScript thiếu file và thêm 7 sổ tay thực hành mở rộng. Phần học thêm nằm sau
tài liệu chính của bài cuối mỗi khóa. Xem [báo cáo kiểm tra](docs/materials-audit.md)
và [mục lục học thêm](backend/training/lesson_docs/supplements/README.md).

| File | Nội dung |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Kiến trúc tổng thể, luồng xác thực, quyết định thiết kế |
| [docs/rag.md](docs/rag.md) | RAG AI Tutor: ingest, retrieval, đánh giá |
| [docs/fine-tuning.md](docs/fine-tuning.md) | Dataset, LoRA/QLoRA, đánh giá Base vs Fine-tuned |
| [docs/recommendation.md](docs/recommendation.md) | Learning Analytics + Rule Engine + vòng lặp cá nhân hoá |
| [docs/api.md](docs/api.md) | Tham chiếu toàn bộ endpoint + schema CSDL |
| [backend/README.md](backend/README.md) | Chi tiết backend |
| [backend/training/README.md](backend/training/README.md) | Hướng dẫn fine-tune trên Colab |
