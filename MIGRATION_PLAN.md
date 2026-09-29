# MIGRATION_PLAN.md — StudyOnline

**Đồ án tốt nghiệp:** StudyOnline – Nền tảng học tập trực tuyến hỗ trợ cá nhân hóa học tập ứng dụng AI
**Tài liệu này = kết quả PHASE 1 (Phân tích).** Chưa viết code chức năng mới. Chỉ phân tích hiện trạng + lập kế hoạch migration PHP → FastAPI + kiến trúc AI.

> Ngày phân tích: 2026-09-06
> Người phân tích: Senior Full-Stack + AI Engineer (theo yêu cầu đề bài)

---

## MỤC LỤC

1. [Current Architecture](#1-current-architecture)
2. [Current Frontend](#2-current-frontend)
3. [Current Backend](#3-current-backend)
4. [Current Database](#4-current-database)
5. [Existing APIs](#5-existing-apis)
6. [PHP → FastAPI Migration Map](#6-php--fastapi-migration-map)
7. [AI Architecture](#7-ai-architecture)
8. [RAG Architecture](#8-rag-architecture)
9. [Fine-tuning Architecture](#9-fine-tuning-architecture)
10. [Recommendation Architecture](#10-recommendation-architecture)
11. [Files to Create](#11-files-to-create)
12. [Files to Modify](#12-files-to-modify)
13. [Files to Delete / Archive](#13-files-to-delete--archive)
14. [Risks](#14-risks)
15. [Development Plan](#15-development-plan)

---

## 1. CURRENT ARCHITECTURE

### 1.1 Tổng quan

Dự án hiện tại có **3 lớp mã nguồn chồng nhau** (2 lớp đã ngừng phát triển):

| Lớp | Vị trí | Trạng thái | Vai trò |
|---|---|---|---|
| **REST API PHP thuần** | `backend/` | ✅ Đang dùng | Backend chính hiện tại |
| **SPA React + Vite** | `frontend/` | ✅ Đang dùng | Frontend chính hiện tại |
| Classic MVC monolithic PHP | `app/`, `core/`, `public/` | ⚠️ Legacy | Bản cũ, giữ tham khảo |
| Frontend HTML/CSS/JS thuần | `legacy-frontend-vanilla-backup/` | ⚠️ Legacy | Bản trước khi lên React |

Kiến trúc **decoupled**: `frontend/` gọi `backend/` hoàn toàn qua HTTP + JSON, không chia sẻ mã nguồn.

### 1.2 Sơ đồ hiện trạng

```
┌────────────────────┐         HTTP/JSON          ┌─────────────────────────┐
│  frontend/ (React) │ ─────────────────────────► │  backend/ (PHP REST)     │
│  Vite dev :5173    │  Authorization: Bearer JWT │  php -S :8000 -t public  │
│  axios + localStrg │ ◄───────────────────────── │  (hoặc Apache/XAMPP)     │
└────────────────────┘   { success, data|token }  └───────────┬─────────────┘
                                                              │ PDO (mysql)
                                                              ▼
                                                  ┌─────────────────────────┐
                                                  │  MySQL  studyonline_db  │
                                                  │  10 bảng                │
                                                  └─────────────────────────┘
```

### 1.3 Kích thước mã nguồn

| Thành phần | Số dòng | Số file |
|---|---|---|
| Backend PHP (`backend/**/*.php`) | ~2.560 | 34 |
| Frontend React (`frontend/src/**/*.{jsx,js}`) | ~8.560 | 70 |
| SQL (`database/*.sql`) | ~1.000 | 3 |

### 1.4 Môi trường đã kiểm chứng trên máy dev (2026-09-06)

- PHP **8.3.30** CLI ✅
- Node **v24.14.0**, npm **11.9.0** ✅
- MySQL **8.4.8** (service `MySQL84`, khởi động thủ công, cổng **3306**) ✅
- Đã chạy được: import 3 file SQL → backend `php -S 127.0.0.1:8001` → frontend `npm run dev` :5173 → login `admin@gmail.com/123456` trả JWT hợp lệ.
- **Lưu ý cổng:** README ghi backend cổng 8000 + MySQL 3307. Thực tế máy này: MySQL **3306**, và cổng **8000 đã bị một app Python khác chiếm** → đã tạm chạy backend PHP ở **8001** và sửa `frontend/.env` tương ứng.

---

## 2. CURRENT FRONTEND

### 2.1 Stack

| Thư viện | Phiên bản | Ghi chú |
|---|---|---|
| React | 18.3.1 | |
| Vite | 6.0.5 | plugin `@vitejs/plugin-react` |
| React Router DOM | 6.28.0 | `BrowserRouter` |
| axios | 1.7.9 | 1 client dùng chung |
| Tailwind CSS | 4.3.2 | `@tailwindcss/vite` (chỉ 4 trang công khai) |
| chart.js + react-chartjs-2 | 4.4.7 / 5.2.0 | biểu đồ dashboard |

Chưa có: `lucide-react`, `recharts` (đề bài yêu cầu bổ sung `lucide-react`; giữ `chart.js`, không cần `recharts`).

### 2.2 Cây thư mục `frontend/src/`

```
src/
├── main.jsx                 # createRoot + BrowserRouter + AuthProvider + ToastProvider
├── App.jsx                  # chỉ render <AppRoutes/>
├── index.css
├── api/
│   └── axiosClient.js       # ⭐ instance axios, gắn JWT, chuẩn hoá response, xử lý 401
├── services/                # 11 file — mỗi resource 1 service
│   ├── authService.js       ├── chapterService.js  ├── courseService.js
│   ├── enrollmentService.js ├── lessonService.js   ├── paymentService.js
│   ├── progressService.js   ├── quizService.js     ├── reportService.js
│   ├── uploadService.js     └── userService.js
├── context/
│   ├── AuthContext.jsx      # token + user lưu localStorage; login()/logout()
│   └── ToastContext.jsx
├── hooks/                   # useAuth, useToast, useClickOutside
├── routes/
│   ├── AppRoutes.jsx        # toàn bộ <Routes>
│   ├── ProtectedRoute.jsx   # chặn theo roles=[...]
│   └── PublicOnlyRoute.jsx
├── layouts/                 # PublicLayout, AppLayout, StudentLayout, AdminLayout, TeacherLayout
├── components/
│   ├── common/  Modal, ProgressDoughnut, WeeklyBarChart
│   ├── layout/  Navbar, Footer, StudentHeader, StudentSidebar
│   ├── admin/   AdminSidebar, AdminTopbar
│   └── teacher/ TeacherSidebar, TeacherTopbar, LessonPreviewModal
├── pages/
│   ├── (public/chung) Home, Login, Register, Courses, Chapters, Lesson, Quiz, QuizShow
│   ├── student/  Dashboard, Courses, MyCourses, Progress, Certificates, Profile, QuizResult
│   ├── admin/    Overview, Users, Courses, Stats, Reports, Settings
│   └── teacher/  Overview, Courses, Chapters, Lessons, Quizzes, QuizQuestions, Students, Stats, Profile
├── assets/css/  admin.css, teacher.css, student.css, chapters.css, certificates.css, ...
└── utils/videoUrl.js        # chuyển URL YouTube → embed
```

### 2.3 Cơ chế giao tiếp API (rất quan trọng cho migration)

`src/api/axiosClient.js`:

- `BASE_URL = import.meta.env.VITE_API_BASE_URL` (fallback `http://localhost/studyonline/backend/public`).
- **Request interceptor:** nếu có `token` trong localStorage → thêm header `Authorization: Bearer <token>`.
- **Response interceptor chuẩn hoá:** mọi lời gọi trả về object `{ ok: boolean, status: number, data: <body JSON gốc> }` — **không throw** ở luồng thường.
  - Thành công → `{ ok: true, status, data }`
  - Lỗi có response → `{ ok: false, status, data }`
  - `status === 401` và path **không** bắt đầu `/api/auth/` → `clearAuthStorage()` + `window.location.href = '/login'`.
  - Lỗi mạng → `{ ok:false, status:0, data:{ success:false, message:'Không thể kết nối tới máy chủ...' } }`.

Các trang đọc dữ liệu theo pattern: `res.data.data`, `res.data.token`, `res.data.user`, `res.data.success`, `res.data.message`.

> **HỆ QUẢ MIGRATION #1:** FastAPI **bắt buộc** trả đúng "phong bì" JSON mà PHP đang trả (xem §5.1), nếu không toàn bộ frontend vỡ ngầm (không có exception, chỉ hiển thị rỗng).

### 2.4 Routing & phân quyền phía client

`ProtectedRoute({ roles, wrongRoleRedirect='/login', alertOnWrongRole })`:
- Chưa đăng nhập → `/login`.
- Có `roles` và `user.role` không thuộc → `window.alert(...)` + redirect.

Nhóm route: công khai (`/`, `/login`, `/register`), chung có bảo vệ (`/courses`), student (`/chapters`, `/lesson`, `/quiz`, `/quiz-show`, `/student/*`), `/admin/*` (roles `['admin']`), `/teacher/*` (roles `['teacher','admin']`).

> Đề bài **bỏ Admin** khỏi phạm vi chính → nhánh `/admin/*` sẽ được giữ lại nhưng không phát triển thêm (hoặc ẩn menu), không xoá vội để tránh vỡ build.

### 2.5 Các điểm frontend cần biết

- `utils/videoUrl.js`: hỗ trợ `<video>` file trực tiếp **và** YouTube (chuyển sang `/embed/`).
- `student/Dashboard.jsx` gọi song song `courseService.getCourses()`, `progressService.getProgress()`, `getWeeklyProgress()`, `getRecentActivities()` — đây là chỗ sẽ nhúng thêm widget **Weak Topics / AI Recommendations**.
- `Certificates.jsx` tồn tại nhưng backend **không có** API chứng chỉ (tính năng tĩnh/suy diễn phía client).

---

## 3. CURRENT BACKEND

### 3.1 Stack

- PHP thuần **≥ 8.0** (đang chạy 8.3), **không framework**, **không Composer** (`composer.json` chỉ khai báo PSR-4, không có `vendor/`).
- Autoloader PSR-4 tự viết trong `public/index.php` (map `App\` → `app/`, `Config\` → `config/`).
- Parser `.env` tự viết (đọc từng dòng, tách `=`, strip quote, đổ vào `$_ENV` + `putenv`).
- Điểm vào duy nhất: `backend/public/index.php` + `.htaccess` (rewrite mọi request → `index.php`).

### 3.2 Cây thư mục `backend/`

```
backend/
├── public/
│   ├── index.php        # ⭐ entry: autoload + .env + CORS + route /api/docs + App::run()
│   ├── .htaccess        # RewriteRule ^ index.php [L]
│   ├── docs.php         # Swagger UI (tĩnh)
│   ├── swagger.json     # đặc tả OpenAPI (thủ công, có thể lệch thực tế)
│   └── uploads/         # videos/ images/ documents/  (đích upload)
├── routes/
│   └── api.php          # ⭐ toàn bộ định nghĩa route (Router::get/post/put/delete)
├── app/
│   ├── Core/
│   │   ├── App.php          # require routes/api.php rồi Router::resolve()
│   │   ├── Router.php       # map [METHOD][path] => [Controller::class, 'method']  (KHỚP CHÍNH XÁC, không param)
│   │   ├── Request.php      # getMethod / getPath / getBody(JSON hoặc $_POST) / getHeader
│   │   ├── Response.php     # json()/success()/error() — "phong bì" cố định + exit
│   │   ├── Controller.php   # abstract: success()/error()/getBody()/getQueryParams()
│   │   ├── Model.php        # abstract: $this->db = Database::connect() (PDO)
│   │   └── Database.php     # PDO singleton, đọc config/database.php
│   ├── Middleware/
│   │   ├── JwtMiddleware.php   # đọc "Authorization: Bearer", decode, cache static; lỗi → 401 + exit
│   │   ├── RoleMiddleware.php  # check(...$roles): gọi JwtMiddleware rồi kiểm role; sai → 403 + exit
│   │   └── AuthMiddleware.php  # chỉ alias JwtMiddleware::handle()
│   ├── Services/
│   │   └── JwtService.php   # HS256 tự cài (base64url + hash_hmac), encode/decode, kiểm exp
│   ├── Controllers/        # Auth, User, Course, Chapter, Lesson, Quiz, Enrollment, Payment, Progress, Upload, Report
│   └── Models/             # User, Course, Chapter, Lesson, Enrollment, LessonProgress, Quiz, Question, Result, Payment
├── config/
│   ├── app.php         # env/debug/url
│   ├── database.php    # host/port/dbname/username/password  (từ $_ENV, fallback cứng)
│   └── jwt.php         # secret/expire (fallback 'studyonline_super_secret_key_2026', 604800s = 7 ngày)
├── .env               # APP_*, DB_* (DB_PORT=3307 — cần sửa theo máy), JWT_SECRET, JWT_EXPIRE
└── composer.json      # chỉ PSR-4, không require gói nào
```

### 3.3 Luồng xử lý 1 request

```
Request → public/index.php
  → autoload + parse .env + set CORS(*) + (OPTIONS → 200 exit)
  → nếu path kết thúc /api/docs → docs.php
  → App::run() → require routes/api.php → Router::resolve()
      → $method = REQUEST_METHOD ; $path = REQUEST_URI (bỏ query, bỏ prefix '/studyonline/backend/public', rtrim '/')
      → $callback = routes[$method][$path]  (khớp CHÍNH XÁC)
      → new Controller() ; $controller->$method()
          → (tuỳ action) JwtMiddleware::handle() / RoleMiddleware::check('admin','teacher')
          → Model (PDO prepared statements)
          → Response::success([...]) / Response::error('msg', code)  → echo json_encode ; exit
```

### 3.4 Xác thực

- **JWT HS256 tự cài** (`JwtService`): header `{alg:HS256,typ:JWT}`, payload nghiệp vụ `{ id, fullname, email, role }` + `iat` + `exp` (`time() + 604800`).
- `JwtMiddleware::handle()` — đọc header `Authorization` (hoặc `authorization`), phải bắt đầu `Bearer `, decode; sai/hết hạn → `Response::error(..., 401)` **và `exit`** (middleware kiểu "fail-fast", không phải dependency).
- **Mật khẩu:** `AuthController::login` chấp nhận **cả plaintext lẫn bcrypt**: `$password === $user['password'] || password_verify($password, $user['password'])`. Seed data để **plaintext `123456`**. `User::create()` mới thì hash bằng `password_hash(PASSWORD_DEFAULT)` (bcrypt).
- Không có refresh token, không có blacklist, `logout` chỉ trả success (stateless).

### 3.5 Quy ước API bất thường (khác REST chuẩn)

1. **1 URL cho mỗi resource**, phân biệt bằng **HTTP method + query string**:
   - Chi tiết: `GET /api/courses?id=5`  · Danh sách: `GET /api/courses`  · Lọc: `GET /api/chapters?course_id=3`
   - Sửa: `PUT /api/courses` với `id` trong **body**  · Xoá: `DELETE /api/courses?id=5`
   - **Không có** path param kiểu `/api/courses/5`.
2. "Phong bì" phản hồi (xem §5.1) — `data` được **merge phẳng** vào object gốc, và nhiều endpoint bọc thêm 1 lớp `data` nữa → client đọc `res.data.data`.
3. Nhiều endpoint **đa mục đích qua query flag**: `GET /api/enrollments?ids_only=1`, `?course_id=`, `GET /api/progress?weekly=1|recent=1|course_id=`.
4. Một số action có **side effect ẩn**:
   - `POST /api/progress` → nếu user chưa enroll khoá chứa bài học đó thì **tự động enroll**.
   - `POST /api/payments` → khoá giá 0 thì enroll thẳng; khoá có phí thì tạo payment `pending` → `complete` ngay lập tức (mock, không cổng thanh toán) → enroll.

### 3.6 CORS & Upload

- CORS mở hoàn toàn: `Access-Control-Allow-Origin: *`, methods `GET,POST,PUT,DELETE,OPTIONS`, headers `Content-Type, Authorization`.
- `POST /api/upload` (multipart): field `file` + `type` (`video|image|document`). Kiểm MIME bằng `finfo`, giới hạn 500MB video / 5MB ảnh / 20MB PDF. Lưu vào `public/uploads/<sub>/<time>_<rand>.<ext>`. Trả `{ url: "http://<host>/uploads/..." }`.

---

## 4. CURRENT DATABASE

### 4.1 Nguồn schema

- `database/studyonline_db.sql` — **DROP DATABASE + CREATE** (⚠️ destructive), 9 bảng, `utf8mb4_unicode_ci`, chèn sẵn admin `id=1` (`admin@gmail.com` / `123456` plaintext).
- `database/migration_add_payments.sql` — thêm bảng `payments` (`CREATE TABLE IF NOT EXISTS`, an toàn).
- `database/sample_data.sql` — seed 14 user (id 2–15), 6 course, 18 chapter, 54 lesson, 6 quiz, 30 question, 18 enrollment, 15 payment, 17 result, 15 lesson_progress. `SET FOREIGN_KEY_CHECKS=0`.

### 4.2 Sơ đồ quan hệ (10 bảng)

```
users (1) ──< courses (teacher_id)
users (1) ──< enrollments >── (1) courses
users (1) ──< lesson_progress >── (1) lessons
users (1) ──< results >── (1) quizzes
users (1) ──< payments >── (1) courses

courses (1) ──< chapters (1) ──< lessons
courses (1) ──< quizzes (1) ──< questions
```

### 4.3 Chi tiết các bảng

| Bảng | Cột chính | Ghi chú |
|---|---|---|
| `users` | id, fullname, email(unique), password, **role ENUM('student','teacher','admin')**, avatar, bio, is_active, created_at, updated_at | password đang plaintext ở seed |
| `courses` | id, **teacher_id→users**, title, slug(unique), description, thumbnail, **price DECIMAL(10,2)**, level ENUM(beginner/intermediate/advanced), status ENUM(draft/published/archived), timestamps | |
| `chapters` | id, **course_id→courses**, chapter_name, order_index, created_at | |
| `lessons` | id, **chapter_id→chapters**, title, description, video_url(500), document_url(500), **duration INT (giây, seed=0)**, order_index, is_free, status ENUM(draft/published), timestamps | duration hầu như = 0 |
| `enrollments` | id, **user_id**, **course_id**, enroll_date, **UNIQUE(user_id,course_id)** | |
| `lesson_progress` | id, **user_id**, **lesson_id**, is_completed, **watched_sec INT**, completed_at, updated_at, **UNIQUE(user_id,lesson_id)** | nguồn "thời gian học" thực tế |
| `quizzes` | id, **course_id→courses**, title, description, created_at | **quiz gắn với COURSE, không gắn lesson** |
| `questions` | id, **quiz_id→quizzes**, content, option_a..d, **correct_answer ENUM('A','B','C','D')**, order_index | **không có `topic`, không có `difficulty`, không có `explanation`** |
| `results` | id, **user_id**, **quiz_id**, score INT, total INT, submit_time | **cho phép nhiều lần làm** (không unique) → so sánh "Quiz lần 2" khả thi |
| `payments` | id, **user_id**, **course_id**, amount, method ENUM(card/bank_transfer/momo/zalopay), status ENUM(pending/completed/failed/refunded), transaction_ref, note, paid_at, timestamps | mock, không cổng thật |

### 4.4 Khoảng trống schema so với yêu cầu đề bài

| Yêu cầu | Thiếu gì hiện tại |
|---|---|
| "Weak/Strong topics", "điểm theo topic" | **Không có chiều `topic`** ở `questions`/`quizzes`. Analytics theo topic không thực hiện được nếu không thêm cột. |
| AI Quiz theo **bài học** | `quizzes` chỉ có `course_id`, chưa có `lesson_id`. |
| Quiz có `explanation`, `difficulty` | `questions` chưa có 2 cột này (đề bài yêu cầu output AI có). |
| RAG tài liệu | Chưa có `documents`, `document_chunks`. |
| AI Tutor hội thoại | Chưa có `ai_conversations`, `ai_messages`. |
| Recommendation / Analytics lưu lịch sử | Chưa có `recommendations`, `learning_analytics`. |
| Nguồn "learning time" | Chỉ có `lesson_progress.watched_sec` (do frontend ping); `lessons.duration` = 0. |

→ Tất cả bổ sung là **ADDITIVE** (thêm bảng mới, thêm cột nullable). **Không sửa/xoá cột cũ, không xoá dữ liệu.**

---

## 5. EXISTING APIs

### 5.1 "Phong bì" phản hồi (contract phải giữ nguyên)

```jsonc
// Thành công (Response::success($data, $message)):
{ "success": true, "message": "<tuỳ chọn>", ...$data }
// ví dụ list:   { "success": true, "data": [ ... ] }
// ví dụ detail: { "success": true, "data": { ... } }
// ví dụ login:  { "success": true, "token": "<jwt>", "user": { "id":1,"fullname":"...","email":"...","role":"admin" } }
// ví dụ submit: { "success": true, "quiz": {...}, "score": 8, "total": 10, "percent": 80, "details": [ ... ] }

// Lỗi (Response::error($message, $status)):  HTTP status = $status
{ "success": false, "message": "<thông điệp tiếng Việt>" }
```

Header: `Content-Type: application/json; charset=utf-8`; `json_encode(JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)`.

### 5.2 Bảng đầy đủ endpoint (nguồn: `backend/routes/api.php`)

| # | Method | Path | Auth | Controller::action | Ghi chú hành vi |
|---|---|---|---|---|---|
| 1 | POST | `/api/auth/login` | – | Auth::login | body `{email,password}` → `{token,user}`; chấp nhận plaintext/bcrypt |
| 2 | POST | `/api/auth/register` | – | Auth::register | body `{fullname,email,password,confirm_password}`; luôn tạo role `student` |
| 3 | POST | `/api/auth/logout` | – | Auth::logout | no-op, trả success |
| 4 | GET | `/api/auth/me` | JWT | Auth::me | trả `{user:{id,fullname,email,role}}` từ payload |
| 5 | POST | `/api/auth/change-password` | JWT | Auth::changePassword | body `{old_password,new_password}` (min 6) |
| 6 | GET | `/api/users` | admin/teacher | User::index | `?id=` → chi tiết (teacher chỉ xem chính mình); không id → list toàn bộ |
| 7 | POST | `/api/users` | admin | User::create | body `{fullname,email,password,role}` |
| 8 | PUT | `/api/users` | admin/teacher/student | User::update | non-admin chỉ sửa chính mình, không đổi role |
| 9 | DELETE | `/api/users` | admin | User::delete | `?id=`; không tự xoá mình |
| 10 | GET | `/api/courses` | – | Course::index | `?id=` → chi tiết (kèm `teacher_name`); list sắp xếp id DESC |
| 11 | POST | `/api/courses` | admin/teacher | Course::create | body `{title,description,thumbnail}`; teacher_id = user hiện tại |
| 12 | PUT | `/api/courses` | admin/teacher | Course::update | body `{id,title,description,thumbnail?}` |
| 13 | DELETE | `/api/courses` | admin/teacher | Course::delete | `?id=` (CASCADE xoá chapter/lesson/quiz/...) |
| 14 | GET | `/api/chapters` | – | Chapter::index | **bắt buộc** `?course_id=` hoặc `?id=` |
| 15 | POST | `/api/chapters` | admin/teacher | Chapter::create | body `{course_id,chapter_name}` |
| 16 | PUT | `/api/chapters` | admin/teacher | Chapter::update | body `{id,chapter_name}` |
| 17 | DELETE | `/api/chapters` | admin/teacher | Chapter::delete | `?id=` |
| 18 | GET | `/api/lessons` | – | Lesson::index | **bắt buộc** `?chapter_id=` hoặc `?id=` |
| 19 | POST | `/api/lessons` | admin/teacher | Lesson::create | body `{chapter_id,title,description,video_url,document_url}` |
| 20 | PUT | `/api/lessons` | admin/teacher | Lesson::update | body `{id,title,description,video_url,document_url}` |
| 21 | DELETE | `/api/lessons` | admin/teacher | Lesson::delete | `?id=` |
| 22 | GET | `/api/quizzes` | – | Quiz::index | `?id=` / `?course_id=` / all; mỗi quiz kèm `question_count` |
| 23 | POST | `/api/quizzes` | admin/teacher | Quiz::create | body `{course_id,title,description}` |
| 24 | PUT | `/api/quizzes` | admin/teacher | Quiz::update | body `{id,course_id,title,description}` |
| 25 | DELETE | `/api/quizzes` | admin/teacher | Quiz::delete | `?id=` |
| 26 | GET | `/api/quizzes/questions` | – | Quiz::indexQuestions | **bắt buộc** `?quiz_id=` hoặc `?id=` |
| 27 | POST | `/api/quizzes/questions` | admin/teacher | Quiz::createQuestion | body `{quiz_id,content,option_a..d,correct_answer,order_index}` |
| 28 | PUT | `/api/quizzes/questions` | admin/teacher | Quiz::updateQuestion | body `{id,content,option_a..d,correct_answer,order_index}` |
| 29 | DELETE | `/api/quizzes/questions` | admin/teacher | Quiz::deleteQuestion | `?id=` |
| 30 | POST | `/api/quizzes/submit` | JWT | Quiz::submit | body `{quiz_id, answers:{<question_id>:'A'..'D'}}` → chấm điểm + `details[]` + lưu `results` |
| 31 | GET | `/api/enrollments` | JWT | Enrollment::index | `?course_id=`→`{enrolled}` · `?ids_only=1`→`{data:[id]}` · else theo role |
| 32 | POST | `/api/enrollments` | JWT | Enrollment::create | body `{course_id}`; 409 nếu đã đăng ký |
| 33 | DELETE | `/api/enrollments` | JWT | Enrollment::delete | `?course_id=` |
| 34 | GET | `/api/payments` | JWT | Payment::index | theo role (admin all / teacher theo khoá dạy / student của mình) |
| 35 | POST | `/api/payments` | JWT | Payment::create | body `{course_id,method}`; mock complete + enroll |
| 36 | GET | `/api/payments/check` | JWT | Payment::check | `?course_id=` → `{has_paid,enrolled}` |
| 37 | GET | `/api/progress` | JWT | Progress::index | `?course_id=`→`[lesson_id]` · `?weekly=1`→7 ngày · `?recent=1&limit=`→hoạt động · else tổng hợp theo khoá |
| 38 | POST | `/api/progress` | JWT | Progress::update | body `{lesson_id,watched_sec,is_completed}`; auto-enroll |
| 39 | POST | `/api/upload` | JWT | Upload::upload | multipart `file`+`type`; trả `{url}` |
| 40 | GET | `/api/reports/summary` | admin | Report::summary | `?range=today\|7d\|30d\|1y`; aggregate doanh thu/top khoá/gần đây |

**40 endpoint / 11 controller.** Có `docs.php` + `swagger.json` (đặc tả thủ công, có thể lệch — không dùng làm nguồn chân lý; `routes/api.php` mới là chuẩn).

### 5.3 Endpoint frontend đang thực sự gọi (từ `src/services/*.js`)

Tất cả 11 service map 1–1 với bảng trên. Điểm cần lưu khi migrate:
- `authService.register(...)` gửi `confirm_password`.
- `quizService.submitQuiz(quizId, answers)` — `answers` là object `{questionId: 'A'}`.
- `uploadService` set `Content-Type: multipart/form-data` + `onUploadProgress`.
- `reportService.getSummary(range)` — chỉ dùng ở khu admin.

---

## 6. PHP → FastAPI MIGRATION MAP

### 6.1 Nguyên tắc

1. **Giữ nguyên contract HTTP** (path, method, query flag, phong bì JSON, thông điệp lỗi tiếng Việt, HTTP status) ở Phase 2–3 để frontend **gần như không phải sửa**. Việc "REST hoá" (`/api/courses/{id}`) — nếu làm — để **phase sau** kèm sửa đồng bộ 11 service.
2. **Tái sử dụng MySQL `studyonline_db` hiện có.** Alembic: `alembic stamp head` coi schema hiện tại là baseline, rồi chỉ thêm migration additive.
3. **Không xoá `backend/` PHP ngay** — đổi tên thành `legacy-backend-php/` để đối chiếu hành vi trong lúc test parity.

### 6.2 Ánh xạ thành phần

| PHP hiện tại | FastAPI tương đương | Ghi chú |
|---|---|---|
| `public/index.php` (autoload + .env + CORS + bootstrap) | `app/main.py` (`FastAPI()`, `CORSMiddleware`, include routers) + `app/core/config.py` (`pydantic-settings`) | |
| `app/Core/Router.php` + `routes/api.php` | `app/routers/*.py` với `APIRouter(prefix="/api")` | giữ path y hệt |
| `app/Core/Request.php` | `Request` của FastAPI + Pydantic models (`app/schemas/`) | body JSON tự parse |
| `app/Core/Response.php` (phong bì cố định) | helper `app/core/responses.py`: `ok(data=..., message=...)`, `err(message, status)` + `JSONResponse` (ensure_ascii=False) | **giữ đúng shape** |
| `app/Core/Database.php` (PDO singleton) | `app/core/database.py`: `create_engine("mysql+pymysql://...")` + `SessionLocal` + `get_db()` dependency | |
| `app/Core/Model.php` + `app/Models/*` | `app/models/*.py` (SQLAlchemy declarative) + `app/services/*.py` (truy vấn/nghiệp vụ) | tách model ORM vs logic |
| `app/Services/JwtService.php` (HS256 tự cài) | `app/core/security.py` dùng `python-jose[cryptography]` hoặc `pyjwt` | giữ `JWT_SECRET`, `exp` 7 ngày |
| `JwtMiddleware::handle()` (fail-fast + exit) | `Depends(get_current_user)` → raise `HTTPException(401)` | payload giữ key `id`,`fullname`,`email`,`role` |
| `RoleMiddleware::check(...$roles)` | `Depends(require_roles("teacher","admin"))` (factory) | 403 khi sai role |
| `password_hash`/`password_verify` (bcrypt) | `passlib[bcrypt]`; `verify_password` **giữ nhánh so sánh plaintext** cho dữ liệu seed | |
| `UploadController` (`move_uploaded_file`, `finfo`) | `UploadFile` + `python-magic`/kiểm đuôi + lưu `backend/uploads/` + `StaticFiles` mount `/uploads` | |
| `.htaccess` rewrite | không cần (Uvicorn) | |
| `docs.php` + `swagger.json` thủ công | Swagger tự sinh tại `/docs`, ReDoc `/redoc` | bỏ file thủ công |

### 6.3 Ánh xạ router (giữ path nguyên trạng)

| Router FastAPI | Bao gồm endpoint # (theo §5.2) | Dependency mặc định |
|---|---|---|
| `routers/auth.py` | 1–5 | 4,5 cần `get_current_user` |
| `routers/users.py` | 6–9 | `require_roles` tuỳ action |
| `routers/courses.py` | 10–13 | ghi: `require_roles("teacher","admin")` |
| `routers/chapters.py` | 14–17 | như trên |
| `routers/lessons.py` | 18–21 | như trên |
| `routers/quizzes.py` | 22–30 | 30 chỉ cần đăng nhập |
| `routers/enrollments.py` | 31–33 | `get_current_user` |
| `routers/payments.py` | 34–36 | `get_current_user` |
| `routers/progress.py` | 37–38 | `get_current_user` |
| `routers/uploads.py` | 39 | `get_current_user` |
| `routers/reports.py` | 40 | `require_roles("admin")` — giữ, không phát triển thêm |
| `routers/ai.py` | **MỚI** (§7) | tuỳ endpoint |
| `routers/analytics.py` | **MỚI** (§10) | `get_current_user` |

### 6.4 Bẫy cần xử lý khi port

- **`GET /api/chapters|lessons|quizzes/questions` bắt buộc query** → nếu thiếu, PHP trả `error(...)` 400. Giữ nguyên.
- **Side effect** `POST /api/progress` auto-enroll và `POST /api/payments` auto-complete+enroll — port **đúng logic**, có test.
- **`Quiz::submit`**: `answers` key = `question_id` (string). `percent = round(score/total*100)`. Trả `details[]` gồm cả `option_a..d`, `chosen`, `correct_answer`, `is_right`.
- **`results` không unique** → mỗi lần submit là 1 dòng mới (cần cho "Quiz lần 2" ở §10).
- **JWT payload key `id`** (không phải `user_id`). Đề bài §20 ghi `user_id` — để **an toàn frontend**, giữ `id` (có thể thêm `sub`/`user_id` song song).
- **Enum role** vẫn `('student','teacher','admin')` trong DB. Đề bài chỉ dùng 2 vai trò → không đổi enum, chỉ giới hạn ở tầng ứng dụng.
- **CORS**: chuyển từ `*` sang danh sách origin cấu hình được (`FRONTEND_ORIGIN` trong `.env`), vẫn cho `*` ở môi trường dev.
- **Thông điệp lỗi**: giữ tiếng Việt gần đúng để không phá UX (frontend hiển thị thẳng `res.data.message`).

### 6.5 Thay đổi phía Frontend (tối thiểu)

| File | Thay đổi |
|---|---|
| `frontend/.env` | `VITE_API_BASE_URL` → URL FastAPI (dev: `http://127.0.0.1:8000`) |
| `src/api/axiosClient.js` | Sửa fallback URL + câu thông báo lỗi "Kiểm tra XAMPP đang chạy" → "Kiểm tra API server". Logic giữ nguyên. |
| `src/services/*.js` | **Không đổi** nếu giữ contract. Chỉ thêm `aiService.js`, `analyticsService.js` mới. |
| `package.json` | thêm `lucide-react` |
| Trang mới | `pages/student/AiTutor.jsx`, `pages/teacher/AiQuizGenerator.jsx`, widget Recommendation/WeakTopics trong `student/Dashboard.jsx` + `student/Progress.jsx` |

---

## 7. AI ARCHITECTURE

### 7.1 Ba khối AI (đúng phạm vi đề bài, không hơn)

```
                         FastAPI  app/ai/
   ┌───────────────────────────┼───────────────────────────┐
   │                           │                           │
1) RAG AI TUTOR         2) AI QUIZ GENERATOR        3) RULE-BASED RECOMMENDATION
   RAG + LLM               Fine-tuned LLM + context     Rule engine (thuần Python)
   → ChromaDB              → LoRA/QLoRA adapter          → không ML
   → sources trích dẫn     → validate JSON + duyệt tay   → phân loại Weak/Avg/Good/Excellent
```

### 7.2 Thư mục AI trong backend

```
backend/app/ai/
├── model_manager.py     # nạp LLM (API hoặc local + LoRA adapter) theo .env; 1 chỗ đổi model
├── rag/
│   ├── document_loader.py   # PDF/DOCX/TXT → text (pypdf, python-docx)
│   ├── text_splitter.py     # chunk ~500–800 token, overlap 100
│   ├── embeddings.py        # SentenceTransformers (vd: bkai-foundation/vietnamese-bi-encoder hoặc all-MiniLM)
│   ├── vector_store.py      # ChromaDB PersistentClient, collection theo course
│   ├── retriever.py         # similarity search top-k + filter metadata {course_id,lesson_id}
│   └── rag_pipeline.py      # build prompt + gọi LLM + trả {answer, sources[]}
├── quiz_generator.py    # lesson/context → prompt → fine-tuned model → parse+repair JSON → validate schema
├── tutor.py             # orchestrate hội thoại: lưu ai_conversations/ai_messages, gọi rag_pipeline
└── recommendation.py    # rule engine (§10)
```

### 7.3 Cấu hình (`.env`, không hard-code)

```env
LLM_PROVIDER=gemini            # gemini | openai | hf_local | hf_inference
LLM_MODEL=                     # vd: gemini-2.0-flash  /  Qwen/Qwen2.5-1.5B-Instruct
LLM_API_KEY=
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DB_PATH=./data/chroma
BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct   # cho quiz generator fine-tune
LORA_ADAPTER_PATH=./data/adapters/quizgen-lora    # rỗng = dùng base model
AI_MAX_CONTEXT_CHUNKS=5
```

`model_manager.py` đọc các biến này; **code không phụ thuộc model cụ thể** — đổi model chỉ sửa `.env`.

### 7.4 Endpoint AI mới (`routers/ai.py`)

| Method | Path | Auth | Mô tả |
|---|---|---|---|
| POST | `/api/ai/generate-quiz` | teacher | body `{course_id, lesson_id, number_of_questions, difficulty}` → `{questions:[...]}` (preview, **chưa lưu**) |
| POST | `/api/ai/quiz/approve` | teacher | body `{course_id, lesson_id?, title, questions:[...]}` → tạo `quizzes` + `questions` thật (đã giáo viên chỉnh/duyệt) |
| POST | `/api/ai/chat` | student/teacher | body `{course_id, lesson_id?, conversation_id?, message}` → `{answer, sources:[{document,page}], conversation_id}` |
| GET | `/api/ai/conversations` | student | list hội thoại của user (theo course) |
| GET | `/api/ai/conversations/{id}` | student | lịch sử messages |
| DELETE | `/api/ai/conversations/{id}` | student | clear conversation |
| POST | `/api/ai/documents/ingest` | teacher | body `{document_id}` (hoặc kèm upload) → chạy pipeline RAG, ghi `document_chunks` + nạp vector store |
| GET | `/api/ai/documents?course_id=` | teacher | trạng thái index tài liệu |

### 7.5 Nguyên tắc bắt buộc (từ đề bài)

- **AI Quiz KHÔNG tự lưu.** Luôn qua bước preview → giáo viên duyệt (`/api/ai/quiz/approve`).
- **RAG không bịa nguồn.** Không đủ ngữ cảnh → trả đúng câu: *"Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."*
- **Quiz lỗi JSON không vào DB.** `quiz_generator.py`: parse → repair (vd `json-repair`) → retry (tối đa N lần) → nếu vẫn hỏng trả lỗi rõ ràng cho giáo viên.

---

## 8. RAG ARCHITECTURE

### 8.1 Pipeline nạp tài liệu (ingest — chạy khi giáo viên upload/ingest)

```
documents (PDF/DOCX/TXT trong backend/uploads/documents)
   │  document_loader.py
   ▼
raw text  ──►  cleaning (bỏ header/footer, chuẩn hoá khoảng trắng, giữ số trang)
   │  text_splitter.py  (chunk 500–800 token, overlap ~100)
   ▼
chunks[]  ──►  embeddings.py (SentenceTransformers)  ──►  vectors[]
   │
   ▼
ChromaDB collection "course_<id>"  +  bảng MySQL document_chunks (id, document_id, course_id, lesson_id, chunk_index, page, content, token_count)
```

Metadata mỗi vector: `{ course_id, lesson_id, document_id, page, chunk_index }` → cho phép **lọc theo đúng khoá học** khi truy vấn.

### 8.2 Pipeline trả lời (query — khi sinh viên hỏi)

```
question  ──► embeddings.py ──► query vector
   │
   ▼
ChromaDB.similarity_search(query_vector, k=AI_MAX_CONTEXT_CHUNKS, filter={course_id [, lesson_id]})
   │
   ▼
top-k chunks  ──► ghép thành context (kèm nhãn nguồn [Doc, tr.X])
   │
   ▼
prompt = SYSTEM(chỉ trả lời dựa trên context, không bịa, trả câu "không tìm thấy" nếu thiếu)
       + context + lịch sử hội thoại ngắn + question
   │
   ▼
LLM (model_manager) ──► answer
   │
   ▼
response = { answer, sources: [{document, page}] }  ──► lưu ai_messages
```

### 8.3 Thư mục & bảng

- Code: `backend/app/ai/rag/` (§7.2).
- Vector store: ChromaDB persistent tại `VECTOR_DB_PATH` (mặc định `backend/data/chroma`) — **không commit** vào git.
- MySQL: `documents`, `document_chunks` (giữ bản sao text + metadata để truy vết, không phụ thuộc hoàn toàn vào Chroma).

### 8.4 Đánh giá RAG (§14 đề bài — cần số liệu thật)

Tạo `backend/training/rag_eval/` với test set: `[{question, expected_document, expected_topic/lesson}]` (~20–40 câu).
Đo: **Retrieval hit@k** (tài liệu đúng có trong top-k?), **Answer relevance** (chấm tay hoặc LLM-as-judge 1–5), **Source correctness** (nguồn trích dẫn có khớp không).

---

## 9. FINE-TUNING ARCHITECTURE

### 9.1 Mục tiêu (rõ ràng theo đề bài)

Fine-tune **KHÔNG** để model "biết thêm kiến thức". Mục tiêu: **dạy model xuất Quiz đúng ĐỊNH DẠNG JSON của StudyOnline** (ổn định, ít lỗi parse, câu hỏi bám ngữ cảnh bài học).

### 9.2 Thư mục

```
backend/training/
├── dataset/
│   ├── train.jsonl          # ~300–800 mẫu
│   ├── validation.jsonl     # ~15%
│   └── test.jsonl           # ~15%  (giữ để so Base vs Fine-tuned)
├── prepare_dataset.py       # sinh cặp instruction/input/output từ tài liệu giáo dục mẫu + quiz hiện có trong DB
├── train_lora.py            # LoRA/QLoRA (PEFT + TRL SFTTrainer), chạy được trên Colab T4/A100
├── evaluate.py              # chấm test.jsonl: JSON valid %, đúng format %, câu hỏi hợp lệ %, tỉ lệ trùng
└── README.md                # hướng dẫn chạy trên Colab + cách đưa adapter về backend
```

### 9.3 Định dạng dữ liệu (1 dòng JSONL)

```json
{
  "instruction": "Tạo 5 câu hỏi trắc nghiệm về HTTP ở mức trung bình. Trả về JSON đúng schema StudyOnline.",
  "input": "HTTP là giao thức tầng ứng dụng ... (nội dung bài học / chunk tài liệu)",
  "output": "{\"questions\":[{\"question\":\"...\",\"options\":{\"A\":\"...\",\"B\":\"...\",\"C\":\"...\",\"D\":\"...\"},\"correct_answer\":\"A\",\"explanation\":\"...\",\"difficulty\":\"medium\",\"topic\":\"HTTP\"}]}"
}
```

Nguồn dữ liệu: (a) tài liệu giáo dục mẫu công khai (CNTT cơ bản), (b) 6 quiz × 30 câu hỏi đang có trong DB (đảo ngược thành cặp input→output), (c) tự soạn thêm. **Không dùng dữ liệu cá nhân.**

### 9.4 Pipeline

```
Course docs / lessons / quiz hiện có
        │  prepare_dataset.py
        ▼
   train / validation / test (.jsonl)
        │
        ▼
Base model (Qwen2.5-1.5B/3B-Instruct hoặc Gemma-2-2B — chọn theo GPU Colab)
        │  train_lora.py  (QLoRA 4-bit nếu VRAM thấp; LoRA nếu đủ)
        ▼
Fine-tuned LoRA adapter  (vài chục MB)  ──► lưu ./data/adapters/quizgen-lora
        │  evaluate.py  (so Base vs Fine-tuned trên test.jsonl)
        ▼
Backend nạp: model_manager.load_base() + PeftModel.from_pretrained(adapter)
        ▼
/api/ai/generate-quiz
```

### 9.5 Ràng buộc vận hành (§29 đề bài)

- Fine-tuning **không chạy trong backend production**. Chạy trên **Google Colab / HF / GPU cloud**, chỉ **đem adapter về**.
- Nếu không có GPU và không kịp fine-tune: backend vẫn chạy `generate-quiz` bằng **base model + prompt engineering + JSON validator** (`LORA_ADAPTER_PATH` rỗng). Fine-tune là phần nâng cấp chất lượng, có số liệu so sánh Base vs Fine-tuned để đưa vào báo cáo.

### 9.6 Đánh giá (bảng phải là số đo thật từ `evaluate.py`)

| Metric | Base | Fine-tuned |
|---|---|---|
| JSON hợp lệ (%) | _đo_ | _đo_ |
| Đúng schema/format (%) | _đo_ | _đo_ |
| Câu hỏi liên quan ngữ cảnh (%) | _đo_ | _đo_ |
| Tỉ lệ câu trùng lặp (%) | _đo_ | _đo_ |

---

## 10. RECOMMENDATION ARCHITECTURE

### 10.1 Loại: **Rule-based** (không ML) — đúng đề bài §15.

### 10.2 Đầu vào (tính từ dữ liệu học tập thật)

| Tín hiệu | Nguồn |
|---|---|
| Điểm quiz trung bình | `results` (`AVG(score*100/total)`), theo course và/hoặc theo topic |
| Tiến độ khoá học (%) | `lesson_progress` vs tổng `lessons` của course |
| Số bài đã hoàn thành | `lesson_progress.is_completed=1` |
| Thời gian học | `SUM(lesson_progress.watched_sec)` |
| Số lần làm quiz | `COUNT(results)` theo quiz/user |
| Topic yếu/mạnh | điểm trung bình theo `questions.topic` (⚠️ cần thêm cột `topic`) |

### 10.3 Rule engine (`app/ai/recommendation.py`)

```
score = điểm quiz trung bình gần nhất (theo course hoặc topic)

if score < 50:      level = "Weak"       → ["Học lại bài", "Làm quiz cơ bản"]
elif score < 70:    level = "Average"    → ["Làm quiz luyện tập"]
elif score < 85:    level = "Good"       → ["Học bài tiếp theo"]
else:               level = "Excellent"  → ["Nội dung nâng cao"]
```

Kết hợp thêm luật phụ: tiến độ < 50% → ưu tiên "hoàn thành bài chưa học"; topic có điểm thấp nhất → chèn "ôn lại topic X trước".

### 10.4 Vòng lặp cá nhân hoá (điểm nhấn bảo vệ đồ án — §16)

```
Học bài → Làm Quiz → Lưu results → Learning Analytics → Xác định topic yếu
      → Gợi ý bài học → Học lại → Làm Quiz lần 2 → So sánh kết quả (lần 1 vs lần 2)
```

`results` cho phép nhiều lần làm → truy vấn 2 lần gần nhất cùng `quiz_id` để hiển thị "tiến bộ +X%". Recommendation **được lưu** vào bảng `recommendations` mỗi lần sinh → chứng minh nó **thay đổi theo dữ liệu mới**.

### 10.5 Endpoint (`routers/analytics.py`)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/analytics/overview?course_id=` | avg quiz score, completion rate, completed lessons, learning time, quiz attempts |
| GET | `/api/analytics/topics?course_id=` | `[{topic, avg_score, status}]` (Weak/Good/Excellent) |
| GET | `/api/recommendations?course_id=` | gợi ý hiện tại + lịch sử |
| POST | `/api/recommendations/refresh` | tính lại từ dữ liệu mới nhất, ghi `recommendations` |
| GET | `/api/analytics/quiz-progress?quiz_id=` | so sánh các lần làm (cho vòng lặp §10.4) |

### 10.5 bảng mới

`learning_analytics` (snapshot theo user×course: avg_score, completion_pct, completed_lessons, total_time_sec, quiz_attempts, computed_at) — cache kết quả nặng, không bắt buộc realtime.
`recommendations` (id, user_id, course_id, topic?, level, items JSON, based_on JSON, created_at).

---

## 11. FILES TO CREATE

### 11.1 Backend FastAPI (thư mục `backend/` mới, sau khi đổi tên bản PHP)

```
backend/
├── app/
│   ├── main.py
│   ├── core/           config.py  database.py  security.py  dependencies.py  responses.py
│   ├── models/         user.py course.py chapter.py lesson.py enrollment.py
│   │                   lesson_progress.py quiz.py question.py result.py payment.py
│   │                   document.py document_chunk.py ai_conversation.py ai_message.py
│   │                   recommendation.py learning_analytics.py  __init__.py(Base)
│   ├── schemas/        auth.py user.py course.py chapter.py lesson.py quiz.py
│   │                   enrollment.py payment.py progress.py ai.py analytics.py common.py
│   ├── routers/        auth.py users.py courses.py chapters.py lessons.py quizzes.py
│   │                   enrollments.py payments.py progress.py uploads.py reports.py
│   │                   ai.py analytics.py
│   ├── services/       auth_service.py course_service.py quiz_service.py
│   │                   enrollment_service.py progress_service.py payment_service.py
│   │                   report_service.py analytics_service.py
│   └── ai/             model_manager.py quiz_generator.py tutor.py recommendation.py
│       └── rag/        document_loader.py text_splitter.py embeddings.py
│                       vector_store.py retriever.py rag_pipeline.py
├── training/           dataset/{train,validation,test}.jsonl  prepare_dataset.py
│                       train_lora.py  evaluate.py  rag_eval/  README.md
├── alembic/            env.py  versions/  (001_baseline_stamp, 002_add_ai_tables, 003_add_question_topic_difficulty, 004_add_quiz_lesson_id)
├── alembic.ini
├── requirements.txt    fastapi uvicorn[standard] sqlalchemy pymysql alembic pydantic
│                       pydantic-settings python-jose[cryptography] passlib[bcrypt]
│                       python-multipart pypdf python-docx
│                       langchain langchain-community sentence-transformers chromadb
│                       (fine-tune, cài riêng ở Colab: transformers peft trl bitsandbytes torch accelerate datasets)
├── .env  /  .env.example
├── uploads/            videos/ images/ documents/   (giữ file đã có)
└── README.md
```

### 11.2 Frontend (bổ sung)

```
frontend/src/
├── services/       aiService.js        analyticsService.js
├── pages/student/  AiTutor.jsx         (LearningAnalytics gộp vào Progress.jsx)
├── pages/teacher/  AiQuizGenerator.jsx
├── components/
│   ├── ai/         ChatWindow.jsx  MessageBubble.jsx  SourceCitation.jsx
│   │               GeneratedQuestionCard.jsx  QuizPreviewPanel.jsx
│   └── common/     RecommendationCard.jsx  WeakTopicsList.jsx  TopicScoreBar.jsx
└── (Dashboard.jsx / Progress.jsx: chèn widget)
```

### 11.3 Tài liệu DATN

```
docs/
├── architecture.md      # Client · FastAPI · MySQL · RAG · Vector DB · LLM · Fine-tuning · Recommendation
├── api.md               # bảng endpoint (cũ giữ nguyên + mới)
├── rag.md               # ingest + query pipeline, đánh giá
├── fine-tuning.md       # dataset, base model, LoRA/QLoRA, train, eval, deploy adapter
└── recommendation.md    # tín hiệu, phân loại, rule engine, vòng lặp cá nhân hoá
```

### 11.4 SQL migration mới

```
database/
├── 02_add_ai_tables.sql              # documents, document_chunks, ai_conversations, ai_messages, recommendations, learning_analytics
├── 03_alter_questions_add_topic.sql  # ADD COLUMN topic VARCHAR(100) NULL, difficulty ENUM('easy','medium','hard') NULL, explanation TEXT NULL
└── 04_alter_quizzes_add_lesson.sql   # ADD COLUMN lesson_id INT NULL + FK
```
(Được quản lý qua Alembic; file .sql giữ để đọc nhanh/khôi phục thủ công.)

---

## 12. FILES TO MODIFY

| File | Thay đổi | Rủi ro |
|---|---|---|
| `frontend/.env` | `VITE_API_BASE_URL` → URL FastAPI | thấp |
| `frontend/src/api/axiosClient.js` | fallback URL + text lỗi (bỏ "XAMPP"); **giữ logic phong bì & 401** | thấp |
| `frontend/package.json` | thêm `lucide-react` | thấp |
| `frontend/src/pages/student/Dashboard.jsx` | chèn `RecommendationCard` + `WeakTopicsList` | trung bình |
| `frontend/src/pages/student/Progress.jsx` | thêm mục Learning Analytics theo topic | trung bình |
| `frontend/src/pages/teacher/Quizzes.jsx` | thêm nút "Tạo Quiz bằng AI" → điều hướng `AiQuizGenerator` | thấp |
| `frontend/src/routes/AppRoutes.jsx` | thêm route `/student/ai-tutor`, `/teacher/ai-quiz` | thấp |
| `frontend/src/components/layout/StudentSidebar.jsx`, `components/teacher/TeacherSidebar.jsx` | thêm mục menu AI | thấp |
| `database/studyonline_db.sql` | (khuyến nghị) tách phần `DROP DATABASE`/seed admin ra file riêng để tránh chạy nhầm mất dữ liệu | thấp |
| `README.md` | cập nhật hướng dẫn chạy (FastAPI thay PHP) | thấp |
| `.gitignore` | thêm `backend/data/`, `backend/uploads/*` (trừ .gitkeep), `**/__pycache__/`, `*.pyc`, `.venv/`, `backend/.env` | thấp |

**Không sửa** (giữ nguyên để không phá frontend): 11 file `frontend/src/services/*.js` hiện có, các trang student/teacher hiện có (ngoài các mục chèn widget), toàn bộ `assets/css/`.

---

## 13. FILES TO DELETE / ARCHIVE

> Quy tắc đề bài: **không xoá DB, không xoá dữ liệu, không rewrite thừa.** Vì vậy phần lớn là **ARCHIVE (đổi tên)**, xoá hẳn để cuối cùng.

| Đối tượng | Hành động | Thời điểm |
|---|---|---|
| `backend/` (PHP REST hiện tại) | **Đổi tên → `legacy-backend-php/`** (giữ để đối chiếu hành vi khi test parity) | Đầu Phase 2 |
| `app/`, `core/`, `public/` (MVC monolith gốc) | **Đổi tên → `legacy-mvc-php/`** | Đầu Phase 2 |
| `legacy-frontend-vanilla-backup/` | Giữ nguyên (đã là bản lưu, vô hại). Xoá ở Phase 12 nếu muốn gọn | Phase 12 |
| `test_db.php` | Chuyển `docs/legacy/` (thay bằng check trong README FastAPI) | Phase 2 |
| `StudyOnline.postman_collection.json`, `StudyOnline.postman_environment.json` | Giữ; cập nhật/không dùng (đã có `/docs` tự sinh). Có thể chuyển `docs/` | Phase 3 |
| `package.json` ở thư mục gốc (chỉ có tailwind, không script) | Xoá (thừa; frontend có `package.json` riêng) | Phase 2 |
| `backend/public/docs.php`, `backend/public/swagger.json` | Theo `legacy-backend-php/` (Swagger mới tự sinh tại `/docs`) | Phase 2 |
| `legacy-backend-php/`, `legacy-mvc-php/` | **Xoá hẳn** sau khi FastAPI đạt parity & demo ổn | Cuối Phase 3 |

Xoá hẳn hoàn toàn chỉ khi: (1) FastAPI pass toàn bộ test parity, (2) frontend chạy end-to-end trên FastAPI, (3) đã commit mốc "LMS parity".

---

## 14. RISKS

### 14.1 Migration

| # | Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|---|
| R1 | **Sai "phong bì" JSON** (thiếu `success`, sai lớp `data`, escape unicode) | Frontend hỏng ngầm, không lỗi rõ | Helper `ok()/err()` tập trung; test so sánh byte-level output PHP vs FastAPI cho từng endpoint |
| R2 | Routing khác kiểu (query flag `?ids_only`, `?weekly`, `id` trong body) | 404 / hành vi lệch | Giữ **đúng** path + query; checklist 40 endpoint (§5.2) |
| R3 | JWT payload key `id` vs `user_id` | `/auth/me`, các trang đọc `user.id` lỗi | Giữ `id`,`fullname`,`email`,`role`; thêm `user_id` song song nếu cần |
| R4 | Mật khẩu seed **plaintext** | Không đăng nhập được sau migrate | `verify_password` giữ nhánh `plain == stored` cho hàng cũ |
| R5 | Side effect ẩn (`progress` auto-enroll, `payment` auto-complete) không port | Sai nghiệp vụ, test student vỡ | Ghi rõ trong §6.4; viết unit test cho từng side effect |
| R6 | `studyonline_db.sql` có `DROP DATABASE` | Chạy nhầm → **mất toàn bộ dữ liệu** | Tách file; Alembic `stamp` thay vì re-run; backup trước mỗi phase |
| R7 | CORS từ `*` → siết origin sai | Frontend bị chặn | Biến `.env` `FRONTEND_ORIGIN`, dev vẫn `*` |
| R8 | Node 24 + Vite 6 (một số peer chưa chuẩn) | `npm run dev` cảnh báo/khựng | Đã chạy OK (Vite 6.4.3). Ghi chú dùng Node LTS 20/22 nếu CI trục trặc |
| R9 | Cổng: MySQL 3306 (không 3307), service manual, **8000 bị app Python khác chiếm** | Không kết nối / xung đột | `.env` cấu hình cổng; backend dev dùng 8000 (kill app kia) hoặc 8001; tài liệu hoá |

### 14.2 AI

| # | Rủi ro | Giảm thiểu |
|---|---|---|
| A1 | **Không có GPU** để fine-tune | Colab/HF; hoặc bỏ qua fine-tune, chạy base model + validator (đề bài §29 cho phép) |
| A2 | LLM API tốn phí / rate limit / cần key | `LLM_PROVIDER` đổi được; hỗ trợ model local nhỏ; cache câu trả lời khi demo |
| A3 | Model xuất **JSON hỏng** | validator schema + `json-repair` + retry N lần + không lưu bản hỏng (đề bài §10) |
| A4 | RAG **bịa nguồn / trả sai** | prompt ràng buộc "chỉ dùng context"; trả câu "không tìm thấy"; hiển thị sources; test hit@k |
| A5 | Trích xuất PDF tiếng Việt kém (OCR, layout cột) | chọn tài liệu text-based; `pypdf` + fallback; làm sạch; giới hạn loại tài liệu demo |
| A6 | Embedding model không tối ưu tiếng Việt | dùng `bkai-foundation-models/vietnamese-bi-encoder` hoặc đa ngữ; đo lại hit@k |
| A7 | ChromaDB persist / version lệch | pin version trong `requirements.txt`; `VECTOR_DB_PATH` ngoài git; script rebuild index |
| A8 | Thiếu chiều `topic` → analytics topic không chạy | thêm cột `questions.topic` (additive) + backfill thủ công cho 30 câu seed |
| A9 | `lessons.duration = 0` → "learning time" chỉ dựa `watched_sec` | tài liệu hoá cách tính; frontend ping `watched_sec` khi xem |

### 14.3 Phạm vi / đồ án

| # | Rủi ro | Giảm thiểu |
|---|---|---|
| S1 | Đề bài rất rộng (12 phase, 3 khối AI) — dễ trễ | Ưu tiên **LMS parity (Phase 2–3) xong trước**; AI làm tăng dần; mỗi phase có Definition of Done |
| S2 | Over-engineering (microservice, k8s...) | Cấm theo §32; giữ 1 backend FastAPI, 1 vector DB nhúng |
| S3 | Sửa frontend quá nhiều → vỡ UI đang chạy | Giữ contract API; chỉ **thêm** trang/widget, không rewrite |
| S4 | Demo phụ thuộc mạng/API ngoài | Chuẩn bị kịch bản demo offline: model local nhỏ + tài liệu đã ingest sẵn + dữ liệu seed |

---

## 15. DEVELOPMENT PLAN

> Quy tắc: **mỗi Phase = Implement → Test → Fix → Report**. Không sang Phase mới khi Phase trước chưa ổn định. Backup DB trước mỗi Phase có migration.

### PHASE 1 — Phân tích (ĐANG Ở ĐÂY) ✅
- **Làm:** scan toàn bộ source, viết `MIGRATION_PLAN.md` (file này).
- **DoD:** 15 mục hoàn tất; đã dựng chạy được hệ thống hiện tại 1 lần để xác nhận baseline (đã làm: MySQL 3306, backend :8001, frontend :5173, login OK).
- **Chưa code chức năng mới.**

### PHASE 2 — Migrate PHP → FastAPI (LMS core)
- Đổi tên `backend/` → `legacy-backend-php/`; tạo `backend/` FastAPI (skeleton §11.1).
- `core/`: config, database (SQLAlchemy + PyMySQL tới `studyonline_db` hiện có), security (JWT HS256, verify_password dual), responses (phong bì), dependencies (`get_current_user`, `require_roles`).
- Alembic: `stamp` baseline (không tạo lại bảng).
- Models SQLAlchemy cho 10 bảng hiện có.
- Port **40 endpoint** theo §5.2 (giữ path/query/envelope). Upload → `StaticFiles`.
- **Test:** script đối chiếu response PHP (`legacy-backend-php` chạy song song :8001) vs FastAPI (:8000) cho mọi endpoint với token admin/teacher/student; unit test side effect (R5).
- **DoD:** 40/40 endpoint trả cùng shape + status; `pytest` xanh; login 3 vai trò OK.

### PHASE 3 — Nối React ↔ FastAPI + test toàn bộ LMS
- `frontend/.env` + `axiosClient.js` (§12).
- Chạy tay toàn bộ luồng: đăng ký/đăng nhập, giáo viên tạo course→chapter→lesson→quiz→question→upload, sinh viên enroll/học/đánh dấu hoàn thành/làm quiz/xem kết quả/lịch sử/tiến độ, thanh toán mock.
- **DoD:** mọi trang student & teacher hoạt động như trước migration; không lỗi console; xoá được `legacy-*` (giữ tới hết Phase 3 rồi commit mốc "LMS parity").

### PHASE 4 — Learning Analytics
- Migration `learning_analytics` + cột `questions.topic` (+ `difficulty`,`explanation`), backfill topic cho 30 câu seed.
- `analytics_service.py` + `routers/analytics.py`: overview, topics, quiz-progress.
- Frontend: mục Analytics trong `Progress.jsx` (avg score, completion, time, topic bars).
- **DoD:** số liệu khớp truy vấn SQL kiểm chứng tay; hiển thị Weak/Good/Excellent theo topic.

### PHASE 5 — Rule-based Recommendation
- Migration `recommendations`.
- `recommendation.py` (rule engine §10.3) + endpoints `/api/recommendations`, `/refresh`.
- Frontend: `RecommendationCard` + `WeakTopicsList` trên Dashboard.
- Demo **vòng lặp §10.4**: làm quiz điểm thấp → gợi ý học lại → làm lại → so sánh lần 1/lần 2 → gợi ý đổi.
- **DoD:** recommendation thay đổi quan sát được khi dữ liệu mới; lịch sử lưu trong bảng.

### PHASE 6 — RAG (AI Tutor)
- Migration `documents`, `document_chunks`, `ai_conversations`, `ai_messages`.
- `app/ai/rag/*` + `tutor.py` + endpoints `/api/ai/documents/ingest`, `/api/ai/chat`, conversations CRUD.
- ChromaDB persistent; embeddings tiếng Việt.
- Frontend: `AiTutor.jsx` (chat UI §23: history, loading, error, **source citation**, clear).
- **Test:** ingest 3–5 PDF/DOCX/TXT; test set hit@k; kiểm câu "không tìm thấy".
- **DoD:** hỏi đúng tài liệu khoá → trả lời + nguồn đúng; hỏi ngoài phạm vi → trả câu từ chối chuẩn.

### PHASE 7 — Dataset fine-tuning
- `prepare_dataset.py`: sinh `train/validation/test.jsonl` từ tài liệu mẫu + 6 quiz seed + tự soạn.
- **DoD:** ≥ 300 mẫu train hợp lệ schema; `test.jsonl` giữ riêng; README mô tả nguồn (không dữ liệu cá nhân).

### PHASE 8 — Fine-tune LoRA/QLoRA (trên Colab)
- `train_lora.py` (PEFT+TRL, QLoRA 4-bit); chọn base model theo VRAM (Qwen2.5-1.5B/3B hoặc Gemma-2-2B).
- `evaluate.py`: bảng Base vs Fine-tuned (§9.6) — **số thật**.
- Đem adapter về `backend/data/adapters/`.
- **DoD:** adapter load được; fine-tuned ≥ base ở JSON-valid % và format %; có bảng số liệu cho báo cáo.

### PHASE 9 — Tích hợp AI Quiz Generator
- `model_manager.py` nạp base + adapter (hoặc chỉ base nếu `LORA_ADAPTER_PATH` rỗng).
- `quiz_generator.py`: context (lesson + RAG chunks) → prompt → model → parse+repair+validate → preview.
- Endpoints `/api/ai/generate-quiz` (preview, **không lưu**), `/api/ai/quiz/approve` (lưu sau khi giáo viên chỉnh/duyệt).
- Frontend: `AiQuizGenerator.jsx` (§24: chọn course/lesson/số câu/độ khó → Generate → sửa từng câu → Approve & Save).
- **DoD:** quiz sinh ra preview đúng schema; giáo viên duyệt → xuất hiện trong `Quizzes.jsx` như quiz thường; quiz JSON hỏng **không** vào DB.

### PHASE 10 — Hoàn thiện UI/UX
- Áp phong cách EdTech (§25): Inter, Indigo/Slate, `lucide-react`, responsive; bỏ gradient/neon thừa.
- Ẩn/loại menu Admin khỏi điều hướng chính (giữ code).
- **DoD:** 3 màn hình AI + Dashboard/Analytics gọn, đồng nhất, chạy tốt mobile/desktop.

### PHASE 11 — Testing
- Backend: `pytest` (auth, RBAC, LMS CRUD, side effects, analytics, recommendation, AI endpoints với model mock).
- AI eval: RAG hit@k + relevance; QuizGen JSON-valid/format/relevance/duplicate; bảng Base vs Fine-tuned.
- Frontend: smoke test thủ công theo checklist; (tuỳ chọn) Playwright cho luồng chính.
- **DoD:** tất cả test xanh; số liệu eval AI ghi vào `docs/`.

### PHASE 12 — Documentation + Deployment
- Viết `docs/architecture.md`, `rag.md`, `fine-tuning.md`, `recommendation.md`, `api.md`.
- `README.md` mới (chạy FastAPI + frontend + AI, biến `.env`).
- Deploy: Uvicorn/Gunicorn + Nginx (hoặc Docker Compose: api + mysql + chroma), frontend build tĩnh.
- Xoá `legacy-*` nếu chưa xoá; dọn `.gitignore`.
- **DoD:** clone máy mới → theo README → chạy được toàn bộ; tài liệu đủ cho báo cáo & bảo vệ.

---

## PHỤ LỤC A — Lệnh dựng lại hệ thống hiện tại (baseline, đã kiểm chứng 2026-09-06)

```powershell
# 1. MySQL (service MySQL84, cổng 3306, root không mật khẩu trên máy dev này)
net start MySQL84                      # cần quyền admin
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -e "source F:/studyonline-main/studyonline-main/database/studyonline_db.sql"
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -e "source F:/studyonline-main/studyonline-main/database/migration_add_payments.sql"
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -e "source F:/studyonline-main/studyonline-main/database/sample_data.sql"

# 2. Backend PHP (tạm cổng 8001 vì 8000 bị chiếm); sửa backend/.env: DB_PORT=3306
cd F:\studyonline-main\studyonline-main\backend ; php -S 127.0.0.1:8001 -t public

# 3. Frontend; sửa frontend/.env: VITE_API_BASE_URL=http://127.0.0.1:8001
cd F:\studyonline-main\studyonline-main\frontend ; npm install ; npm run dev   # http://localhost:5173
```

Tài khoản (mật khẩu chung `123456`): admin `admin@gmail.com` · teacher `an.nguyen@studyonline.vn`, `binh.tran@studyonline.vn` · student `em.hoang@gmail.com`, `phuong.vu@gmail.com`.

## PHỤ LỤC B — Bảng mới cần tạo (tóm tắt cột)

| Bảng | Cột |
|---|---|
| `documents` | id, course_id→courses, lesson_id→lessons NULL, uploaded_by→users, filename, file_path, file_type(pdf/docx/txt), status(pending/indexed/failed), pages INT NULL, created_at |
| `document_chunks` | id, document_id→documents, course_id, lesson_id NULL, chunk_index, page INT NULL, content TEXT, token_count INT, embedding_id VARCHAR (id trong Chroma), created_at |
| `ai_conversations` | id, user_id→users, course_id→courses, lesson_id NULL, title, created_at, updated_at |
| `ai_messages` | id, conversation_id→ai_conversations, role(user/assistant), content TEXT, sources JSON NULL, created_at |
| `recommendations` | id, user_id→users, course_id→courses, topic VARCHAR NULL, level(Weak/Average/Good/Excellent), items JSON, based_on JSON, created_at |
| `learning_analytics` | id, user_id→users, course_id→courses, avg_quiz_score DECIMAL, completion_pct DECIMAL, completed_lessons INT, total_time_sec INT, quiz_attempts INT, weak_topics JSON, strong_topics JSON, computed_at |

| Bảng cũ | Cột thêm (nullable, additive) |
|---|---|
| `questions` | `topic VARCHAR(100) NULL`, `difficulty ENUM('easy','medium','hard') NULL`, `explanation TEXT NULL` |
| `quizzes` | `lesson_id INT NULL` + FK→lessons (AI sinh quiz theo bài học); `source ENUM('manual','ai') DEFAULT 'manual'` |
| `results` | (tuỳ chọn) `quiz_attempt INT` để đánh số lần làm — hoặc suy ra từ `submit_time` |

---

*Hết PHASE 1. Chờ duyệt trước khi bắt đầu PHASE 2 (code).*
