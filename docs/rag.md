# RAG — AI Tutor

Trợ giảng AI trả lời câu hỏi của học viên **chỉ dựa trên tài liệu của khóa học**,
kèm **trích dẫn nguồn** cho nội dung trả lời từ tài liệu. Câu hỏi thiếu thông tin sẽ được hỏi lại;
câu hỏi đã rõ nhưng không có tài liệu phù hợp vẫn bị **từ chối**, không bịa.

Mã nguồn: `backend/app/ai/rag/` + `backend/app/ai/tutor.py` + `backend/app/routers/ai.py`.

---

## 1. Pipeline nạp tài liệu (ingest)

```
Tài liệu (PDF / DOCX / TXT)               documents (MySQL): status = pending
        │  document_loader.extract()
        ▼
[(số trang, văn bản)]  ──► làm sạch (bỏ ký tự rác, chuẩn hoá khoảng trắng, bỏ dòng "TÀI LIỆU:")
        │  text_splitter.split_pages()
        ▼
chunks ~380 ký tự, tách theo mục đánh số ("1. ", "2. "…) và câu, overlap ~60
        │  embeddings.embed_texts()   (fastembed / ONNX, model đa ngữ 384 chiều)
        ▼
vectors[]  ──► vector_store.add_chunks()
        ▼
document_chunks (MySQL): document_id, course_id, lesson_id, chunk_index, page,
                          content, embedding (JSON mảng 384 số), token_count
        │
        ▼
documents.status = indexed,  pages = N,  chunk_count = M
```

- **Loader**: `pypdf` (giữ số trang), `python-docx` (đoạn + bảng), TXT/MD đọc trực tiếp.
- **Splitter**: mỗi mục đánh số ≈ một chunk → truy hồi chính xác tới đúng đoạn.
- **Embedding**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  (đổi qua `EMBEDDING_MODEL` trong `.env`). Nạp lười ở lần gọi đầu.

## 2. Pipeline trả lời (query)

```
Câu hỏi
   │  clarification: thiếu chủ đề/code/đề bài/đối tượng so sánh?
   ├── Có, lịch sử chưa làm rõ → hỏi ngắn về thông tin còn thiếu; không truy hồi, không gắn nguồn
   ▼ (đã rõ, hoặc có chủ đề từ các lượt trước)
   │  embeddings.embed_query()
   ▼
vector câu hỏi
   │  vector_store.search()  — cosine similarity trên chunk của khóa (+lọc lesson nếu có)
   ▼
pool top (k×3)
   │  retriever: re-rank LAI = 0.55·cosine + 0.45·(trùng từ khóa)
   ▼
top-k chunk  (k = AI_MAX_CONTEXT_CHUNKS, mặc định 6)
   │
   ├── cosine tốt nhất < 0.55  ──►  "Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."
   │
   ▼ (đủ liên quan)
NGỮ CẢNH = ghép các chunk, gắn nhãn [Nguồn i] Tên tài liệu (trang X)
   │
   ├── Có LLM_API_KEY  →  prompt SYSTEM (ràng buộc "chỉ dùng ngữ cảnh, không bịa")
   │                       + lịch sử 4 lượt gần nhất + ngữ cảnh + câu hỏi  →  Gemini/OpenAI
   │
   └── Không có LLM    →  extractive: chấm điểm từng CÂU trong ngữ cảnh
                          (0.4·cosine + 0.6·trùng từ khóa), lấy 2 câu tốt nhất theo thứ tự
   ▼
{ answer, sources: [{document, page, score}] }   (nguồn = top-3 theo hybrid, khử trùng)
   │
   ▼
Lưu ai_messages (role=user) + ai_messages (role=assistant, sources JSON)
Cập nhật ai_conversations.updated_at; đặt title từ câu hỏi đầu tiên
```

## 3. API

| Method | Path | Mô tả |
|---|---|---|
| POST | `/api/ai/documents` | (GV) multipart `file` + `course_id` + `lesson_id?` + `title?` → tải + ingest đồng bộ |
| GET | `/api/ai/documents?course_id=` | (GV) danh sách + trạng thái + `chunk_count` |
| DELETE | `/api/ai/documents?id=` | (GV) xoá tài liệu (chunk cascade) + xoá file |
| POST | `/api/ai/chat` | `{course_id, lesson_id?, conversation_id?, message}` → `{answer, sources, conversation_id, used_context, needs_clarification, clarification_kind}` |
| GET | `/api/ai/conversations?course_id=` | hội thoại của người dùng |
| GET | `/api/ai/conversations/{id}` | các tin nhắn |
| DELETE | `/api/ai/conversations/{id}` | xoá hội thoại |
| GET | `/api/ai/status` | provider LLM + model embedding đang dùng |

## 4. Metadata & lọc theo khóa

Câu hỏi mơ hồ phổ biến (có dấu/không dấu) được nhận diện trước truy hồi bằng
`backend/app/ai/rag/clarification.py`; LLM cũng được hướng dẫn hỏi thêm tối đa hai câu khi còn thiếu dữ liệu.
“HTTP là gì?”, “SQL JOIN”, hoặc câu hỏi rõ khác vẫn đi vào RAG trực tiếp.
Một câu hỏi về hành vi API hoặc phân biệt khái niệm không bị coi là yêu cầu sửa code chỉ vì có từ “báo lỗi/sửa lỗi”.
Các đại từ được xét cùng đối tượng đã nêu ngay trong câu hỏi, không chỉ dựa vào lịch sử.
Từ tiếng Anh `this`/`that` được nhận diện trên văn bản gốc, tránh việc bỏ dấu biến “thật” thành `that`.
“Cho ví dụ đi” sau một chủ đề đã trả lời dùng lại chủ đề đó, kể cả qua nhiều lượt nối tiếp.
Khi người học bổ sung chủ đề sau lời hỏi lại, truy vấn giữ cả mục đích ban đầu và nội dung bổ sung.
Đổi sang câu mới đã rõ sẽ không bị ghép chủ đề cũ.

