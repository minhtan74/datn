# Rà soát chức năng hiện tại sau khi hoàn tác luồng hoàn tiền mới

**Cập nhật sau báo cáo:** các mục 1–4 đã xử lý trong [bản sửa riêng](admin-fixes-1-4.md).
Mục 4 theo quyết định mới là liên hệ Admin quản lý, không dùng SMTP. Nội dung và bằng chứng
bên dưới giữ trạng thái tại thời điểm rà soát trước bản sửa.

Website tải và điều hướng được trong các ca đã kiểm tra, nhưng vẫn có vấn đề nghiệp vụ và
trải nghiệm dưới đây. Đây là rà soát localhost, không phải xác nhận website không còn lỗi.
Không sửa mã chức năng trong lượt này.

## 1. Cao — Luồng hoàn tiền Admin cũ còn rủi ro xử lý trùng và cập nhật dở

- Hai request đồng thời cùng gửi yêu cầu đến cổng trước khi một request bị DB từ chối.
  Tái hiện **2 lần gọi cổng giả lập**, HTTP **200/409**. Không kết luận ngân hàng đã hoàn hai lần.
- Chèn lỗi ở bước thu hồi quyền học: API trả **500**, đơn đã `refunded` nhưng ghi danh vẫn còn.
- Các lỗi này trở lại sau khi hoàn tác luồng mới theo yêu cầu. Chưa dùng tiền thật để kiểm tra.
- Nên sửa chống gửi trùng và lưu/cập nhật kết quả nhất quán trước khi dùng hoàn tiền thật.

Mã: [payments.py](../backend/app/routers/payments.py), hàm `refund`.
Bằng chứng mới: [kiểm tra API](web-health-current-payments.json).

## 2. Vừa — Đối soát hàng loạt không khớp phạm vi đang hiển thị

Sau khi lọc một đơn, nút ghi “Đối soát 1 đơn đang chờ” nhưng request không gửi bộ lọc;
backend chọn toàn bộ đơn chờ. Khi cô lập vào dữ liệu tạm: hiển thị **1** nhưng truy vấn **7** đơn.
Đề nghị phân biệt rõ toàn hệ thống và các đơn trong bộ lọc, kèm đúng số lượng/phạm vi trước thao tác.

Mã: [Payments.jsx](../frontend/src/pages/admin/Payments.jsx), `handleReconcileAll`;
[payments.py](../backend/app/routers/payments.py), `reconcile_pending`.

## 3. Vừa — Chi tiết và số liệu giao dịch Admin có thể hiển thị sai/nghèo thông tin

- API danh sách không trả ngày/lý do/mã hoàn tiền dù DB có; modal hiển thị dấu `—` khi mở lại đơn hoàn.
- Đối soát A → đóng → mở B → phản hồi A về: modal bị thay thành A. Đã tái hiện bằng phản hồi chậm có kiểm soát.
- Tải bộ lọc mới bị lỗi: bảng rỗng nhưng tổng số/doanh thu cũ vẫn còn; tái hiện tổng **40** vẫn hiển thị cùng lỗi HTTP 500.

Nên trả đủ dữ liệu chi tiết, ràng buộc phản hồi theo đơn/modal hiện tại và đánh dấu/ẩn số liệu cũ khi lỗi.
Bằng chứng: [kiểm tra trình duyệt Admin](web-health-current-admin-payments-browser-audit.json),
[modal đổi nhầm đơn](web-health-current-admin-payments-stale-detail.png),
[số liệu cũ khi lỗi](web-health-current-admin-payments-stale-totals.png).

## 4. Cao khi triển khai — Quên mật khẩu chưa gửi được email trong cấu hình local hiện tại

Form và các API đã có, liên kết từ đăng nhập trỏ đúng `/forgot-password`; kiểm thử khôi phục đạt.
Tuy nhiên, kiểm tra cấu hình chỉ xác nhận có/không cho thấy **chưa có SMTP host/from**, nên
hệ thống không gửi thư ra ngoài ở môi trường này. Thông báo công khai vẫn chung để bảo vệ email.

Đây là cấu hình chưa hoàn tất, không phải lỗi còn thiếu form như báo cáo cũ.
Xem [hướng dẫn SMTP](password-recovery.md). Không đọc/in mật khẩu SMTP hay token trong báo cáo.

## 5. Vừa — Câu trả lời AI chưa hiển thị code/nguồn thuận tiện

