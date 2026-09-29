"""Cấu hình ứng dụng — đọc từ backend/.env (tương đương config/*.php của bản PHP)."""
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Đọc biến môi trường từ file .env; tên biến không phân biệt hoa/thường, biến lạ thì bỏ qua
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # App: APP_DEBUG=true thì lỗi 500 trả kèm chi tiết (chỉ dùng khi phát triển)
    app_env: str = "local"
    app_debug: bool = True
    app_url: str = "http://localhost:8080"

    # Database: thông tin kết nối MySQL
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "studyonline_db"
    db_user: str = "root"
    db_pass: str = ""

    # JWT: khóa bí mật ký token đăng nhập và thời hạn token
    jwt_secret: str = "studyonline_super_secret_key_2026"
    jwt_expire: int = 604800  # 7 ngày (giây)

    # HTTP / upload: domain frontend được phép gọi API, thư mục lưu file, địa chỉ public của API
    frontend_origin: str = "*"
    upload_dir: str = "./uploads"
    public_base_url: str = "http://127.0.0.1:8080"

    # Thanh toán VNPay Sandbox: mã website (TMN code) + chuỗi bí mật do VNPay cấp khi đăng ký sandbox.
    # vnpay_return_url: VNPay chuyển trình duyệt về đây (API backend) sau khi thanh toán;
    # frontend_url: backend chuyển tiếp học viên về trang kết quả trên giao diện.
    vnpay_tmn_code: str = ""
    vnpay_hash_secret: str = ""
    vnpay_payment_url: str = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    # API truy vấn / hoàn tiền (querydr, refund) của VNPay
    vnpay_api_url: str = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"
    vnpay_return_url: str = "http://127.0.0.1:8080/api/payments/vnpay/return"
    frontend_url: str = "http://localhost:5173"
    # Bật lại thanh toán giả lập (không qua cổng) — chỉ dùng khi demo offline
    payment_mock: bool = False
    # Chu kỳ (giây) tự đối soát đơn VNPay đang chờ đã quá hạn; 0 = tắt
    payment_reconcile_interval: int = 300

    # AI (dùng từ Phase 6): nhà cung cấp LLM, model embedding và ngưỡng của RAG AI Tutor
    llm_provider: str = "gemini"
    llm_model: str = ""
    llm_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db_path: str = "./data/chroma"
    base_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    lora_adapter_path: str = ""
    ai_max_context_chunks: int = 5
    rag_similarity_threshold: float = 0.55
    rag_max_question_length: int = 2000

    # Chuỗi kết nối SQLAlchemy tới MySQL (mật khẩu được mã hóa URL để không vỡ ký tự đặc biệt)
    @property
    def database_url(self) -> str:
        pw = quote_plus(self.db_pass) if self.db_pass else ""
        return (
            f"mysql+pymysql://{self.db_user}:{pw}@{self.db_host}:{self.db_port}"
            f"/{self.db_name}?charset=utf8mb4"
        )

    # Danh sách domain được phép gọi API (CORS): "*" = mọi nơi, hoặc nhiều domain cách nhau dấu phẩy
    @property
    def cors_origins(self) -> list[str]:
        if self.frontend_origin.strip() in ("", "*"):
            return ["*"]
        return [o.strip() for o in self.frontend_origin.split(",") if o.strip()]


# Đối tượng cấu hình dùng chung cho toàn bộ backend
settings = Settings()
