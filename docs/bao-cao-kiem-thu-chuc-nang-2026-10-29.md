# Báo cáo kiểm thử chức năng StudyOnline

**Ngày kiểm tra:** 29/10/2026, múi giờ Việt Nam.  
**Môi trường:** frontend `http://127.0.0.1:5173`, backend `http://127.0.0.1:8080`, MySQL local; Chromium tự động.  
**Phương pháp:** đăng nhập tài khoản thật trong dữ liệu mẫu, thao tác trực tiếp qua giao diện và gọi API có xác thực. Tạo khóa học, tài khoản, câu hỏi và đơn VNPay riêng cho lần kiểm thử; lưu bằng chứng rồi dọn dữ liệu test.

## 1. Kết luận

Các luồng chức năng đã kiểm tra hoạt động đúng sau khi đối chiếu kết quả: **178 kịch bản API và 35 kịch bản giao diện đạt ở lần xác minh cuối**. Không ghi nhận lỗi JavaScript hoặc HTTP bất thường trong các kịch bản giao diện cuối cùng.

**Vấn đề thực tế cần ưu tiên là độ trễ và độ ổn định của AI Tutor:** hai câu hỏi trong tài liệu mất **45,51 giây** và **61,29 giây**; lần thứ hai dùng câu trả lời trích xuất dự phòng do AI gián đoạn. Sinh đề AI vẫn tạo được 3/3 câu và duyệt lưu thành công trong lần thử này.

Kết quả này áp dụng cho những kịch bản được liệt kê bên dưới; không phải chứng nhận toàn bộ hệ thống không còn lỗi.

## 2. Tài khoản sử dụng

| Vai trò | Tài khoản | Nội dung kiểm tra chính |
|---|---|---|
| Admin | `admin@gmail.com` | Quản lý tài khoản, khóa/mở khóa, giao dịch, bộ lọc, báo cáo và xuất CSV |
| Giảng viên | `an.nguyen@studyonline.vn` | Tạo/sửa khóa, chương, bài, đề, câu hỏi; tài liệu RAG; sinh và duyệt đề AI |
| Giảng viên | `binh.tran@studyonline.vn` | Tạo/sửa khóa riêng; kiểm tra không được sửa hoặc làm đề của giảng viên khác |
| Học viên | `em.hoang@gmail.com` | Đăng ký khóa, hoàn thành bài, làm quiz, ôn tập, gợi ý, AI Tutor, quyền riêng tư |
| Học viên | `phuong.vu@gmail.com` | Kiểm tra độc lập các luồng học tập, chấm điểm và gợi ý trên cùng khóa test |

Ngoài 5 tài khoản mẫu, có 2 tài khoản tạm để kiểm tra admin tạo người dùng, tự đăng ký, đổi mật khẩu và cập nhật hồ sơ. Hai tài khoản này đã được xóa. Mật khẩu và hồ sơ của các tài khoản mẫu không bị thay đổi.

## 3. Số liệu hệ thống trước khi tạo dữ liệu test

Đây là dữ liệu hiện có trong database local, bao gồm dữ liệu mẫu/lịch sử demo; không phải số liệu sử dụng thực tế ngoài môi trường này.

| Chỉ số | Giá trị |
|---|---:|
| Tổng tài khoản | 15 |
| Admin / giảng viên / học viên | 1 / 4 / 10 |
| Khóa học đã xuất bản | 11 |
| Chương / bài học | 41 / 102 |
| Bài có URL video / tài liệu | 66 / 101 |
| Bộ quiz / câu hỏi | 34 / 393 |
| Tài liệu RAG đã lập chỉ mục | 75 |
| Ghi danh | 25 |
| Lượt quiz chính thức | 104 |
| Học viên có kết quả quiz chính thức | 9 |
| Điểm quiz tổng hợp theo quy tắc chấm | 78,4% |
| Hoàn thành bài học trung bình | 58,7% |
| Câu hỏi AI Tutor đã lưu | 9 |
| Tỷ lệ AI không tìm thấy thông tin trong lịch sử | 11,1% |
| Tổng giao dịch | 32 |
| Thành công / thất bại / hoàn tiền / đang chờ | 18 / 12 / 2 / 0 |
| Doanh thu từ giao dịch `completed` | 11.782.000đ |
| Số tiền giao dịch `refunded` | 998.000đ |

