# Kiểm tra chức năng StudyOnline — 22/10/2026

## Kết luận

Các luồng cốt lõi đã hoạt động trong phạm vi kiểm tra: đăng nhập ba vai trò, phân quyền, quản lý nội dung, ghi danh, học tập, nhập đề Word, làm quiz, xem kết quả và thống kê. Kiểm tra bổ sung với Gemini thật cũng thành công cho một câu AI Tutor và một câu quiz mức trung bình. Chưa thể kết luận toàn bộ chức năng đã ổn: bộ kiểm thử còn 5 bài thất bại do kỳ vọng chưa cập nhật; liên kết quên mật khẩu chưa có chức năng; giao dịch VNPay qua cổng thực tế chưa được xác minh.

Không sửa mã ứng dụng hay các test có sẵn trong đợt kiểm tra này.

## Môi trường và phạm vi

- Ban đầu cả MySQL, backend và frontend đều tắt. Đã khởi động MySQL từ thư mục dữ liệu có sẵn.
- Database gốc có 7 khóa học; Alembic ở `0020_topic_catalog`, khớp migration mới nhất trong mã nguồn.
- Toàn bộ kiểm tra có ghi dữ liệu chạy trên database **bản sao riêng**. Không chạy test ghi dữ liệu trên database gốc, không import lại SQL khởi tạo.
- Backend chạy bộ pytest tắt tác vụ tự đối soát thanh toán và dùng `LLM_PROVIDER=stub`. Lần kiểm tra Gemini bổ sung dùng cấu hình Gemini thật sau khi người dùng cho phép, trên một database bản sao riêng khác.
- Frontend được build và chạy bằng Vite preview. Chrome headless chạy với hồ sơ tạm, kiểm tra màn hình desktop 1440 px và mobile 390 px.
- Chỉ kiểm tra mở trang đối với một số màn hình; việc mở trang thành công không chứng minh mọi nút và mọi tình huống trên trang đều đã được kiểm thử.
- Đã xóa database bản sao và dừng các tiến trình kiểm thử sau khi hoàn tất; MySQL được dừng bằng lệnh shutdown bình thường. Database gốc vẫn có 7 khóa học.

## Kết quả

| Nhóm | Kết quả và giới hạn |
|---|---|
| Build frontend | Thành công; có 2 cảnh báo CSS và bundle JavaScript khoảng 1,03 MB trước nén. |
| Backend tự động | **106/111 bài đạt, 5 bài thất bại** trong lần chạy cuối sau khi model embedding tải thành công. |
| Trình duyệt | Mở **31 lượt trang** gồm công khai, admin, giảng viên, học viên và 3 màn hình mobile. Không ghi nhận exception JavaScript hoặc API trả lỗi trong các lượt mở trang này. Có một lỗi tài nguyên `favicon.ico` trả 404. |
| Đăng nhập và phân quyền | Đăng nhập thành công admin, giảng viên, học viên qua form thật. Học viên bị chặn khỏi `/admin`; xóa phiên rồi vào trang bảo vệ được chuyển về đăng nhập. API kiểm tra quyền truy cập người dùng, nội dung học, tài liệu và kết quả bài làm đã đạt các bài tương ứng. |
| Khóa học, chương, bài | Các bài kiểm tra CRUD, kiểm tra sở hữu và bảo vệ dữ liệu đã có học viên/kết quả được thực thi. Luồng tổng hợp cũ có lỗi test ở bước nộp quiz, được xác minh bổ sung bằng trình duyệt. |
| Nhập Word | Test bộ đọc, công thức, ảnh, nhập qua API và lưu đề đạt. |
| Quiz | Trình duyệt tạo khóa và đề 3 câu trong database bản sao, ghi danh học viên, chọn đúng theo **nội dung phương án đã đảo**, tải lại trang, nộp và xem lại kết quả. Giữ nguyên thứ tự câu và đáp án đang chọn, chấm 100%, tải lại kết quả vẫn hiển thị đúng. |
| Tiến độ và gợi ý | Các trang dashboard, khóa học và tiến độ hiển thị được; kiểm tra đơn vị về chủ đề, bằng chứng học tập và gợi ý đạt. Một test tích hợp vẫn yêu cầu nhãn phân loại cũ. |
| AI Tutor | Test cục bộ hỏi đáp theo tài liệu, từ chối câu hỏi ngoài nội dung và quyền giảng viên đạt. Lần gọi Gemini thật trả đúng ba trạng thái Promise, kèm hai nguồn tài liệu, không dùng trả lời dự phòng; thời gian 7,24 giây. |
| AI sinh quiz | Các test đơn vị quy tắc sinh câu, phương án nhiễu, độ khó và thẩm định đạt. Gemini thật sinh được một câu mức trung bình trong 10,91 giây, có bốn phương án và căn cứ tài liệu; bước tự giải lại khớp đáp án và mức độ khó. Duyệt, lưu và đọc lại quiz thành công trong database bản sao. Test tích hợp cũ yêu cầu sinh câu trung bình bằng chế độ offline vẫn thất bại đúng với giới hạn đã ghi trong README. |
| Thanh toán | Các test callback có chữ ký, chống bỏ qua thanh toán, đối soát và hoàn tiền đạt với phản hồi VNPay mô phỏng. Chưa thực hiện một lượt thanh toán qua trang VNPay hoặc xác minh IPN công khai. |
| Mobile | Dashboard, khám phá khóa học và tiến độ không tràn ngang ở độ rộng 390 px; đã xem ảnh chụp trang tiến độ. Các màn hình mobile khác chưa được rà soát toàn bộ. |

