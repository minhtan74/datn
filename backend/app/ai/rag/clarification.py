"""Hỏi thông tin còn thiếu trước RAG; không gọi LLM và không đoán chủ đề."""
from __future__ import annotations

import re
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


_GENERIC = set("""
    a ah oi em minh toi ban thay co anh chi ai ho giup voi nhe nha nho vui long hay
    cho mot vai vi du giai thich them ro hon ky chi tiet don gian ngan gon de hieu di nua thuc te
    khong chua biet muon can hoi ve cai nay do kia no nhu vay the thi la gi sao nao lai cua trong thu
    lam cach the nao dung hoat dong nhu the nao tai vi sao cai gi phan doan bai cau tap huong dan
    so sanh khac nhau giong nen chon dung tot nhat cai nao giai dap an tra loi duoc
    xin chao hello hi hey help me please explain this that example examples
""".split())
_REFERENCE = re.compile(r"\b(no|cai nay|cai do|cai kia|phan nay|phan do|doan nay|doan do|ham nay|bien nay)\b")
_ENGLISH_REFERENCE = re.compile(r"\b(this|that)\b", re.I)
_DEBUG = re.compile(
    r"\b(bi loi|bao loi|khong chay|chay khong duoc|khong ra ket qua|sai o dau|"
    r"sua (?:code|loi)|fix (?:this|my|the) (?:code|error)|doesn.t(?: it)? work)\b"
)
_DEFINITION = re.compile(r"\b(la gi|nghia la gi|what is|what does .+ mean)\b")
_COMPARISON = re.compile(r"\b(phan biet|so sanh|khac nhau|compare|difference between)\b")
_SPECIFIC_ERROR = re.compile(r"\b\w+(?:Error|Exception)\b|\bHTTP\s*[45]\d{2}\b", re.I)
_PERSONAL = re.compile(r"\b(em|minh|toi|my)\b")
_PROGRAM = re.compile(r"\b(code|web|website|app|chuong trinh|ung dung|project|du an)\b")
_FAILURE = re.compile(r"\b(bi loi|bao loi|khong chay|chay khong duoc|khong ra ket qua|sai o dau|doesn.t(?: it)? work)\b")
# Các từ này chỉ mô tả yêu cầu/trạng thái, chưa chỉ ra một đối tượng cụ thể để giải thích.
_SUBJECT_FILLERS = _GENERIC | set("""
    bi bao loi code web website app chuong trinh ung dung dang o dau duoc ham bien
    on an toan chinh xac dum trinh bay chay sua sai ra ket qua
    what is are does do how why doesn t work can should the which to it
""".split())
_CODE = re.compile(r"```|`[^`]*[()\[\]{}=;+*/][^`]*`|\bdef \w+\(|\bfunction\b|=>|\bprint\(|\bconsole\.|"
                   r"\bselect\b.+\bfrom\b|\btraceback\b|\w+(?:Error|Exception):", re.I | re.S)

PROMPTS = {
    "topic": "Bạn muốn mình giải thích chủ đề hoặc khái niệm nào? Bạn gửi tên nội dung hoặc đoạn đang chưa hiểu nhé.",
    "debug": "Bạn gửi đoạn code liên quan và thông báo lỗi đầy đủ nhé. Bạn đang dùng ngôn ngữ/công cụ nào và mong đợi kết quả gì?",
    "exercise": "Bạn gửi nguyên đề bài hoặc nội dung câu hỏi cần giải nhé; chỉ số câu/tên bài chưa đủ để xác định yêu cầu.",
    "comparison": "Bạn muốn so sánh những khái niệm hoặc lựa chọn nào? Bạn cho biết mục đích sử dụng để mình giải thích đúng trọng tâm nhé.",
}


def last_exchange(history: list[dict] | None) -> tuple[dict, dict]:
    """Chỉ dùng lượt gần nhất, không mượn một chủ đề cũ sau câu hỏi chưa giải quyết."""
    rows = [m for m in (history or []) if m.get("role") in ("user", "assistant")]
    if len(rows) >= 2 and rows[-1]["role"] == "assistant" and rows[-2]["role"] == "user":
        return rows[-2], rows[-1]
    return {}, {}


def _generic(text: str) -> bool:
    words = re.findall(r"[a-z]+", normalize(text))
    if text.strip() == "AI" or (re.search(r"\bAI\b", text) and re.search(r"\bai (la gi|hoat dong)\b", normalize(text))):
        return False
    if re.search(r"\d+\s*[+*/=−-]\s*\d+", text) or _CODE.search(text):
        return False
    return not words or all(w in _GENERIC for w in words)


