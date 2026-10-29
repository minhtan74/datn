# Kiểm chứng gợi ý học tập — 13/10/2026

Mục đích: chứng minh quy tắc có căn cứ, hành động hợp lệ, xử lý thiếu dữ liệu và không làm thay đổi phân loại cũ. Đây là kiểm chứng phần mềm bằng tình huống có kết quả mong đợi, chưa phải nghiên cứu đánh giá hiệu quả sư phạm trên học viên thực tế.

## Bộ tình huống

| Tình huống | Kết quả mong đợi | Kiểm thử tự động |
|---|---|---|
| Chưa làm bài | Chưa đủ dữ liệu; vẫn gợi ý bài chưa hoàn thành | `test_no_results_is_not_average` |
| Chỉ có 1 câu chủ đề, làm lại nhiều lần | Không tăng số câu làm căn cứ; không xếp Yếu/Tốt | `test_topic_normalization_course_separation_and_distinct_evidence` |
| Điểm chính thức cao nhất 100%, lượt gần nhất yếu ở một chủ đề | Giữ điểm chính thức 100%; vẫn gợi ý ôn chủ đề theo lượt mới | `test_latest_content_is_independent_of_highest_official_grade` |
| Tên có khoảng trắng/chữ hoa khác nhau | Cùng một mã chủ đề trong một khóa | `test_catalog_reuses_names_for_manual_word_and_ai` |
| Cùng tên ở hai khóa | Không gộp kết quả hai môn | `test_topic_normalization_course_separation_and_distinct_evidence` |
| Câu thiếu chủ đề | Vẫn tính điểm tổng; báo thiếu phân loại | `test_unclassified_question_still_counts_in_official_score` |
| Đổi chủ đề sau khi đã nộp | Kết quả cũ giữ nguyên mã/tên chủ đề tại lúc nộp | `test_saved_classification_is_not_changed_by_question_edit` |
| Câu chưa phân loại lúc nộp, gắn chủ đề sau đó | Không tự gán chủ đề mới cho kết quả cũ | `test_snapshot_unclassified_remains_unclassified_after_edit` |
| Được 75%, đề yêu cầu 80% | Gợi ý làm lại nếu còn lượt | `test_retake_above_70_but_below_passing_score` |
| Đề lấy điểm lần đầu | Không gợi ý làm lại nhằm tăng điểm chính thức | `test_retake_uses_grading_policy` |
| Lượt bỏ dở hoặc hết hạn dùng hết số lượt | Không gợi ý mở lượt mới | `test_abandoned_attempt_uses_last_slot`, `test_expired_last_attempt_cannot_be_recommended` |
| Lượt cuối vẫn đang làm | Cho tiếp tục lượt đó | `test_live_last_attempt_can_be_resumed` |
| Liên kết bài học khác khóa / bộ luyện không có câu chủ đề | Từ chối cấu hình | `test_topic_mapping_rejects_other_course_lesson`, `test_topic_mapping_rejects_practice_without_topic_questions` |
| Giáo viên sửa chủ đề của khóa người khác | Từ chối 403 | `test_teacher_cannot_edit_another_courses_topic` |
| Hủy ghi danh | Không tạo hành động hoặc checkpoint mới cho khóa đó | `test_checkpoint_denied_after_enrollment_removed`, `test_removed_enrollment_does_not_create_retake` |
| Mở gợi ý nhưng chưa làm bài mới | Hiện trạng thái chờ; không lấy kết quả cũ làm “sau” | `test_progress_uses_only_submissions_after_checkpoint` |
| Làm từ 2/6 đúng lên 5/6 đúng sau mốc | Hiện +50 điểm phần trăm, cùng bộ câu; nêu khả năng nhớ đáp án | `test_progress_uses_only_submissions_after_checkpoint` |
| Hai mốc khác số câu/độ khó và một mốc ít hơn 5 câu | Hiện số liệu tham khảo, chưa đủ dữ liệu và giới hạn so sánh | `test_comparison_exposes_sample_limits_and_no_causal_claim` |

Chạy tại `backend`:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_recommendations.py tests/test_word_import.py tests/test_quiz_difficulty.py tests/test_quiz_shuffle.py -p no:cacheprovider
```

Kết quả: **76 passed**. Dữ liệu kiểm thử nằm trong SQLite bộ nhớ; không ghi điểm demo.

## Luồng demo cho hội đồng

1. Đăng nhập giảng viên, mở **Quiz trắc nghiệm**, chọn đề. Chọn hoặc thêm chủ đề ngay khi soạn câu hỏi nhập tay/Word/AI và dùng cùng chủ đề cho các câu cùng nội dung.
2. Tạo bộ ôn tập có câu thuộc chủ đề. Trang quản lý chủ đề riêng đã được gỡ; liên kết ôn tập đã lưu vẫn được dùng, còn chủ đề chưa có liên kết riêng sẽ dùng thông tin bài học hoặc dẫn về danh sách bài của khóa.
3. Dùng tài khoản học viên đã ghi danh, làm bài có ít nhất 5 câu của chủ đề với kết quả thấp. Mở Dashboard/Tiến độ và bấm Cập nhật.
4. Mở **Vì sao có gợi ý này?** để chỉ ra số câu đúng/tổng, đề, thời điểm và đường dẫn kết quả. Chỉ ra các ngưỡng là quy tắc cấu hình ban đầu.
5. Bấm **Ôn bài học** hoặc **Xem bài học**, sau đó làm bài luyện liên quan. Nút **Làm bài luyện** chỉ có nếu đã tồn tại liên kết bộ ôn được xác nhận và còn quyền/lượt làm. Sau khi nộp bài mới, mở Dashboard/Tiến độ và bấm Cập nhật để xem mốc trước/sau.
6. Trình bày số câu ở hai mốc và chênh lệch điểm phần trăm. Nêu rõ dữ liệu này chỉ phản ánh thay đổi quan sát được, chưa chứng minh quan hệ nhân quả hoặc thành thạo kiến thức.

Các thao tác demo trên tạo dữ liệu học tập thật; dùng tài khoản/khóa demo riêng khi trình diễn. Không tự chèn kết quả tốt hoặc đánh dấu giảng viên xác nhận hộ người dùng.

## Bằng chứng kiểm tra MySQL local

- Migration `0020_topic_catalog` áp dụng thành công, giữ các chủ đề cũ ở trạng thái chờ xác nhận.
- API đọc danh mục/gợi ý và ghi checkpoint/đọc so sánh trả HTTP 200.
- API nhập tay, duyệt Word và AI cùng chấp nhận mã chủ đề thuộc khóa.
- API thêm và xác nhận liên kết chủ đề trả HTTP 200.
- API nộp bài lưu đúng `topic_id`, `topic_name`, `classification_version=2`.
- Các bản ghi dùng trong kiểm tra tích hợp được rollback.
- Frontend build thành công. Chưa tự động thao tác toàn bộ luồng bằng trình duyệt; build và TestClient không thay cho kiểm tra trực quan từng màn hình.
