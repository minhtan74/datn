# Fine-tuning AI Quiz Generator (Phase 7–8)

Mục tiêu **không** phải dạy model kiến thức mới, mà dạy nó **xuất Quiz đúng định dạng
JSON của StudyOnline** (ổn định, ít lỗi parse, câu hỏi bám ngữ cảnh).

```
training/
├── dataset/
│   ├── qa_bank.jsonl        # 42 cặp Q&A biên soạn tay (context/topic/difficulty/explanation)
│   ├── train.jsonl          # sinh ra bởi prepare_dataset.py  (~243)
│   ├── validation.jsonl     # ~30
│   └── test.jsonl           # ~30  (giữ riêng để so Base vs Fine-tuned)
├── prepare_dataset.py       # qa_bank + 30 câu hỏi trong DB  ->  instruction/input/output + augmentation
├── train_lora.py            # QLoRA (PEFT + TRL) — chạy trên Colab
├── evaluate.py              # chấm test.jsonl: JSON valid %, schema %, đáp án %, trùng lặp %, khớp số câu %
├── seed_documents.py        # (RAG) nạp tài liệu mẫu vào AI Tutor
└── seed_result_answers.py   # (demo) sinh result_answers cho các results seed cũ
```

## 1. Tạo dataset

```powershell
cd backend
.\.venv\Scripts\python.exe training\prepare_dataset.py           # cần DB chạy để lấy 30 câu hỏi mẫu
.\.venv\Scripts\python.exe training\prepare_dataset.py --no-db   # chỉ từ qa_bank
```

Mỗi dòng là `{"instruction","input","output"}`, `output` là JSON schema StudyOnline:

```json
{"questions":[{"question":"...","options":{"A":"...","B":"...","C":"...","D":"..."},
  "correct_answer":"B","explanation":"...","difficulty":"medium","topic":"..."}]}
```

Mở rộng dataset = thêm dòng vào `qa_bank.jsonl` rồi chạy lại `prepare_dataset.py`.

## 2. Fine-tune (Google Colab, GPU T4)

```python
!pip install -q "transformers>=4.44" "peft>=0.13" "trl>=0.11" "bitsandbytes>=0.44" "accelerate>=0.34" "datasets>=3.0"
# tải thư mục training/ lên Colab, rồi:
!python train_lora.py --base_model Qwen/Qwen2.5-1.5B-Instruct --out ./adapters/quizgen-lora --epochs 3
```

Base model gợi ý (nhỏ, hợp GPU Colab): `Qwen/Qwen2.5-1.5B-Instruct`, `Qwen/Qwen2.5-3B-Instruct`,
`google/gemma-2-2b-it`. Đổi bằng cờ `--base_model` hoặc biến môi trường `BASE_MODEL`.

Kết quả: thư mục **LoRA adapter** (~vài chục MB). Tải về máy backend, đặt trong
`backend/.env`:

```
BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct
LORA_ADAPTER_PATH=./data/adapters/quizgen-lora
```

> Backend production **không** chạy fine-tuning. Nếu chưa có adapter, để `LORA_ADAPTER_PATH`
> trống — AI Quiz Generator vẫn chạy bằng LLM API (Gemini/OpenAI) hoặc fallback heuristic.

## 3. Đánh giá (số liệu cho báo cáo)

Chạy 2 lần rồi lập bảng so sánh:

```bash
python evaluate.py --provider hf --model Qwen/Qwen2.5-1.5B-Instruct                                  --label base
python evaluate.py --provider hf --model Qwen/Qwen2.5-1.5B-Instruct --adapter ./adapters/quizgen-lora --label finetuned
```

| Metric | Base | Fine-tuned |
|---|---|---|
| JSON hợp lệ (%) | _đo_ | _đo_ |
| Đúng schema (%) | _đo_ | _đo_ |
| Đáp án hợp lệ (%) | _đo_ | _đo_ |
| Không trùng câu hỏi (%) | _đo_ | _đo_ |
| Khớp số câu yêu cầu (%) | _đo_ | _đo_ |

Không có GPU vẫn chấm nhanh được bằng Gemini: `--provider gemini --model gemini-2.0-flash`
(đặt `LLM_API_KEY`).
