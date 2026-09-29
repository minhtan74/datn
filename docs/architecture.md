# Kiến trúc hệ thống StudyOnline

> Nền tảng học tập trực tuyến hỗ trợ **cá nhân hoá học tập ứng dụng AI**.
> Backend **FastAPI (Python)** · Frontend **React (Vite)** · CSDL **MySQL**.

---

## 1. Sơ đồ tổng thể

```
                                   NGƯỜI DÙNG (Giảng viên / Học viên)
                                              │  HTTPS
                                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  FRONTEND — React 18 + Vite + React Router + Axios                         │
│  (SPA, JWT lưu localStorage, axiosClient tự gắn Bearer, xử lý 401)         │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │  REST/JSON  (Authorization: Bearer <JWT>)
                                ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  BACKEND — FastAPI + SQLAlchemy + Pydantic                                 │
│                                                                           │
│   Routers ──► Dependencies (get_current_user / require_roles)              │
│      │                                                                     │
│      ├── LMS API     : auth, users, courses, chapters, lessons,            │
│      │                 quizzes(+questions+submit), enrollments,            │
│      │                 payments (mock), progress, uploads, reports         │
│      │                                                                     │
│      ├── Analytics   : /api/analytics/*      (Learning Analytics)          │
│      ├── Recommend   : /api/recommendations/*(Rule-based Engine)           │
│      └── AI          : /api/ai/*                                           │
│             ├── RAG AI Tutor      (chat + tài liệu + trích dẫn nguồn)      │
│             └── AI Quiz Generator (sinh quiz → giảng viên duyệt)           │
│                                                                           │
│   app/ai/                                                                  │
│     ├── rag/       document_loader · text_splitter · embeddings ·          │
│     │              vector_store (MySQL) · retriever · rag_pipeline         │
│     ├── model_manager.py  (Gemini / OpenAI / extractive-offline)           │
│     ├── recommendation.py (rule engine)                                    │
│     └── quiz_generator.py (LLM JSON / heuristic-offline)                   │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │  SQLAlchemy (PyMySQL)                        │  fastembed (ONNX)
                                ▼                                             ▼
┌─────────────────────────────────────────────┐        ┌──────────────────────────────┐
│  MySQL  studyonline_db                       │        │  Embedding model (offline)    │
│   LMS: users, courses, chapters, lessons,    │        │  paraphrase-multilingual-    │
│        enrollments, lesson_progress,         │        │  MiniLM-L12-v2 (384d)         │
│        quizzes, questions, results, payments │        └──────────────────────────────┘
│   AI : result_answers, learning_analytics,  │        ┌──────────────────────────────┐
│        recommendations, documents,          │        │  LLM API (tuỳ chọn)          │
│        document_chunks, ai_conversations,   │───────►│  Gemini / OpenAI qua HTTPS   │
│        ai_messages                          │        │  (không có key → offline)     │
└─────────────────────────────────────────────┘        └──────────────────────────────┘
```

**Vector store nằm ngay trong MySQL** (`document_chunks.embedding` kiểu JSON) — không
cần vector DB ngoài; truy hồi bằng cosine similarity (numpy) trên tập chunk của khóa học.

---

## 2. Thành phần

### 2.1 Frontend (`frontend/`)
| Lớp | Vai trò |
|---|---|
| `api/axiosClient.js` | Cấu hình Axios: `baseURL` từ `.env`, request interceptor gắn `Authorization: Bearer`, response interceptor chuẩn hoá `{ ok, status, data }`, tự đăng xuất khi 401 |
| `services/*.js` | Mỗi tài nguyên một service (courseService, quizService, analyticsService, recommendationService, aiService…) |
| `context/` | `AuthContext` (token + user trong localStorage), `ToastContext` |
| `routes/` | `AppRoutes`, `ProtectedRoute` (chặn theo vai trò), `PublicOnlyRoute` |
| `layouts/` | Public / App / Student / Teacher / Admin |
| `pages/` | Public + `student/*` + `teacher/*` (+ `admin/*` giữ nguyên, không phát triển thêm) |

