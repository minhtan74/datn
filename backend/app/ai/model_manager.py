"""Quản lý LLM sinh câu trả lời — đổi provider/model qua .env, không hard-code key.

- LLM_PROVIDER=gemini + LLM_API_KEY  -> gọi Google Gemini REST API.
- LLM_PROVIDER=openai + LLM_API_KEY  -> gọi OpenAI Chat Completions.
- LLM_PROVIDER=claude + LLM_API_KEY  -> gọi Claude qua SDK chính thức (anthropic).
- Không có key / provider=stub       -> chế độ TRÍCH XUẤT (extractive): ghép câu
  trả lời từ chính các đoạn ngữ cảnh đã truy hồi. Nhờ vậy toàn bộ pipeline RAG
  chạy được offline khi bảo vệ đồ án; khi có key thì tự động dùng LLM thật.
"""
from __future__ import annotations

import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger("llm")

# Model mặc định của từng nhà cung cấp khi .env không chỉ định LLM_MODEL
# (gemini-2.0-flash đã bị Google ngừng -> 404; ghim bản ổn định cụ thể thay vì alias "-latest" để kết quả đo không tự đổi)
_GEMINI_DEFAULT = "gemini-3.1-flash-lite"
_OPENAI_DEFAULT = "gpt-4o-mini"
_CLAUDE_DEFAULT = "claude-opus-5"

# Các nhà cung cấp LLM được hỗ trợ
_PROVIDERS = ("gemini", "openai", "claude")

# Lỗi tạm thời (quá tải / vượt rate limit) -> thử lại thay vì báo lỗi ngay.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3
_RETRY_BASE_DELAY = 1.5  # giây, tăng dần theo cấp số nhân
_RETRY_MAX_WAIT = 30.0  # giây — chờ lâu nhất khi nhà cung cấp yêu cầu đợi (vượt giới hạn lượt gọi / phút)


# 429 do hết hạn mức THEO NGÀY (gói miễn phí): chờ vài giây rồi gọi lại cũng vô ích -> báo lỗi ngay
def _daily_quota(resp: httpx.Response) -> bool:
    try:
        return any(
            "PerDay" in str(v.get("quotaId", ""))
            for d in resp.json().get("error", {}).get("details", [])
            for v in d.get("violations", [])
        )
    except (ValueError, AttributeError):
        return False


# Thời gian nhà cung cấp yêu cầu chờ khi trả 429: header Retry-After, hoặc retryDelay "23s" trong lỗi của Gemini
def _retry_after(resp: httpx.Response) -> float | None:
    try:
        if resp.headers.get("retry-after"):
            return float(resp.headers["retry-after"])
        for d in resp.json().get("error", {}).get("details", []):
            if str(d.get("retryDelay", "")).endswith("s"):
                return float(d["retryDelay"][:-1])
    except (ValueError, TypeError, AttributeError):
        pass
    return None