Lưu ý khi diễn giải:

- Trong 11 khóa có một khóa rỗng tên `PYTEST Course` từ lần kiểm thử trước; 11 không đồng nghĩa 11 khóa nội dung hoàn chỉnh. Khóa này không thuộc dữ liệu test mới của báo cáo.
- Có 10 quiz chính thức không đặt điểm đạt. Chỉ số tỷ lệ đạt tổng quan đang là 0%, nhưng chỉ tính các kết quả đủ điều kiện có ngưỡng đạt; không thể kết luận mọi học viên đều trượt.
- “Có URL video/tài liệu” là kiểm tra trường dữ liệu, chưa xác nhận mọi tài nguyên phát hoặc tải được. Một số bài có thể chủ đích là bài đọc.

Nguồn: [snapshot trước/sau](functional-account-state.json), [kiểm kê nội dung](functional-account-inventory.json).

## 4. Phạm vi và kết quả kiểm thử

| Nhóm chức năng | Đã thực hiện | Kết quả |
|---|---|---|
| Xác thực | Đăng nhập 5 tài khoản qua API và form; đăng xuất, chặn quay lại trang riêng | Đạt |
| Tài khoản | Admin tạo/sửa/khóa/mở khóa; tự đăng ký, trùng email, đổi mật khẩu, mật khẩu cũ bị từ chối, sửa hồ sơ | Đạt |
| Phân quyền | Học viên không xem danh sách người dùng/báo cáo admin, không tạo khóa/sinh đề; giảng viên không sửa khóa hoặc nộp đề của người khác | Đạt |
| Khóa học | Hai giảng viên tạo/sửa khóa qua API; sửa mô tả và tìm khóa bằng giao diện | Đạt |
| Chương/bài | Tạo chương, 2 bài học, gắn câu hỏi vào kiến thức chương/bài | Đạt |
| Ghi danh | Hai học viên mở chi tiết và đăng ký miễn phí qua giao diện; chặn đăng ký miễn phí khóa trả phí | Đạt |
| Tiến độ | Hoàn thành từng bài bằng nút đánh dấu; tải lại vẫn giữ trạng thái | Đạt |
| Quiz chính thức | Đề 6 câu, 10 phút, 3 lượt, điểm đạt 70%, lấy điểm lượt cuối; mỗi học viên nộp 3 lần | Đạt |
| Tính ổn định lượt làm | Tải lại giữ token, thứ tự phương án và đáp án nháp; không lộ đáp án trước nộp; chặn lượt thứ tư | Đạt |
| Ôn chương | Hai lượt ôn/người, chặn nộp lại token đã hoàn tất; điểm ôn không làm thay đổi điểm quiz chính thức | Đạt |
| Gợi ý | Ghi nhận kiến thức yếu, lưu mốc trước ôn, đối chiếu sau ôn, bỏ gợi ý đã đạt | Đạt |
| Quyền riêng tư | Học viên không đọc được kết quả hoặc hội thoại của người khác | Đạt |
| Tài liệu AI | Tải TXT, lập chỉ mục, từ chối đuôi không hỗ trợ và xóa tài liệu | Đạt |
| AI Tutor | Câu hỏi trong tài liệu có nguồn; ngoài tài liệu bị từ chối; đọc/xóa hội thoại | Đạt chức năng, có suy giảm dịch vụ |
| Sinh đề AI | Sinh 3 câu dễ bằng Gemini, kiểm tra đáp án/bằng chứng và duyệt lưu | Đạt trong mẫu thử |
| Thanh toán | Tạo đơn 10.000đ trên VNPay Sandbox; đơn chờ chưa cấp quyền học | Đạt bước khởi tạo |
| Báo cáo | Lọc giao dịch theo 4 trạng thái, từ chối bộ lọc sai; 5 loại CSV và xuất từ giao diện | Đạt |
| Bảo vệ dữ liệu | Không cho xóa khóa đã có học viên | Đạt |
| Mobile | Trang tiến độ của hai học viên ở chiều rộng 390px | Không tràn ngang |

