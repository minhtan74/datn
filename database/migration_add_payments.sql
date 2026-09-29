-- Migration: Thêm bảng payments
-- Chạy file này nếu database đã tồn tại (không muốn drop & recreate)

USE studyonline_db;

CREATE TABLE IF NOT EXISTS payments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT           NOT NULL,
    course_id       INT           NOT NULL,
    amount          DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    method          ENUM('card','bank_transfer','momo','zalopay') DEFAULT 'card',
    status          ENUM('pending','completed','failed','refunded') DEFAULT 'pending',
    transaction_ref VARCHAR(100)  DEFAULT NULL  COMMENT 'Mã giao dịch / mã tham chiếu',
    note            TEXT          DEFAULT NULL,
    paid_at         TIMESTAMP     NULL DEFAULT NULL,
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_payment_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_payment_course
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

SELECT 'Migration hoàn tất: bảng payments đã được tạo.' AS result;
