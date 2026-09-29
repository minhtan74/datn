"""Sinh embedding cho văn bản (fastembed / ONNX — không cần PyTorch).

Model đa ngữ (có tiếng Việt): sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
(384 chiều). Nạp lười ở lần gọi đầu tiên để không chặn khởi động server.
"""
from __future__ import annotations

import os
import threading

from app.core.config import settings

# fastembed chỉ hỗ trợ một tập model nhất định -> map tên "chung" sang tên hợp lệ.
_SUPPORTED = {
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "sentence-transformers/all-MiniLM-L6-v2",
    "BAAI/bge-small-en-v1.5",
    "intfloat/multilingual-e5-large",
}
_DEFAULT = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Model được nạp 1 lần duy nhất và dùng chung; khóa (lock) tránh 2 request cùng nạp model một lúc
_model = None
_lock = threading.Lock()


# Tên model trong .env không được fastembed hỗ trợ thì dùng model đa ngữ mặc định
def _resolve_model_name() -> str:
    name = (settings.embedding_model or "").strip()
    return name if name in _SUPPORTED else _DEFAULT


# Nạp model lười ở lần gọi đầu tiên (kiểm tra 2 lần trước/sau khi khóa để an toàn đa luồng)
def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
                from fastembed import TextEmbedding

                _model = TextEmbedding(_resolve_model_name())
    return _model


# Tạo vector 384 chiều cho danh sách văn bản
def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    return [vec.tolist() for vec in model.embed(list(texts))]


# Tạo vector cho 1 câu hỏi
def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


# Thông tin model embedding (hiển thị ở /api/ai/status)
def model_info() -> dict:
    return {"provider": "fastembed", "model": _resolve_model_name(), "dim": 384}