“Đạt” được xác định theo phạm vi thao tác và điều kiện đã kiểm tra, không đồng nghĩa đã kiểm tra mọi biến thể của chức năng đó.

## 5. Số liệu học tập thu được từ thao tác trực tiếp

### Quiz chính thức

Hai học viên cùng làm đề 6 câu. Bộ kiểm tra chọn phương án theo **nội dung đúng sau khi đảo**, không cố định chữ A/B/C/D.

| Học viên | Lượt 1 | Lượt 2 | Lượt 3 | Điểm chính thức cuối | Tiến độ bài học |
|---|---:|---:|---:|---:|---:|
| Em | 0/6 — 0% | 3/6 — 50% | 6/6 — 100% | 100% | 2/2 — 100% |
| Phương | 0/6 — 0% | 3/6 — 50% | 6/6 — 100% | 100% | 2/2 — 100% |

- Tổng cộng **6 bài nộp, 36 câu trả lời**, 18 câu đúng và 18 câu sai theo kịch bản chủ động chọn.
- Mức thay đổi lượt đầu → lượt cuối là **+100 điểm phần trăm/người**.
- Hai lượt đầu chưa đạt ngưỡng 70%; lượt cuối đạt. Đáp án đúng được ẩn ở hai lượt đầu và hiện ở lượt cuối.
- API phân tích trả đúng `avg_quiz_score=100`, `completion_pct=100`, `quiz_attempts=3` cho từng học viên.
- Thời gian xem video là **0 giây** trong khóa test: bài không có video và được hoàn thành bằng nút đánh dấu. Không dùng số liệu này để suy ra thời gian học thực tế.

### Ôn tập và gợi ý cá nhân hóa

| Học viên | Trước ôn | Sau ôn | Thay đổi API ghi nhận | Gợi ý ôn chương |
|---|---:|---:|---:|---|
| Em | 0/6 — 0% | 6/6 — 100% | +100 điểm phần trăm | 1 mục cần ôn → 0 mục |
| Phương | 3/6 — 50% | 6/6 — 100% | +50 điểm phần trăm | 1 mục cần ôn → 0 mục |

Có thêm **4 bài ôn, 24 câu trả lời**. Hệ thống giữ điểm chính thức ở 100% và cập nhật đánh giá kiến thức theo lượt ôn mới. Mỗi bài chỉ có 3 câu trong đề chính thức, dưới ngưỡng 5 câu để phân loại; giao diện hiển thị “Chưa đủ dữ liệu”, trong khi chương có 6 câu nên đủ điều kiện đánh giá.

**Đây là số liệu kiểm thử có kiểm soát, không phải bằng chứng AI giúp học viên tăng năng lực.** Đáp án được chọn theo kịch bản và ôn lại cùng bộ câu hỏi.

Bằng chứng: [Em — 0%](functional-student_em-score-0.png), [Em — 100%](functional-student_em-score-100.png), [Phương — 50%](functional-student_phuong-score-50.png), [mobile](functional-student_em-mobile.png).

## 6. AI: kết quả và độ trễ

### AI Tutor

| Tài khoản | Câu hỏi | Thời gian | Kết quả |
|---|---|---:|---|
| Em | Biến trong Python dùng để làm gì? | 45,51 giây | Trả lời đúng định nghĩa, kèm tài liệu nguồn |
| Phương | Biến trong Python dùng để làm gì? | 61,29 giây | Trích xuất dự phòng; thông báo AI tạm gián đoạn, vẫn có nguồn |
| Em | Ai vô địch World Cup năm 2018? | 0,114 giây | Từ chối vì ngoài tài liệu |
| Phương | Ai vô địch World Cup năm 2018? | 0,115 giây | Từ chối vì ngoài tài liệu |

