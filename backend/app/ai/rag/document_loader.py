"""Trích xuất văn bản từ PDF / DOCX / TXT (giữ số trang nếu có)."""
from __future__ import annotations

import re

# Ký tự điều khiển (C0 + DEL) — pypdf đôi khi giải mã glyph bullet ("•") của PDF
# thành các byte này thay vì ký tự đọc được, làm nhiễu cả nội dung lẫn điểm truy hồi.
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


# Làm sạch văn bản: bỏ ký tự điều khiển, gộp khoảng trắng thừa, tối đa 1 dòng trống liên tiếp
def _clean(text: str) -> str:
    text = _CTRL.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Chọn hàm trích xuất theo loại file
def extract(path: str, file_type: str) -> tuple[list[tuple[int | None, str]], int | None]:
    """Trả về (list[(page_no|None, text)], tổng_số_trang|None)."""
    ft = file_type.lower()
    if ft == "pdf":
        return _extract_pdf(path)
    if ft == "docx":
        return _extract_docx(path)
    return _extract_txt(path)


# PDF: đọc từng trang bằng pypdf, giữ số trang để trích dẫn nguồn; trang lỗi / không có chữ thì bỏ qua
def _extract_pdf(path: str):
    from pypdf import PdfReader

    reader = PdfReader(path)
    out: list[tuple[int | None, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            txt = _clean(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            txt = ""
        if txt:
            out.append((i, txt))
    return out, len(reader.pages)


# DOCX: lấy các đoạn văn và nội dung bảng (các ô nối bằng " | "); DOCX không có khái niệm trang
def _extract_docx(path: str):
    import docx

    doc = docx.Document(path)
    parts = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    text = _clean("\n".join(parts))
    return ([(None, text)] if text else []), None


# TXT/MD: đọc toàn bộ file, ký tự lỗi mã hóa được thay thế thay vì báo lỗi
def _extract_txt(path: str):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = _clean(f.read())
    return ([(None, text)] if text else []), None
