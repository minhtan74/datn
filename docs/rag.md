# RAG — AI Tutor

Trợ giảng AI trả lời câu hỏi của học viên **chỉ dựa trên tài liệu của khóa học**,
luôn kèm **trích dẫn nguồn**, và **từ chối** khi không đủ ngữ cảnh (không bịa).

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
| POST | `/api/ai/chat` | `{course_id, lesson_id?, conversation_id?, message}` → `{answer, sources, conversation_id}` |
| GET | `/api/ai/conversations?course_id=` | hội thoại của người dùng |
| GET | `/api/ai/conversations/{id}` | các tin nhắn |
| DELETE | `/api/ai/conversations/{id}` | xoá hội thoại |
| GET | `/api/ai/status` | provider LLM + model embedding đang dùng |

## 4. Metadata & lọc theo khóa

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
