"""Dựng PDF tài liệu cho từng bài học từ training/lesson_docs/content/*.md.

    python training/lesson_docs/build_pdfs.py            # dựng mọi bài
    python training/lesson_docs/build_pdfs.py 2 10 54    # chỉ dựng các bài có id này

Mỗi file .md chứa nhiều bài, ngăn cách bằng dòng "=== LESSON <id> ===". Thông tin chương / bài lấy từ lessons.json.
Kết quả: training/lesson_docs/pdf/lesson_<id>.pdf (đã commit sẵn để nạp vào CSDL mà không cần dựng lại).

Dùng Chrome / Edge (headless) để in HTML ra PDF nên tiếng Việt có dấu hiển thị và sao chép / trích xuất văn bản đúng.
Nếu Chrome nằm ở chỗ khác, đặt biến môi trường CHROME_PATH.
"""
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
OUT = os.path.join(HERE, "pdf")

# Các vị trí Chrome / Edge thường gặp (Windows, macOS, Linux)
_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', 'Noto Sans', Arial, sans-serif; color: #0f172a; font-size: 11pt; line-height: 1.55; }
.tag { font-size: 8.5pt; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: #2563eb; }
h1 { font-size: 20pt; margin: 4pt 0 2pt; line-height: 1.25; }
.sub { color: #64748b; margin: 0 0 12pt; font-size: 10pt; }
h2 { font-size: 13pt; margin: 16pt 0 5pt; padding-bottom: 3pt; border-bottom: 1.5px solid #e2e8f0; color: #1e3a8a; page-break-after: avoid; }
p { margin: 5pt 0; }
ul, ol { margin: 4pt 0 6pt; padding-left: 20pt; }
li { margin: 2pt 0; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 9.5pt; background: #eef2ff; padding: 0 3pt; border-radius: 3px; }
pre { background: #0f172a; color: #e2e8f0; padding: 9pt 11pt; border-radius: 7px; font-size: 9pt; line-height: 1.45; overflow-wrap: anywhere; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
.box { border-radius: 8px; padding: 6pt 12pt 8pt; margin: 8pt 0; page-break-inside: avoid; }
.obj { background: #eff6ff; border-left: 4px solid #2563eb; }
.sum { background: #f0fdf4; border-left: 4px solid #16a34a; }
.ex { background: #fffbeb; border-left: 4px solid #d97706; }
.box h2 { border: none; margin: 4pt 0 2pt; padding: 0; color: inherit; }
"""


def find_chrome() -> str:
    for p in _CANDIDATES:
        if p and os.path.isfile(p):
            return p
    sys.exit("Không tìm thấy Chrome/Edge. Đặt biến môi trường CHROME_PATH trỏ tới chrome.exe.")


# Định dạng trong dòng: `mã`, **đậm**, *nghiêng* (đã escape HTML trước)
def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


# Chuyển Markdown đơn giản (## tiêu đề, danh sách -, 1., khối ```) sang HTML; 3 mục đặc biệt được tô khung riêng
def md_to_html(md: str) -> str:
    out, lines, i = [], md.strip("\n").split("\n"), 0
    box_cls, box_open = None, False

    def close_box():
        nonlocal box_open
        if box_open:
            out.append("</div>")
            box_open = False

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
        elif ln.startswith("## "):
            title = ln[3:].strip()
            close_box()
            cls = "obj" if title.startswith("Mục tiêu") else "sum" if title.startswith("Tóm tắt") else "ex" if title.startswith("Bài tập") else None
            if cls:
                out.append(f'<div class="box {cls}">')
                box_open = True
            out.append(f"<h2>{_inline(title)}</h2>")
        elif re.match(r"^- ", ln):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{_inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(f"<li>{_inline(re.sub(r'^\d+\. ', '', lines[i]))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        elif ln.strip():
            out.append(f"<p>{_inline(ln.strip())}</p>")
        i += 1
    close_box()
    return "\n".join(out)


def load_lessons() -> dict[int, str]:
    lessons = {}
    for path in sorted(glob.glob(os.path.join(CONTENT, "*.md"))):
        text = open(path, encoding="utf-8").read()
        chunks = re.split(r"^=== LESSON (\d+) ===\s*$", text, flags=re.M)
        for k in range(1, len(chunks), 2):
            lessons[int(chunks[k])] = chunks[k + 1]
    return lessons


def render(meta: dict, body_md: str) -> str:
    head = (
        f'<div class="tag">{html.escape(meta["course_title"])} · Chương {meta["chapter_no"]}: {html.escape(meta["chapter_name"])} · Bài {meta["lesson_no"]}</div>'
        f'<h1>{html.escape(meta["title"])}</h1>'
        f'<p class="sub">{html.escape(meta.get("description") or "")}</p>'
    )
    return f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{head}{md_to_html(body_md)}</body></html>'


def main() -> None:
    only = {int(a) for a in sys.argv[1:]}
    meta = {m["lesson_id"]: m for m in json.load(open(os.path.join(HERE, "lessons.json"), encoding="utf-8"))}
    content = load_lessons()
    chrome = find_chrome()
    os.makedirs(OUT, exist_ok=True)
    todo = [lid for lid in sorted(content) if not only or lid in only]
    missing = [lid for lid, m in meta.items() if m["needs_doc"] and lid not in content]
    if missing:
        print("! Thiếu nội dung cho bài:", missing)
    with tempfile.TemporaryDirectory() as tmp:
        for lid in todo:
            if lid not in meta:
                print(f"! bỏ qua bài {lid}: không có trong lessons.json")
                continue
            page = os.path.join(tmp, f"l{lid}.html")
            with open(page, "w", encoding="utf-8") as f:
                f.write(render(meta[lid], content[lid]))
            out = os.path.join(OUT, f"lesson_{lid}.pdf")
            subprocess.run(
                [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                 f"--print-to-pdf={out}", "file:///" + page.replace("\\", "/")],
                check=True, capture_output=True, timeout=120,
            )
            print(f"  bài {lid:2d}: {meta[lid]['title']}  ->  {os.path.getsize(out) // 1024} KB")
    print(f"Xong {len(todo)} bài.")


if __name__ == "__main__":
    main()