Tái hiện bằng phản hồi giả lập: dấu code fence như ` ```python ` xuất hiện nguyên văn,
không có `pre code`; nguồn là nhãn chữ, không mở được tài liệu hoặc trang nguồn.
Cả AI Tutor và khung AI bài học đang dùng cách hiển thị văn bản tương tự.

Đề nghị hỗ trợ định dạng Markdown/code có kiểm soát và liên kết nguồn đã kiểm tra quyền truy cập.
Ca này kiểm tra renderer, **không đánh giá lại độ chính xác kiến thức của AI**.
Mã: [AiTutor.jsx](../frontend/src/pages/student/AiTutor.jsx), [Lesson.jsx](../frontend/src/pages/Lesson.jsx).
Bằng chứng: [kết quả](web-health-current-browser.json), [ảnh](web-health-current-ai-format.png).

## 6. Vừa về nghiệp vụ — Hướng dẫn hỗ trợ/hoàn tiền còn thiếu thông tin áp dụng

Luồng hiện tại yêu cầu Học viên liên hệ Admin bên ngoài website; chưa có luồng gửi yêu cầu
trong web sau lần hoàn tác, và chưa có chính sách hoàn tiền tự kiểm tra theo thời hạn/tiến độ.
Footer còn hotline **`1900 xxxx`**; email hỗ trợ có hiển thị nhưng lượt kiểm tra này không xác minh
khả năng nhận/xử lý của hộp thư đó. Người học cần một kênh hỗ trợ đã xác nhận và chính sách rõ ràng.

Luồng liên hệ Admin có thể tiếp tục dùng; không bắt buộc xây lại chức năng yêu cầu hoàn tiền.
Mã: [Footer.jsx](../frontend/src/components/layout/Footer.jsx).

## Phạm vi và số liệu

| Kiểm tra mới trong lượt này | Kết quả |
|---|---|
| Tải trang, 5 tài khoản mẫu và khách, desktop/mobile | **101 lượt xem**, 0 JavaScript exception, 0 tràn ngang, 0 trang lỗi API thông thường, 0 ảnh hỏng |
| Đăng nhập giao diện và quyền truy cập | **12/12 kiểm tra đạt** |
| Backend, tắt LLM trong tiến trình test | **241 đạt, 4 chưa đạt, 2 không chọn chạy** |
| API giao dịch chuyên sâu, dữ liệu tạm/cổng giả lập | 28 phép kiểm tra, gồm xác nhận 4 nhóm lỗi; không phải 28 ca chứng nhận không lỗi |
| Giao diện Admin giả lập lỗi/chậm | 18 phép kiểm tra, tái hiện 3 vấn đề |
| Mở form trống Admin/Giảng viên desktop/mobile | 6 trường hợp, nút đóng đều thao tác được; không có bằng chứng lỗi che nút ở các form này |
| Kiểm tra lại lỗi đã sửa | Trang kết quả thanh toán không còn kết luận thất bại khi pending/mất mạng; breadcrumb không ghi nhận lặp ở các lượt xem |

### Bốn ca backend chưa đạt

1. `test_full_learning_flow`: bài nộp thiếu `attempt_token`, không có `score`.
2. `test_answers_hidden_until_last_attempt_and_fair_analytics`: kỳ vọng phản hồi/đáp án cố định không còn phù hợp luồng lượt làm hiện tại.
3. `test_recommendation_flow`: chỉ chấp nhận nhóm điểm cũ, không chấp nhận `ContentBased`.
4. `test_ai_generate_and_approve_quiz`: yêu cầu medium khi cấu hình offline chỉ hỗ trợ easy.

Đây là các bất đồng hợp đồng/giả định của test; không tự quy thành 4 chức năng người dùng đang hỏng.
Những kiểm thử chuyên biệt quiz shuffle, difficulty, knowledge, recommendations, khôi phục mật khẩu,
Word import và AI clarification đều đạt trong lượt chạy này.
Hai test AI cũ không chạy vì cleanup có thể xóa lịch sử của tài khoản mẫu theo email.
Khi cập nhật test, cần sửa cleanup trước khi bật lại trên DB có dữ liệu.

Các cảnh báo build font/CSS và bundle lớn đã ghi nhận trước đây vẫn là nợ kỹ thuật;
lượt này không thay mã frontend nên không chạy lại build. Bản build gần nhất sau hoàn tác đã thành công.

Không thực hiện chuyển/hoàn tiền thật. Chặn request ghi từ các lượt duyệt trang thông thường;
test backend và test chuyên sâu chỉ tạo/dọn dữ liệu theo khóa học/tài khoản tạm.
Không gửi câu hỏi đến nhà cung cấp LLM thật trong lượt kiểm tra renderer và suite offline.

Bằng chứng: [tải trang](web-health-current-browser.json), [JUnit](web-health-current-tests.xml),
[API giao dịch](web-health-current-payments.json), [form](web-health-current-modals.json).
