-- =========================================
-- DATABASE: STUDYONLINE
-- Version 2.0 - Upgraded Schema
-- =========================================

DROP DATABASE IF EXISTS studyonline_db;

CREATE DATABASE studyonline_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE studyonline_db;

-- =========================================
-- USERS
-- =========================================

CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    fullname    VARCHAR(100)  NOT NULL,
    email       VARCHAR(100)  UNIQUE NOT NULL,
    password    VARCHAR(255)  NOT NULL,
    role        ENUM('student','teacher','admin') DEFAULT 'student',
    avatar      VARCHAR(255)  DEFAULT NULL,
    bio         TEXT          DEFAULT NULL,
    is_active   TINYINT(1)    NOT NULL DEFAULT 1,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================
-- COURSES
-- =========================================

CREATE TABLE courses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id  INT           NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    slug        VARCHAR(255)  UNIQUE,
    description TEXT,
    thumbnail   VARCHAR(255),
    price       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    level       ENUM('beginner','intermediate','advanced') DEFAULT 'beginner',
    status      ENUM('draft','published','archived')       DEFAULT 'draft',
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_course_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================================
-- CHAPTERS
-- =========================================

CREATE TABLE chapters (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    course_id    INT           NOT NULL,
    chapter_name VARCHAR(255)  NOT NULL,
    order_index  INT           NOT NULL DEFAULT 0,
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_chapter_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);

-- =========================================
-- LESSONS
-- =========================================

CREATE TABLE lessons (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id   INT           NOT NULL,
    title        VARCHAR(255)  NOT NULL,
    description  TEXT,
    video_url    VARCHAR(500),
    document_url VARCHAR(500),
    duration     INT           NOT NULL DEFAULT 0     COMMENT 'Thời lượng tính bằng giây',
    order_index  INT           NOT NULL DEFAULT 0     COMMENT 'Thứ tự bài học trong chương',
    is_free      TINYINT(1)    NOT NULL DEFAULT 0     COMMENT '1 = xem thử miễn phí',
    status       ENUM('draft','published')            DEFAULT 'draft',
    created_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_lesson_chapter
        FOREIGN KEY (chapter_id)
        REFERENCES chapters(id)
        ON DELETE CASCADE
);

-- =========================================
-- ENROLLMENTS
-- =========================================

CREATE TABLE enrollments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT           NOT NULL,
    course_id   INT           NOT NULL,
    enroll_date TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_enroll_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_enroll_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_enrollment (user_id, course_id)
);

-- =========================================
-- LESSON PROGRESS (Tiến độ học bài)
-- =========================================

CREATE TABLE lesson_progress (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT           NOT NULL,
    lesson_id    INT           NOT NULL,
    is_completed TINYINT(1)    NOT NULL DEFAULT 0,
    watched_sec  INT           NOT NULL DEFAULT 0  COMMENT 'Số giây đã xem',
    completed_at TIMESTAMP     NULL DEFAULT NULL,
    updated_at   TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_progress_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_progress_lesson
        FOREIGN KEY (lesson_id)
        REFERENCES lessons(id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_progress (user_id, lesson_id)
);

-- =========================================
-- QUIZZES
-- =========================================

CREATE TABLE quizzes (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_id   INT           NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    description TEXT,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quiz_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);

-- =========================================
-- QUESTIONS
-- =========================================

CREATE TABLE questions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id        INT           NOT NULL,
    content        TEXT          NOT NULL,
    option_a       VARCHAR(255)  NOT NULL,
    option_b       VARCHAR(255)  NOT NULL,
    option_c       VARCHAR(255)  NOT NULL,
    option_d       VARCHAR(255)  NOT NULL,
    correct_answer ENUM('A','B','C','D') NOT NULL,
    order_index    INT           NOT NULL DEFAULT 0,

    CONSTRAINT fk_question_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)
        ON DELETE CASCADE
);

-- =========================================
-- RESULTS
-- =========================================

CREATE TABLE results (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT           NOT NULL,
    quiz_id     INT           NOT NULL,
    score       INT           NOT NULL DEFAULT 0,
    total       INT           NOT NULL DEFAULT 0  COMMENT 'Tổng số câu hỏi',
    submit_time TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_result_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_result_quiz
        FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)
        ON DELETE CASCADE
);

-- =========================================
-- ADMIN ACCOUNT (mật khẩu nên dùng password_hash trong thực tế)
-- =========================================

INSERT INTO users (fullname, email, password, role)
VALUES ('Administrator', 'admin@gmail.com', '123456', 'admin');