### 2.2 Backend (`backend/`)
| Lớp | Vai trò |
|---|---|
| `app/main.py` | Khởi tạo FastAPI, CORS, exception handler → phong bì lỗi `{success:false,message}`, mount `/uploads`, gắn router |
| `app/core/config.py` | Đọc `.env` bằng `pydantic-settings` |
| `app/core/database.py` | Engine SQLAlchemy + `SessionLocal` + helper SQL thô `q_all/q_one/execute` (bám sát truy vấn bản PHP để đảm bảo tương thích contract) |
| `app/core/security.py` | JWT HS256 (giữ secret + payload `{id,fullname,email,role}` như bản PHP), bcrypt + chấp nhận plaintext cho dữ liệu seed |
| `app/core/dependencies.py` | `get_current_user`, `require_roles(...)` |
| `app/core/responses.py` | `ok()`, `ApiError`, `ApiJSONResponse` (Decimal → `"599000.00"`, datetime → `"Y-m-d H:i:s"`) |
| `app/models/` | SQLAlchemy models (cho Alembic + code AI) |
| `app/routers/` | 14 router |
| `app/services/` | `analytics_service` |
| `app/ai/` | RAG, model_manager, recommendation, quiz_generator |
| `alembic/` | 6 migration (0001 baseline stamp → 0006) |

### 2.3 CSDL
- 10 bảng LMS (giữ nguyên từ bản gốc) + 6 bảng AI (thêm mới, hoàn toàn additive).
- Chi tiết: [api.md](api.md) và `database/*.sql`.

---

## 3. Luồng xác thực

1. `POST /api/auth/login` → server kiểm tra mật khẩu (bcrypt hoặc plaintext seed) →
   phát **JWT HS256** payload `{id, fullname, email, role, iat, exp}` (hết hạn 7 ngày).
2. Frontend lưu `token` + `user` vào `localStorage`.
3. Mọi request kèm header `Authorization: Bearer <token>`.
4. Backend: `get_current_user` giải mã & kiểm hạn; `require_roles("teacher","admin")`
   chặn 403 nếu sai vai trò.
5. Token sai/hết hạn → 401 → frontend xoá phiên, chuyển `/login`.

---

## 4. Ba trục AI (đúng phạm vi đề tài)

| # | Chức năng | Kỹ thuật | Chạy offline? |
|---|---|---|---|
| 1 | **RAG AI Tutor** | Retrieval-Augmented Generation: embed → vector search (MySQL) → prompt có ràng buộc → LLM | Có — chế độ *extractive* (trích câu từ ngữ cảnh) |
| 2 | **AI Quiz Generator** | LLM (fine-tuned LoRA / Gemini) sinh JSON quiz theo schema → giảng viên duyệt → lưu | Có — heuristic *điền chỗ trống* |
| 3 | **Personalized Recommendation** | Rule-based engine (không ML) trên số liệu học tập thật | Có — luôn offline |

Vòng lặp cá nhân hoá: **Học bài → Làm Quiz → Lưu kết quả → Learning Analytics →
Xác định chủ đề yếu → Gợi ý → Học lại → Quiz lần 2 → So sánh kết quả**
(xem [recommendation.md](recommendation.md)).

---

## 5. Quyết định thiết kế đáng chú ý

| Vấn đề | Lựa chọn | Lý do |
|---|---|---|
| Giữ frontend cũ | Không viết lại; chỉ đổi `VITE_API_BASE_URL` + 1 dòng `axiosClient` | FastAPI giữ **nguyên contract HTTP** của bản PHP (path, query, phong bì JSON, thông điệp lỗi) — kiểm chứng bằng 37 test so-byte |
| Vector DB | MySQL (cột JSON) + cosine numpy | Không thêm dịch vụ ngoài; dễ triển khai & giải thích; `chroma-hnswlib` không build được trên Python 3.13/Windows |
| Embedding | `fastembed` (ONNX) | Không cần PyTorch; model đa ngữ có tiếng Việt |
| LLM | REST (Gemini/OpenAI) qua `httpx`, đổi bằng `.env`; fallback offline | Không khoá cứng nhà cung cấp; demo được khi không có mạng/khoá |
| Fine-tuning | LoRA/QLoRA trên Colab, chỉ đem adapter về | Backend production không cần GPU |
| Admin | Giữ code, không phát triển thêm | Đề tài chỉ 2 vai trò; không xoá để tránh vỡ build |
