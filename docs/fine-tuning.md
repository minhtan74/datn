# Fine-tuning — AI Quiz Generator

**Mục tiêu:** KHÔNG dạy model kiến thức mới, mà dạy model **xuất Quiz đúng định dạng
JSON của StudyOnline** — ổn định, ít lỗi parse, câu hỏi bám ngữ cảnh bài học.

Mã nguồn: `backend/training/`.

---

## 1. Dataset

```
training/dataset/
├── qa_bank.jsonl        # 42 cặp Q&A biên soạn tay (context/topic/difficulty/explanation)
├── train.jsonl          # ~243  (prepare_dataset.py sinh ra)
├── validation.jsonl     # ~30
└── test.jsonl           # ~30   (giữ riêng để so Base vs Fine-tuned)
```

`prepare_dataset.py` sinh dữ liệu từ:
1. `qa_bank.jsonl` — 42 câu phủ 8 lĩnh vực (Python, JavaScript, HTML, CSS, Java, React, SQL, HTTP)
2. 30 câu hỏi thật trong `studyonline_db` — gộp theo quiz

**Augmentation:** 10 mẫu câu lệnh (instruction) khác nhau · gộp câu theo *chủ đề hẹp*
và *lĩnh vực rộng* · số câu yêu cầu 1–5 · khử trùng theo `(instruction, output)`.
Kết quả: **303 ví dụ** (train 243 / val 30 / test 30).

Mỗi dòng:

```json
{
  "instruction": "Tạo 3 câu hỏi trắc nghiệm mức trung bình về \"JavaScript\"...",
  "input": "<đoạn tài liệu / nội dung bài học>",
  "output": "{\"questions\":[{\"question\":\"...\",\"options\":{\"A\":\"...\",\"B\":\"...\",\"C\":\"...\",\"D\":\"...\"},\"correct_answer\":\"B\",\"explanation\":\"...\",\"difficulty\":\"medium\",\"topic\":\"...\"}]}"
}
```

Mở rộng dataset = thêm dòng vào `qa_bank.jsonl` rồi chạy lại `prepare_dataset.py`.

## 2. Base model

Ưu tiên model nhỏ hợp GPU Colab (T4/A100):
`Qwen/Qwen2.5-1.5B-Instruct` (mặc định), `Qwen/Qwen2.5-3B-Instruct`, `google/gemma-2-2b-it`.
Đổi bằng `--base_model` hoặc `BASE_MODEL` trong môi trường.

## 3. Kỹ thuật: QLoRA (PEFT + TRL)

`train_lora.py`:
- Nạp base model **4-bit NF4** (BitsAndBytes) → tiết kiệm VRAM.
- LoRA adapter: `r=16`, `alpha=32`, `dropout=0.05`,
  `target_modules = [q,k,v,o,gate,up,down]_proj`.
- `SFTTrainer` (TRL), 3 epoch, lr 2e-4, cosine schedule, `max_seq_length=1536`.
- Chỉ ~0.5–1% tham số được cập nhật → adapter chỉ vài chục MB.

```python
# Google Colab
!pip install -q "transformers>=4.44" "peft>=0.13" "trl>=0.11" "bitsandbytes>=0.44" "accelerate>=0.34" "datasets>=3.0"
!python train_lora.py --base_model Qwen/Qwen2.5-1.5B-Instruct --out ./adapters/quizgen-lora --epochs 3
```

## 4. Pipeline

```
Course Docs / Lessons / 30 câu hỏi DB
        │  prepare_dataset.py
        ▼
train / validation / test (.jsonl)
        │
        ▼
Base model  ──►  QLoRA (train_lora.py, trên Colab)  ──►  LoRA adapter (~vài chục MB)
        │                                                        │
        │  evaluate.py  (so Base vs Fine-tuned trên test.jsonl)   │
        ▼                                                        ▼
    Bảng số liệu                                    copy adapter → backend/data/adapters/
                                                    .env: LORA_ADAPTER_PATH=./data/adapters/quizgen-lora
                                                          BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct
```

> **Backend production KHÔNG chạy fine-tuning.** Nếu chưa có adapter, để
> `LORA_ADAPTER_PATH` trống — AI Quiz Generator vẫn chạy bằng LLM API (Gemini/OpenAI)
> hoặc fallback heuristic *điền chỗ trống*.

## 5. Đánh giá (`evaluate.py`)

Chấm `test.jsonl`, đo:

| Chỉ số | Ý nghĩa |
|---|---|
| **JSON hợp lệ (%)** | output parse được thành JSON |
| **Đúng schema (%)** | có `questions[]`, mỗi câu đủ `question` / `options{A,B,C,D}` / `correct_answer ∈ {A,B,C,D}` |
| **Đáp án hợp lệ (%)** | `correct_answer` trỏ tới option không rỗng |
| **Không trùng câu (%)** | trong một đề không có 2 câu hỏi giống nhau |
| **Khớp số câu (%)** | số câu trả về đúng số câu được yêu cầu |

```bash
python evaluate.py --provider hf --model Qwen/Qwen2.5-1.5B-Instruct                                  --label base
python evaluate.py --provider hf --model Qwen/Qwen2.5-1.5B-Instruct --adapter ./adapters/quizgen-lora --label finetuned
# hoặc chấm nhanh không cần GPU:
python evaluate.py --provider gemini --model gemini-3.1-flash-lite --label gemini   # cần LLM_API_KEY
```

Bảng kết quả (điền số đo thật từ `eval_*.json`):

| Chỉ số | Base | Fine-tuned |
|---|---|---|
| JSON hợp lệ (%) | _đo_ | _đo_ |
| Đúng schema (%) | _đo_ | _đo_ |
| Đáp án hợp lệ (%) | _đo_ | _đo_ |
| Không trùng câu (%) | _đo_ | _đo_ |
| Khớp số câu (%) | _đo_ | _đo_ |

*Kỳ vọng:* fine-tuned cải thiện rõ ở **JSON hợp lệ** và **đúng schema** (model học được
đúng khuôn output), còn độ chính xác nội dung phụ thuộc base model + ngữ liệu.