## Các vấn đề cần xử lý

### 1. Bộ kiểm thử tích hợp chưa theo kịp hành vi hiện tại

| Test trong `backend/tests/test_api.py` | Nguyên nhân đối chiếu được | Cách cập nhật cần thiết |
|---|---|---|
| `test_full_learning_flow`, dòng 164 | Mở câu hỏi đã cấp lượt làm, nhưng test nộp bài thiếu `attempt_token`; API trả lỗi nghiệp vụ thay vì `score`. | Lưu token từ phản hồi mở đề và gửi khi nộp; chọn phương án theo nội dung đã đảo. |
| `test_lesson_review_and_quiz_settings`, dòng 294 | Test gửi cố định chữ cái đáp án gốc sau khi đề đã đảo phương án; lần chạy cuối nhận 0% thay vì 100%. | Đối chiếu nội dung phương án trong lượt đang làm, không cố định chữ cái biên soạn. |
| `test_answers_hidden_until_last_attempt_and_fair_analytics`, dòng 327 | Giả định chữ A luôn sai; sau khi đảo, chữ A có thể đúng. Một số lượt ôn tập trong test còn thiếu token. | Mỗi lượt lấy token và xác định phương án đúng/sai từ nội dung được hiển thị; cập nhật cả kiểm tra lịch sử theo thứ tự của lượt làm. |
| `test_recommendation_flow`, dòng 496 | Chỉ chấp nhận `Weak/Average/Good/Excellent`, trong khi gợi ý mới trả `ContentBased`; giao diện đã xử lý nhãn mới. | Kiểm tra hợp đồng mới `ContentBased/Insufficient` và cấu trúc dữ liệu gợi ý. |
| `test_ai_generate_and_approve_quiz`, dòng 571 | Test chạy chế độ stub nhưng yêu cầu câu mức `medium`; chức năng offline hiện chỉ hỗ trợ mức dễ. | Tách test offline mức dễ và test tích hợp LLM mức trung bình/khó có điều kiện chạy rõ ràng. |

Đây là nguyên nhân tìm được từ phản hồi, mã nguồn và kiểm tra bổ sung; không nên đổi kỳ vọng chỉ để làm xanh bộ test. Cần cập nhật test rồi chạy lại cả bộ, đặc biệt phần thống kê và lịch sử sau nhiều lượt làm.

### 2. Quên mật khẩu chưa triển khai

`frontend/src/pages/Login.jsx:84` dùng `href="#"`; nhấn **Quên mật khẩu?** chưa mở quy trình khôi phục. Admin có chức năng đổi mật khẩu người dùng và bài kiểm tra tương ứng đã đạt, nhưng chức năng đó không thay thế quy trình tự khôi phục của học viên.

### 3. Hướng dẫn độ dài mật khẩu chưa thống nhất

`frontend/src/pages/student/Profile.jsx:204` hiển thị “Ít nhất 8 ký tự”, trong khi kiểm tra phía client tại dòng 79 và API đổi mật khẩu đang chấp nhận từ 6 ký tự. Cần chọn một quy tắc và đồng bộ thông báo/kiểm tra.

### 4. Cảnh báo giao diện và hiệu năng

- `frontend/src/index.css` đưa các CSS vào `layer(base)`, còn các CSS con chứa `@import` Google Fonts; quá trình build báo hai `Unknown at rule: @import`. Nên đưa khai báo tải font về đầu vào phù hợp rồi kiểm tra lại font thực tế.
- JavaScript được đóng vào một bundle khoảng **1.030.881 byte** trước nén; nên cân nhắc tải trang theo nhu cầu để giảm tải lần đầu. Chưa đo hiệu năng mạng chậm nên đây là cơ hội cải thiện, không phải lỗi chức năng đã chứng minh.
- Trình duyệt yêu cầu `/favicon.ico` và nhận 404; nên thêm biểu tượng trang.