def _reference(question: str) -> bool:
    # IT là thuật ngữ; "it" viết thường là đại từ cần đối tượng trong hội thoại.
    # Không tìm this/that trên bản bỏ dấu: từ tiếng Việt "thật" không phải đại từ "that".
    return bool(_REFERENCE.search(normalize(question)) or _ENGLISH_REFERENCE.search(question) or re.search(r"\b(?:it|It)\b", question))


def _has_subject(question: str) -> bool:
    text = normalize(question)
    # "Trong Python, nó là gì?" chỉ có phạm vi, chưa có đối tượng mà "nó" chỉ đến.
    text = re.sub(r"^(?:trong|voi|bang)\s+[a-z0-9_+#.-]+\s*,?\s+(?=no\b|cai\b|phan\b|doan\b|ham nay\b|bien nay\b)", "", text)
    return bool(_CODE.search(question) or any(w not in _SUBJECT_FILLERS for w in re.findall(r"[a-z][a-z0-9_]*", text)))


def _unresolved_reference(question: str) -> bool:
    return _reference(question) and not _has_subject(question)


def _needs_debug_details(question: str) -> bool:
    text = normalize(question)
    if not _DEBUG.search(text) or _CODE.search(question):
        return False
    if _DEFINITION.search(text) or _SPECIFIC_ERROR.search(question):
        return False
    # Nhắc tới lỗi trong một câu hỏi kiến thức không đồng nghĩa đang nhờ chẩn đoán code bị hỏng.
    if _COMPARISON.search(text) and _has_subject(question):
        return False
    if re.search(r"\bco(?: tu)? bao loi\b", text) and _has_subject(question):
        return False
    if not _has_subject(question):
        return True
    return bool(_FAILURE.search(text) and (_PERSONAL.search(text) or _PROGRAM.search(text)))


def anchor_question(history: list[dict] | None) -> str | None:
    rows = [m for m in (history or []) if m.get("role") in ("user", "assistant")][-12:]
    while len(rows) >= 2:
        user, assistant = last_exchange(rows)
        text = assistant.get("content", "")
        if (not text or assistant.get("needs_clarification") or assistant.get("response_status") == "error"
                or "không tìm thấy thông tin phù hợp" in text.lower() or text.startswith("[Lỗi gọi LLM")):
            return None
        question = user["content"]
        if _CODE.search(question) or (not _generic(question) and not _unresolved_reference(question)):
            return question
        rows = rows[:-2]
    return None


def has_anchor(history: list[dict] | None) -> bool:
    return anchor_question(history) is not None


def request_kind(question: str, history: list[dict] | None = None) -> str | None:
    """Chỉ chặn trường hợp thiếu đối tượng rõ ràng; câu hỏi ngắn có thuật ngữ vẫn qua RAG."""
    text = normalize(question)
    code = bool(_CODE.search(question))
    anchored = has_anchor(history)
    _, previous_assistant = last_exchange(history)
    if _needs_debug_details(question):
        if not (anchored and _CODE.search(anchor_question(history) or "")):
            return "debug"
    # Không suy ra nội dung bài tập chỉ từ số câu, kể cả đã nói về một chủ đề trước đó.
    if re.search(r"\b(bai|cau)\b", text) and _generic(question) and not code:
        return "exercise"
    if _unresolved_reference(question) and not code and not anchored:
        return "comparison" if re.search(r"so sanh|khac nhau|chon", text) else "topic"
    if _generic(question) and not anchored:
        return "comparison" if re.search(r"so sanh|khac nhau|chon", text) else "topic"
    # Trả lời chỉ tên ngôn ngữ sau yêu cầu sửa lỗi vẫn thiếu code/thông báo lỗi.
    if previous_assistant.get("clarification_kind") == "debug" and not code and len(text.split()) <= 4:
        if not (_DEFINITION.search(text) or _COMPARISON.search(text) or _SPECIFIC_ERROR.search(question)):
            return "debug"
    return None


def is_follow_up(question: str, history: list[dict] | None) -> bool:
    return has_anchor(history) and (_generic(question) or _unresolved_reference(question))


def supplemented_query(question: str, history: list[dict] | None) -> str | None:
    """Ghép câu trả lời làm rõ với yêu cầu ban đầu để không mất mục đích (ví dụ, so sánh...)."""
    user, assistant = last_exchange(history)
    if assistant.get("needs_clarification") and len(question.split()) <= 25:
        if not (_DEFINITION.search(normalize(question)) or (_COMPARISON.search(normalize(question)) and _has_subject(question))):
            return f"{user['content']}\nThông tin bổ sung của học viên: {question}"
    return None