Trong **2 câu hỏi trong phạm vi**, có **1 lần fallback**. Đây là mẫu rất nhỏ, chỉ phản ánh lần chạy này. HTTP 200 không có nghĩa lời gọi LLM luôn thành công: ở lần fallback, người học nhận được nội dung trích xuất thay vì câu trả lời LLM.

Tài liệu TXT được lập chỉ mục thành **2 đoạn** trong **3,65 giây**. Nguồn trả về cho câu hỏi Python có điểm truy hồi **0,7236**. Bốn hội thoại test đã được xóa.

### Sinh đề AI

- Model được API ghi nhận: `gemini:gemini-3.1-flash-lite`.
- Yêu cầu **3 câu dễ**, nhận **3/3 câu**, thời gian **9,31 giây**; duyệt lưu thành công.
- Cả 3 câu có 4 phương án, đáp án nằm trong danh sách phương án, bằng chứng từ tài liệu và đáp án xác minh trùng đáp án đề xuất.
- Metadata: `verified=3`, `unverified=0`, `flagged=0`, `ungrounded=0`, `difficulty_flagged=0`.
- Đối chiếu thủ công nội dung của 3 câu: định nghĩa biến, kiểu `str`, hàm `len` phù hợp với tài liệu. Chưa đánh giá mức trung bình/khó hoặc một tập câu hỏi lớn.

## 7. Thanh toán và số liệu quản trị

Đã tạo một đơn test **10.000đ** cho Em, cổng **`sandbox.vnpayment.vn`**. Tham số số tiền gửi cổng là **1.000.000**, đúng quy tắc VNPay nhân 100. Đơn chưa trả tiền không cấp quyền học. Đăng ký miễn phí khóa có phí bị từ chối bằng **HTTP 402**.

**Chưa thực hiện thanh toán tại cổng, IPN/return thành công, đối soát thật hoặc hoàn tiền thật trong đợt này.** Các chức năng đó không được tính là đã xác minh đầu cuối. Đơn chờ test đã được xóa khi dọn khóa test.

Các CSV được xuất lại sau khi dọn dữ liệu test:

| Báo cáo | Số dòng dữ liệu | File |
|---|---:|---|
| Giao dịch | 32 | [payments CSV](functional-export-payments.csv) |
| Ghi danh | 25 | [enrollments CSV](functional-export-enrollments.csv) |
| Khóa học | 11 | [courses CSV](functional-export-courses.csv) |
| Học tập theo khóa | 11 | [learning CSV](functional-export-learning.csv) |
| Chủ đề yếu đủ điều kiện thống kê | 9 | [topics CSV](functional-export-topics.csv) |

## 8. Thống kê thực thi và hiệu năng

| Phép đo | Giá trị |
|---|---:|
| HTTP request được ghi lại | 219 |
| Kịch bản API duy nhất, lấy kết quả lần kiểm tra cuối | 178/178 đạt |
| Lượt chạy bước giao diện, gồm thử lại | 49 |
| Kịch bản giao diện duy nhất, lấy lần kiểm tra cuối | 35/35 đạt |
| Đối chiếu số liệu/ngữ nghĩa bổ sung | 11/11 đạt |
| Request API ngoài nhóm `/api/ai/*` được đo | 194 |
| Trung vị API ngoài nhóm AI | 16,6 ms |
| P95 API ngoài nhóm AI, phương pháp nearest rank | 118,4 ms |
| Lớn nhất API ngoài nhóm AI | 702,7 ms |

Các request thường gồm đọc, ghi, đăng nhập và kiểm tra bị từ chối theo quyền. Chạy tuần tự trên local, không phải kiểm thử tải; không suy rộng thành khả năng chịu số người dùng đồng thời. Thời gian bước giao diện có thêm thời gian chờ của script, không được dùng làm chỉ số tải trang.

Nhật ký thô vẫn giữ các lần bộ kiểm tra sai giả định, để có thể truy vết:

