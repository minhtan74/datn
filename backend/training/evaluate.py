"""PHASE 8 — Đánh giá AI Quiz Generator trên training/dataset/test.jsonl.

Đo (số liệu thật, không tự bịa):
  - JSON hợp lệ (%)            : output parse được thành JSON
  - Đúng schema (%)            : có questions[], mỗi câu đủ question/options{A,B,C,D}/correct_answer∈ABCD
  - Đáp án hợp lệ (%)          : correct_answer trỏ tới option không rỗng
  - Không trùng câu hỏi (%)    : trong 1 đề không có 2 câu hỏi giống nhau
  - Sát số lượng yêu cầu (%)   : số câu trả về khớp số câu được yêu cầu

Cách dùng (so sánh Base vs Fine-tuned trên Colab):
    python evaluate.py --provider hf --model Qwen/Qwen2.5-1.5B-Instruct                 --label base
    python evaluate.py --provider hf --model Qwen/Qwen2.5-1.5B-Instruct --adapter ./adapters/quizgen-lora --label finetuned
Hoặc chấm nhanh bằng Gemini (không cần GPU):
    set LLM_API_KEY=...  &&  python evaluate.py --provider gemini --model gemini-2.0-flash --label gemini
"""
from __future__ import annotations

import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "dataset")
SYSTEM = (
    "Bạn là công cụ sinh đề trắc nghiệm của StudyOnline. Trả về DUY NHẤT một JSON hợp lệ "
    'schema {"questions":[{"question","options":{"A","B","C","D"},"correct_answer","explanation","difficulty","topic"}]}.'
)


# ── các bộ sinh output ──────────────────────────────────────────────────────

def gen_hf(model_name: str, adapter: str | None):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
    )
    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter)
    model.eval()

    def _run(instruction: str, context: str) -> str:
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Hướng dẫn: {instruction}\n\nNgữ liệu:\n{context}"},
        ]
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        ids = tok(prompt, return_tensors="pt").to(model.device)
        out = model.generate(**ids, max_new_tokens=900, do_sample=False, temperature=None, top_p=None)
        return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)

    return _run


def gen_gemini(model_name: str):
    import httpx

    key = os.environ.get("LLM_API_KEY", "").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"

    def _run(instruction: str, context: str) -> str:
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": f"Hướng dẫn: {instruction}\n\nNgữ liệu:\n{context}"}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 900},
        }
        r = httpx.post(url, json=payload, timeout=90)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    return _run


# ── phân tích & chấm ───────────────────────────────────────────────────────

def extract_json(text: str) -> dict | None:
    text = text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def wanted_count(instruction: str) -> int | None:
    m = re.search(r"(\d+)\s*câu", instruction)
    return int(m.group(1)) if m else None


def score(items: list[dict]) -> dict:
    n = len(items)
    js_ok = schema_ok = ans_ok = nodup_ok = count_ok = 0
    for it in items:
        data = extract_json(it["raw"])
        if data is None:
            continue
        js_ok += 1
        qs = data.get("questions")
        if not isinstance(qs, list) or not qs:
            continue
        ok_schema = all(
            isinstance(q, dict)
            and q.get("question")
            and isinstance(q.get("options"), dict)
            and set(q["options"]) >= {"A", "B", "C", "D"}
            and q.get("correct_answer") in {"A", "B", "C", "D"}
            for q in qs
        )
        if ok_schema:
            schema_ok += 1
            if all(str(q["options"].get(q["correct_answer"], "")).strip() for q in qs):
                ans_ok += 1
            texts = [str(q["question"]).strip().lower() for q in qs]
            if len(texts) == len(set(texts)):
                nodup_ok += 1
        want = wanted_count(it["instruction"])
        if want and isinstance(qs, list) and len(qs) == want:
            count_ok += 1
    pct = lambda x: round(x * 100 / n, 1) if n else 0.0
    return {
        "n": n,
        "json_valid_%": pct(js_ok),
        "schema_valid_%": pct(schema_ok),
        "answer_valid_%": pct(ans_ok),
        "no_duplicate_%": pct(nodup_ok),
        "count_match_%": pct(count_ok),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["hf", "gemini"], default="gemini")
    ap.add_argument("--model", default=os.environ.get("BASE_MODEL", "gemini-2.0-flash"))
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--label", default="model")
    ap.add_argument("--limit", type=int, default=0, help="Chỉ chấm N ví dụ đầu (0 = tất cả)")
    args = ap.parse_args()

    tests = []
    with open(os.path.join(DS, "test.jsonl"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tests.append(json.loads(line))
    if args.limit:
        tests = tests[: args.limit]

    runner = gen_hf(args.model, args.adapter) if args.provider == "hf" else gen_gemini(args.model)

    results = []
    for i, ex in enumerate(tests, 1):
        raw = runner(ex["instruction"], ex["input"])
        results.append({"instruction": ex["instruction"], "raw": raw})
        print(f"  [{i}/{len(tests)}] done")

    metrics = score(results)
    report = {"label": args.label, "provider": args.provider, "model": args.model,
              "adapter": args.adapter, "metrics": metrics}

    out_path = os.path.join(HERE, f"eval_{args.label}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"report": report, "samples": results[:5]}, f, ensure_ascii=False, indent=2)

    print("\n| Metric | Giá trị |")
    print("|---|---|")
    for k, v in metrics.items():
        print(f"| {k} | {v} |")
    print(f"\nĐã lưu: {out_path}")


if __name__ == "__main__":
    main()
