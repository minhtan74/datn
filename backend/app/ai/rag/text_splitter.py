"""Chia văn bản thành chunk nhỏ (~350 ký tự) để truy hồi chính xác.

Ưu tiên tách theo mục đánh số ("1. ", "2. "...) và đoạn văn, sau đó gộp/cắt về
kích thước mục tiêu với phần chồng lấn nhỏ.
"""
from __future__ import annotations

import re

# Kích thước mục tiêu mỗi đoạn (ký tự) và phần chồng lấn giữa 2 đoạn liên tiếp (giữ mạch ý khi bị cắt)
CHUNK_SIZE = 380
OVERLAP = 60

# Mẫu nhận diện đầu mục đánh số ("1. Tiêu đề", "2) ...") để tách theo mục
_SECTION = re.compile(r"\n(?=\d{1,2}[.)]\s+[A-ZÀ-Ỹ])")
# Mẫu tách câu: sau dấu . ! ? … hoặc tại dòng trống
_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+|\n{2,}")


# Chia toàn bộ tài liệu thành đoạn, đánh số thứ tự liên tục và giữ số trang của từng đoạn
def split_pages(pages: list[tuple[int | None, str]]) -> list[dict]:
    chunks: list[dict] = []
    idx = 0
    for page_no, text in pages:
        for piece in _split_one(text):
            chunks.append({"index": idx, "page": page_no, "text": piece})
            idx += 1
    return chunks


# Phần "Bài tập vận dụng" ở cuối bài học: đề bài lặp lại đúng từ khoá của kiến thức nên khi tìm kiếm dễ được chọn
# thay cho phần giải thích, mà bản thân đề bài không phải kiến thức -> cắt bỏ từ tiêu đề này tới hết trang
_EXERCISES = re.compile(r"^[ \t]*Bài tập vận dụng\b.*\Z", re.IGNORECASE | re.MULTILINE | re.DOTALL)


# Chia 1 trang: tách theo mục đánh số; mục ngắn giữ nguyên, mục dài thì gom câu thành đoạn; bỏ đoạn < 40 ký tự
def _split_one(text: str) -> list[str]:
    text = _EXERCISES.sub("", text).strip()
    if not text:
        return []

    units: list[str] = []
    for section in _SECTION.split(text):
        section = _strip_doc_heading(section).strip()
        if not section:
            continue
        if len(section) <= CHUNK_SIZE:
            units.append(section)
        else:
            units.extend(_pack_sentences(section))
    return [u for u in units if len(u) >= 40]


def _strip_doc_heading(section: str) -> str:
    """Bỏ dòng tiêu đề dạng 'TÀI LIỆU: ...' ở đầu tài liệu (không mang nội dung)."""
    lines = section.split("\n")
    if lines and re.match(r"^\s*(TÀI LIỆU|TAI LIEU|DOCUMENT)\s*[:：]", lines[0], re.IGNORECASE):
        lines = lines[1:]
    return "\n".join(lines)


def _word_safe_tail(text: str, max_chars: int) -> str:
    """Lấy tối đa max_chars ký tự cuối của text, cắt tại ranh giới khoảng trắng
    gần nhất (không cắt giữa một từ) — tránh sinh chunk overlap bắt đầu bằng
    một từ bị mất ký tự đầu (VD "những" -> "hững")."""
    if len(text) <= max_chars:
        return text
    tail = text[-max_chars:]
    sp = tail.find(" ")
    return tail[sp + 1 :] if sp != -1 else tail


# Gom các câu liên tiếp vào đoạn cho tới khi đủ CHUNK_SIZE; đoạn mới bắt đầu bằng phần đuôi của đoạn trước (overlap)
def _pack_sentences(text: str) -> list[str]:
    sents = [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]
    out: list[str] = []
    buf = ""
    for s in sents:
        # Câu quá dài: cắt cứng theo cửa sổ trượt CHUNK_SIZE, bước nhảy CHUNK_SIZE - OVERLAP
        if len(s) > CHUNK_SIZE:
            if buf:
                out.append(buf.strip())
                buf = ""
            for i in range(0, len(s), CHUNK_SIZE - OVERLAP):
                out.append(s[i : i + CHUNK_SIZE].strip())
            continue
        if len(buf) + len(s) + 1 <= CHUNK_SIZE:
            buf = f"{buf} {s}".strip()
        else:
            if buf:
                out.append(buf.strip())
            tail = _word_safe_tail(buf, OVERLAP) if len(buf) > OVERLAP else ""
            buf = f"{tail} {s}".strip()
    if buf.strip():
        out.append(buf.strip())
    return out


# Ước lượng số token (~4 ký tự / token)
def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)