- 1 request bị đánh dấu không đạt vì script dự kiến 403 khi đăng ký miễn phí khóa có phí; API thực tế trả đúng nghiệp vụ bằng 402. Đã kiểm tra lại với 402.
- 4 bước giảng viên ban đầu dùng bộ chọn bảng trong khi giao diện dùng thẻ khóa học; đã sửa script và thử lại thành công.
- 2 bước đăng xuất học viên ban đầu tìm nút desktop trong khi đang ở viewport mobile; đã chuyển về desktop và thử lại thành công. Chưa dùng lần thử lại này để kết luận riêng về menu đăng xuất mobile.

Đây là lỗi của công cụ kiểm tra, không được báo thành lỗi ứng dụng và không bị xóa khỏi nhật ký. Riêng vấn đề AI fallback/độ trễ vẫn được ghi nhận dù hợp đồng API đáp ứng.

## 9. Tình trạng sau khi dọn dữ liệu test

Đã dọn 2 khóa test cùng chương, bài, câu hỏi, **10 bài làm**, dữ liệu tiến độ, gợi ý và mốc ôn tập liên quan; xóa tài liệu TXT, 4 hội thoại, 1 đơn VNPay chờ và 2 tài khoản tạm.

| Chỉ số đối chiếu | Trước | Sau dọn |
|---|---:|---:|
| Tài khoản | 15 | 15 |
| Khóa học | 11 | 11 |
| Học viên | 10 | 10 |
| Ghi danh | 25 | 25 |
| Giao dịch thành công / thất bại / hoàn tiền / chờ | 18 / 12 / 2 / 0 | 18 / 12 / 2 / 0 |
| Doanh thu | 11.782.000đ | 11.782.000đ |
| Lượt quiz chính thức | 104 | 104 |
| Điểm quiz tổng hợp | 78,4% | 78,4% |
| Câu hỏi AI lưu trong lịch sử | 9 | 9 |

Các trường tổng quan báo cáo kinh doanh và học tập trước/sau khớp hoàn toàn. Không sửa mã nguồn ứng dụng trong đợt kiểm tra này.

## 10. Việc nên ưu tiên tiếp theo

1. **AI Tutor:** tìm nguyên nhân retry/timeout khiến chờ 45–61 giây; hiển thị trạng thái chờ rõ và đo riêng tỷ lệ lỗi nhà cung cấp với tỷ lệ dùng dự phòng.
2. **Bộ test cũ:** 5 test pytest thất bại trong báo cáo trước cần cập nhật cho token lượt làm, đảo phương án, `ContentBased` và giới hạn offline. Không bỏ cơ chế bảo vệ để làm test cũ đạt.
3. **Build frontend:** xử lý hai cảnh báo `@import` font trong `@layer` và cân nhắc chia bundle JavaScript ~1,05 MB; đây là phát hiện từ lượt build trước, chưa sửa hoặc đo lại ở đợt này.
4. **Trước khi demo:** rà soát khóa rỗng `PYTEST Course`, đặt ngưỡng đạt cho quiz khi nghiệp vụ yêu cầu và kiểm tra từng URL video/tài liệu.
5. **Phạm vi chưa thực hiện:** thanh toán/hoàn tiền đầu cuối; xem video đến hết và tự lưu tiến độ; nhập Word qua UI; upload PDF/DOCX qua UI; bộ đề AI trung bình/khó; kiểm thử tải và trình duyệt khác.

## 11. Tệp bằng chứng

- [Danh sách từng kịch bản, mở bằng Excel](functional-account-checks.csv).
- [Số liệu tổng hợp máy đọc được](functional-account-summary.json).
- [Nhật ký API đầy đủ, không lưu token/mật khẩu](functional-account-api.json).
- [Nhật ký thao tác giao diện và các lần thử lại](functional-account-browser.json).
- [Snapshot trước, trong, sau kiểm thử](functional-account-state.json).
- [Giảng viên An — báo cáo](functional-teacher_an-reports.png), [admin — giao dịch](functional-admin-payments.png), [Phương — tiến độ](functional-student_phuong-progress.png).

Script dùng cho đợt kiểm thử: `functional-account-audit.py`, `functional-account-browser.cjs`, `build-functional-account-report.py`. Browser script tham chiếu Playwright/Chromium đang cài trên máy này.