# Gửi POST tới API LLM; gặp lỗi tạm thời (quá tải, mất kết nối) thì thử lại tối đa 3 lần, chờ tăng dần.
# Vượt giới hạn lượt gọi (429) thì chờ đúng thời gian nhà cung cấp yêu cầu (tối đa _RETRY_MAX_WAIT) rồi gọi lại.
# Quá thời gian chờ phản hồi thì KHÔNG thử lại (model chạy chậm, thử lại chỉ khiến người dùng chờ gấp 3).
def _post_with_retry(url: str, *, json: dict, timeout: float, headers: dict | None = None) -> httpx.Response:
    last_error: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        wait = _RETRY_BASE_DELAY * attempt
        try:
            r = httpx.post(url, json=json, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r
        except httpx.HTTPStatusError as e:
            last_error = e
            if e.response.status_code not in _RETRYABLE_STATUS or attempt == _MAX_ATTEMPTS:
                raise
            if e.response.status_code == 429 and _daily_quota(e.response):
                raise
            if e.response.status_code == 429:
                wait = min(_retry_after(e.response) or wait * 4, _RETRY_MAX_WAIT)
        except httpx.TimeoutException:
            raise
        except httpx.TransportError as e:
            last_error = e
            if attempt == _MAX_ATTEMPTS:
                raise
        time.sleep(wait)
    raise last_error  # không thể tới đây, giữ để mypy/an toàn


# Nhà cung cấp đang dùng: chỉ bật LLM khi provider hợp lệ VÀ có API key, ngược lại là 'stub' (offline).
# Riêng openai trỏ tới LLM_BASE_URL (vd. Ollama chạy trên máy) thì không bắt buộc key
def active_provider() -> str:
    p = (settings.llm_provider or "stub").strip().lower()
    if p in _PROVIDERS and settings.llm_api_key.strip():
        return p
    if p == "openai" and settings.llm_base_url.strip():
        return p
    return "stub"


# Thông tin provider + model đang dùng (hiển thị ở giao diện AI)
def info() -> dict:
    p = active_provider()
    defaults = {"gemini": _GEMINI_DEFAULT, "openai": _OPENAI_DEFAULT, "claude": _CLAUDE_DEFAULT}
    model = settings.llm_model.strip() or defaults.get(p, "extractive")
    return {"provider": p, "model": model}


# Hàm chung để sinh văn bản: chuyển tới đúng nhà cung cấp; lỗi thì trả chuỗi "[Lỗi gọi LLM: ...]" thay vì làm sập API
def generate(system: str, user: str, *, max_tokens: int = 700) -> str:
    p = active_provider()
    try:
        if p == "gemini":
            return _gemini(system, user, max_tokens)
        if p == "openai":
            return _openai(system, user, max_tokens)
        if p == "claude":
            return _claude(system, user, max_tokens)
    except Exception as e:  # noqa: BLE001 -> luôn có đường lui
        # Chỉ trả loại lỗi + mã HTTP, không trả nguyên thông báo (có thể chứa URL, khoá, dữ liệu nhạy cảm)
        status = getattr(getattr(e, "response", None), "status_code", None)
        reason = {429: "quá giới hạn lượt gọi", 401: "khoá không hợp lệ", 403: "không có quyền", 404: "model không tồn tại"}
        resp = getattr(e, "response", None)
        why = "hết hạn mức lượt gọi trong ngày" if status == 429 and _daily_quota(resp) else reason.get(status, "lỗi dịch vụ")
        detail = f"HTTP {status} — {why}" if status else type(e).__name__
        logger.warning("LLM %s error: %s", p, detail)
        return f"[Lỗi gọi LLM: {detail}]"
    return _stub(system, user)


# Gọi Google Gemini qua REST (generateContent); temperature thấp 0.2 để câu trả lời bám ngữ cảnh
def _gemini(system: str, user: str, max_tokens: int) -> str:
    model = settings.llm_model.strip() or _GEMINI_DEFAULT
    # Khoá gửi qua header, KHÔNG đặt trong URL: URL xuất hiện trong thông báo lỗi / log và từng lộ khoá ra câu trả lời
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens},
    }
    r = _post_with_retry(url, json=payload, timeout=60, headers={"x-goog-api-key": settings.llm_api_key.strip()})
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# Gọi Chat Completions chuẩn OpenAI qua REST: mặc định OpenAI, hoặc dịch vụ tương thích theo LLM_BASE_URL
def _openai(system: str, user: str, max_tokens: int) -> str:
    model = settings.llm_model.strip() or _OPENAI_DEFAULT
    base_url = settings.llm_base_url.strip().rstrip("/") or "https://api.openai.com/v1"
    key = settings.llm_api_key.strip()
    r = _post_with_retry(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {key}"} if key else None,
        json={
            "model": model,
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        # Model chạy trên máy (Ollama, CPU) trả lời chậm hơn API đám mây nhiều -> chờ lâu hơn
        timeout=180 if settings.llm_base_url.strip() else 60,
    )
    return r.json()["choices"][0]["message"]["content"].strip()


# Gọi Claude qua SDK chính thức anthropic
def _claude(system: str, user: str, max_tokens: int) -> str:
    import anthropic  # nạp lười — chỉ cần khi thực sự dùng Claude

    model = settings.llm_model.strip() or _CLAUDE_DEFAULT
    client = anthropic.Anthropic(api_key=settings.llm_api_key.strip())
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


# Chế độ offline (không có LLM)
def _stub(system: str, user: str) -> str:
    """Trích xuất: lấy phần 'NGỮ CẢNH' trong prompt, ghép 1–2 đoạn liên quan nhất."""
    marker = "NGỮ CẢNH:"
    if marker in user:
        ctx = user.split(marker, 1)[1]
        if "CÂU HỎI:" in ctx:
            ctx = ctx.split("CÂU HỎI:", 1)[0]
        blocks = [b.strip() for b in ctx.strip().split("\n\n") if b.strip()]
        picked = []
        for b in blocks:
            # bỏ nhãn "[Nguồn i] ..." đầu đoạn nếu có
            body = b.split("] ", 1)[1] if b.startswith("[") and "] " in b else b
            picked.append(body.strip())
            if len(" ".join(picked)) > 550:
                break
        answer = " ".join(picked).strip()
        if answer:
            return (
                answer[:900]
                + "\n\n(Trả lời được trích trực tiếp từ tài liệu khóa học — "
                "cấu hình LLM_API_KEY để có câu trả lời được diễn giải tự nhiên hơn.)"
            )
    return "Tôi không tìm thấy thông tin phù hợp trong tài liệu khóa học."