### 5. Kiểm tra riêng Chủ đề kiến thức: logic chính đạt, danh sách khóa học chưa lọc quyền quản lý

**Cập nhật sau kiểm tra:** theo yêu cầu người dùng, đã gỡ trang quản lý chủ đề và mục menu; `/teacher/topics` chuyển về Quiz. Lỗi chọn khóa mô tả dưới đây thuộc trang đã gỡ. Việc phân loại câu hỏi và gợi ý ôn tập vẫn giữ. Frontend build thành công và 27 test liên quan đạt sau thay đổi.

Lần kiểm tra bổ sung theo yêu cầu người dùng: `tests/test_recommendations.py` đạt **27/27 test**. Tám phép kiểm tra API bổ sung trên SQLite trong bộ nhớ đều đạt: dùng lại tên chủ đề tương đương; chặn bộ ôn chưa có câu cùng chủ đề; lưu liên kết hợp lệ; chặn bài học/bộ ôn khác khóa; đổi tên cập nhật câu hỏi; chặn giảng viên khác sửa; chặn học viên quản lý.

Tuy nhiên, `frontend/src/pages/teacher/Topics.jsx` đưa toàn bộ kết quả `/api/courses` vào danh sách và tự chọn khóa đầu tiên. API này trả cả các khóa đã xuất bản của giảng viên khác. Khi khóa mới nhất thuộc người khác, trang tự chọn khóa đó rồi gọi `/api/topics` và nhận **403**, dù tài khoản vẫn có khóa được phép quản lý. Đã tái hiện bằng hai khóa của hai giảng viên trong môi trường API cô lập; dữ liệu gốc không bị tác động.

Cần lọc danh sách theo giảng viên sở hữu đối với tài khoản teacher; admin được chọn tất cả. Đây là lỗi giao diện chọn phạm vi: backend vẫn chặn đúng quyền và không cho sửa chủ đề của khóa người khác. Chưa sửa mã trong đợt đánh giá này. Bằng chứng: [kết quả kiểm tra riêng chủ đề](audit-topic-results.json).

## Kiểm tra Gemini bổ sung và giới hạn thanh toán

Sau khi người dùng cho phép gửi câu hỏi và nội dung tài liệu tới Gemini đã cấu hình, đã kiểm tra trực tiếp hai API bằng model `gemini-3.1-flash-lite`:

- `/api/ai/chat`: HTTP 200, 7,24 giây; câu trả lời có `pending`, `fulfilled`, `rejected`, hai nguồn trích dẫn và không có thông báo dùng trích xuất dự phòng.
- `/api/ai/generate-quiz`: HTTP 200, 10,91 giây; sinh một câu về Semaphore ở mức trung bình, đủ bốn phương án, căn cứ được hệ thống đánh dấu khớp tài liệu. Bước AI giải lại xác nhận đáp án B và mức trung bình, không có cảnh báo về căn cứ hoặc độ khó.
- `/api/ai/quiz/approve`: HTTP 200; quiz lưu và đọc lại được với đúng số câu.
- Ba lượt gọi Gemini bên dưới hai chức năng đều trả HTTP 200. Thời gian là quan sát từ một lần chạy, không phải cam kết hiệu năng.
- Database bản sao của lần kiểm tra này đã được xóa và MySQL do kiểm tra khởi động đã dừng bình thường. Không sửa khóa API hay mã ứng dụng.

Kết quả chỉ xác minh hai tình huống mẫu, không đánh giá toàn diện chất lượng AI hoặc tải đồng thời. Thanh toán qua trang VNPay và IPN công khai vẫn chưa được kiểm tra thực tế.

## Bằng chứng

- [Kết quả pytest lần cuối](audit-final-results.xml) và [log rút gọn](audit-final-pytest.log).
- [Kết quả kiểm tra trình duyệt và từng phép kiểm tra](audit-browser-results.json).
- [Phản hồi và kiểm tra Gemini thật](audit-ai-live-results.json), [log kiểm tra Gemini](audit-ai-live.log).
- Ảnh chụp [admin](audit-admin.png), [giảng viên](audit-teacher.png), [học viên](audit-student.png), [mobile](audit-mobile.png).

Khuyến nghị trước buổi demo: cập nhật 5 test tích hợp nêu trên, xử lý hoặc làm rõ chức năng quên mật khẩu, sau đó xác minh một lượt thanh toán VNPay trong môi trường sandbox nếu có sử dụng chức năng này khi demo.