Lời hỏi lại có `needs_clarification=true`, `clarification_kind` (topic/debug/exercise/comparison/context),
`sources=[]`, `used_context=false`. Lịch sử giữ cờ hỏi lại trong JSON `ai_messages.sources`
dưới dạng `{response_type:"clarification", clarification_kind:"..."}`; API đọc lại thành cờ và mảng nguồn rỗng.
Tin nhắn trả lời thông thường tiếp tục lưu mảng nguồn như trước, không cần migration.
Hội thoại phải cùng khóa và cùng phạm vi bài học; không dùng lịch sử phạm vi khác để đoán ý câu hỏi.
Tài liệu bài học chỉ được nạp sau khi câu hỏi đã đủ thông tin.

Kiểm tra bản sửa hỏi lại thừa: [3 ca hồi quy có trả lời bằng nguồn thật, 6 ca vẫn cần làm rõ](ai-clarification-specificity-results.json).
Kiểm tra phân loại trên 50 câu kiến thức không thay thế việc đo lại độ chính xác nội dung của cả 50 câu.

### Chờ phản hồi và xử lý lỗi

Trang AI Tutor và khung AI bài học dùng chung `useAiChat` và `AiChatFeedback`:

- Giới hạn chờ phía trình duyệt là 120 giây, có bộ đếm; sau 15/45 giây thông báo rõ rằng vẫn đang xử lý/chờ lâu.
- **Dừng chờ** hủy việc chờ ở trình duyệt và bỏ qua phản hồi cũ khi đổi khóa/bài. Tác vụ đã nhận ở máy chủ có thể vẫn hoàn tất và lưu lịch sử; giao diện có giải thích điều này.
- Lỗi mạng/timeout/dịch vụ có vùng thông báo riêng, giữ câu hỏi trên trang để **Thử lại** hoặc **Sửa câu hỏi**. Không tự gửi lại nhiều lần.
- Khi đã nhận `conversation_id`, thử lại giữ đúng hội thoại và phạm vi bài học. Lượt gửi lại được lưu là một lần gửi mới ở máy chủ; không hứa hủy hoặc gộp tác vụ đã chạy trước đó.
- Lỗi LLM không có trích xuất dự phòng trả HTTP503, `success=false`, kèm `data` có `conversation_id`, `response_status="error"`, `error_code="ai_unavailable"`, `retryable=true`.
- Trích xuất dự phòng vẫn trả HTTP200 và nguồn, nhưng có `response_status="fallback"` để phân biệt với câu trả lời LLM.
- Metadata lỗi/dự phòng được lưu trong JSON `ai_messages.sources` (`response_type`, `sources`, `error_code`, `retryable`), đọc lại thành các trường API và mảng nguồn. Lịch sử lỗi kiểu cũ được hiển thị bằng thông báo phù hợp, không lộ chuỗi lỗi kỹ thuật.

Kiểm tra: [25 ca trình duyệt](ai-wait-feedback-check.json). Các ca chậm/lỗi/timeout được giả lập có kiểm soát; không dùng chúng để tính độ chính xác kiến thức của AI.

Mỗi chunk lưu `course_id` và `lesson_id`. Truy vấn `vector_store._load()` chỉ lấy
chunk của đúng khóa học (và `lesson_id = X OR NULL` khi hỏi trong phạm vi một bài),
đảm bảo AI **không rò rỉ** nội dung khóa khác.

## 5. Đánh giá RAG (đưa vào báo cáo)

Tạo tập kiểm thử `[{câu hỏi, tài liệu kỳ vọng, chủ đề kỳ vọng}]` (~20–40 câu), đo:

| Chỉ số | Cách đo |
|---|---|
| **Retrieval hit@k** | tài liệu đúng có nằm trong top-k chunk không |
| **Answer relevance** | chấm tay 1–5 (hoặc LLM-as-judge) |
| **Source correctness** | nguồn trích dẫn có khớp tài liệu chứa đáp án không |
| **Tỷ lệ từ chối đúng** | câu hỏi ngoài phạm vi → trả đúng câu từ chối |

Ví dụ kết quả với dữ liệu mẫu (3 tài liệu, 21 chunk):

| Câu hỏi | Kết quả |
|---|---|
| "HTTP là gì / có phi trạng thái không?" | ✓ trả lời + nguồn "HTTP và Nền Tảng Web" |
| "Promise có những trạng thái nào?" | ✓ "pending, fulfilled, rejected" + nguồn |
| "typeof null trả về gì?" | ✓ "'object' (lỗi lịch sử)" + nguồn |
| "Cách trồng lúa nước?" (ngoài phạm vi) | ✓ "Tôi không tìm thấy thông tin phù hợp…" |

## 6. Cấu hình (`backend/.env`)

```
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
AI_MAX_CONTEXT_CHUNKS=6
LLM_PROVIDER=gemini            # gemini | openai | claude | (bỏ trống → offline)
LLM_MODEL=gemini-3.1-flash-lite
LLM_API_KEY=
LLM_BASE_URL=                  # chỉ với openai: API cùng chuẩn, vd. Ollama http://localhost:11434/v1
```
