"""PHASE 8 — Fine-tune AI Quiz Generator bằng LoRA / QLoRA (PEFT + TRL).

Mục tiêu: dạy model xuất Quiz ĐÚNG ĐỊNH DẠNG JSON của StudyOnline (không dạy kiến
thức mới). Chạy trên Google Colab (GPU T4 đủ cho QLoRA 4-bit với model ~1.5B–3B).

    # trên Colab:
    !pip install -q "transformers>=4.44" "peft>=0.13" "trl>=0.11" "bitsandbytes>=0.44" \
                    "accelerate>=0.34" "datasets>=3.0"
    !python train_lora.py --base_model Qwen/Qwen2.5-1.5B-Instruct \
                          --out ./adapters/quizgen-lora --epochs 3

Sau khi train xong: copy thư mục adapter về backend, đặt LORA_ADAPTER_PATH trong .env.
"""
from __future__ import annotations

import argparse
import json
import os

SYSTEM_PROMPT = (
    "Bạn là công cụ sinh đề trắc nghiệm của StudyOnline. Luôn trả về DUY NHẤT một "
    "đối tượng JSON hợp lệ theo schema: "
    '{"questions":[{"question","options":{"A","B","C","D"},"correct_answer","explanation","difficulty","topic"}]}. '
    "Không thêm chữ nào ngoài JSON."
)

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "dataset")


def _format(example: dict) -> str:
    return (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"<|user|>\nHướng dẫn: {example['instruction']}\n\nNgữ liệu:\n{example['input']}\n"
        f"<|assistant|>\n{example['output']}"
    )


def load_split(name: str):
    from datasets import Dataset

    rows = []
    with open(os.path.join(DS, f"{name}.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ex = json.loads(line)
                rows.append({"text": _format(ex)})
    return Dataset.from_list(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", default=os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-1.5B-Instruct"))
    ap.add_argument("--out", default=os.environ.get("LORA_ADAPTER_PATH", "./adapters/quizgen-lora"))
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--grad_accum", type=int, default=8)
    ap.add_argument("--max_len", type=int, default=1536)
    ap.add_argument("--no_4bit", action="store_true", help="Tắt QLoRA 4-bit (dùng LoRA thường)")
    args = ap.parse_args()

    import torch
    from peft import LoraConfig
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
    )
    from trl import SFTConfig, SFTTrainer

    tok = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    quant = None
    if not args.no_4bit:
        quant = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=quant,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )

    peft_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    sft_cfg = SFTConfig(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch",
        bf16=True,
        max_seq_length=args.max_len,
        dataset_text_field="text",
        packing=False,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_cfg,
        train_dataset=load_split("train"),
        eval_dataset=load_split("validation"),
        peft_config=peft_cfg,
        processing_class=tok,
    )
    trainer.train()
    trainer.save_model(args.out)
    tok.save_pretrained(args.out)
    print(f"\n✔ Đã lưu LoRA adapter vào: {args.out}")
    print("  → Copy thư mục này về backend rồi đặt LORA_ADAPTER_PATH trong backend/.env")


if __name__ == "__main__":
    main()
