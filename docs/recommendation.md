# Learning Analytics & Rule-based Recommendation

Không dùng Machine Learning phức tạp — dùng **rule engine thuần Python** trên số liệu
học tập thật. Mã nguồn: `backend/app/services/analytics_service.py` +
`backend/app/ai/recommendation.py` + router `analytics.py`, `recommendations.py`.

---

## 1. Nguồn dữ liệu

| Bảng | Dùng cho |
|---|---|
| `results` | điểm quiz mỗi lần nộp (score/total), số lần làm quiz, so sánh lần 1 ↔ lần 2 |
| `result_answers` *(mới)* | đúng/sai **từng câu** mỗi lần nộp → tính điểm theo **chủ đề** |
| `lesson_progress` | bài hoàn thành, `watched_sec` → thời gian học, tỷ lệ hoàn thành |
| `questions.topic` *(mới)* | gán chủ đề cho từng câu hỏi (đã backfill 30 câu mẫu) |
| `learning_analytics` *(mới)* | snapshot chỉ số theo user × course (cache) |
| `recommendations` *(mới)* | lưu lịch sử mỗi lần sinh gợi ý |

> `POST /api/quizzes/submit` được bổ sung: ngoài ghi `results`, ghi thêm
> `result_answers` (chosen + is_correct từng câu).

## 2. Learning Analytics — chỉ số

`GET /api/analytics/overview?course_id=` →

```json
{ "avg_quiz_score": 70.0, "level": "Good", "completion_pct": 16.7,
  "completed_lessons": 3, "total_lessons": 18, "total_time_sec": 2020, "quiz_attempts": 2 }
```

`GET /api/analytics/topics?course_id=` → điểm trung bình theo chủ đề (sắp xếp thấp → cao):

```json
{ "data": [
    {"topic":"Vòng lặp (Loops)","answered":1,"correct":0,"avg_score":0.0,"status":"Weak"},
    {"topic":"Kiểu dữ liệu (Data Types)","answered":3,"correct":3,"avg_score":100.0,"status":"Excellent"} ],
  "weak_topics":[...], "strong_topics":[...] }
```

`GET /api/analytics/quiz-progress?quiz_id=` → các lần làm cùng một quiz + `improvement`
(= % lần cuối − % lần đầu) → phục vụ so sánh "Quiz lần 2".

## 3. Phân loại năng lực (thang cố định)

```
điểm quiz trung bình:
  < 50   → Weak       (Yếu)
  50–70  → Average    (Trung bình)
  70–85  → Good       (Khá)
  >= 85  → Excellent  (Tốt)
```

Dùng chung cho cả `analytics_service.level_for()` và rule engine.

## 4. Rule Engine (`recommendation.py`)

**Đầu vào:** overview + topics của học viên (theo khóa hoặc toàn bộ).

**Luật sinh gợi ý (có thứ tự ưu tiên):**

| # | Điều kiện | Gợi ý (kèm link hành động) |
|---|---|---|
| 1 | `completion_pct < 50` | "Hoàn thành các bài học còn lại (X bài chưa xong)" → `/student/my-courses` |
| 2 | có chủ đề `Weak`/`Average` | "Ôn lại chủ đề '<yếu nhất>' — điểm hiện tại Y%" |
| 3 | luôn (nếu tìm được) | "Học bài tiếp theo: '<bài chưa hoàn thành đầu tiên>'" → `/lesson?id=` |
| 4 | có quiz điểm cao nhất < 70 | "Làm lại quiz '<tên>' (điểm cao nhất Z%)" → `/quiz-show?id=` |
| 5 | luôn | lời khuyên theo mức năng lực (Weak/Average/Good/Excellent) |

**Đầu ra:**

```json
{ "level": "Good", "summary": "Tiến độ tốt — học tiếp lộ trình",
  "items": [ {"type":"review_topic","text":"...","topic":"..."},
             {"type":"next_lesson","text":"...","action_url":"/lesson?id=11"}, ... ],
  "based_on": { "avg_quiz_score":70.0, "completion_pct":16.7, "weakest_topic":"...",
                "weak_topics":[...], "strong_topics":[...] } }
```

## 5. API

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/recommendations?course_id=` | gợi ý **tính realtime** từ dữ liệu mới nhất + `history` 10 dòng gần nhất |
| POST | `/api/recommendations/refresh` | tính lại + **LƯU** 1 dòng `recommendations` + cập nhật snapshot `learning_analytics` |

## 6. Vòng lặp cá nhân hoá (điểm nhấn đề tài)

```
Học bài  →  Làm Quiz  →  Lưu results + result_answers
   ↑                              │
   │                              ▼
Học lại  ←  Gợi ý bài học  ←  Xác định chủ đề yếu  ←  Learning Analytics
   │
   ▼
Làm Quiz lần 2  →  /api/analytics/quiz-progress  →  So sánh % lần 1 ↔ lần 2 (improvement)
```

Mỗi lần bấm **"↻ Cập nhật"** trên `RecommendationCard`, hệ thống gọi `/refresh` →
gợi ý **thay đổi theo kết quả học tập mới** và được lưu lại → chứng minh tính động.

## 7. Giao diện

- `student/Progress.jsx`: thẻ **"🧠 Phân tích học tập"** (4 stat tile + thanh điểm từng
  chủ đề Yếu/TB/Khá/Tốt) + thẻ **"🎯 Gợi ý học tập cho bạn"** (có nút Cập nhật).
- `student/Dashboard.jsx`: `RecommendationCard` (rút gọn) ngay dưới ô thống kê.
