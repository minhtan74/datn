## Vị trí bài học trong khóa
- Khóa học: Kiểm thử phần mềm nhập môn.
- Chương 3: Kiểm thử trong vòng đời phát triển.
- Các bài trong chương: SDLC, Agile và chiến lược kiểm thử; Review yêu cầu và truy vết kiểm thử.
- Đọc lý thuyết, tự làm ví dụ rồi đối chiếu hướng giải; sau đó mới làm quiz. Bài thực hành tổng hợp cuối khóa dùng để kết nối kiến thức giữa các chương.

## Mục tiêu bài học
Phát hiện yêu cầu mơ hồ và liên kết test với mục tiêu nghiệp vụ.

## Kiến thức nền
Review tĩnh có thể áp dụng cho yêu cầu, thiết kế, test case và mã nguồn. Một yêu cầu tốt cần rõ ràng, nhất quán và có thể kiểm chứng. “Trang phải nhanh” cần ngữ cảnh đo như thao tác, tải, môi trường và ngưỡng trước khi chuyển thành kiểm thử hiệu năng.

Truy vết nối yêu cầu với test và kết quả hoặc lỗi liên quan. Ma trận có thể đơn giản: mã yêu cầu, ca kiểm thử, trạng thái, mã lỗi. Truy vết giúp nhìn phần chưa có test và xác định test bị ảnh hưởng khi yêu cầu đổi.

Bao phủ yêu cầu không chứng minh bao phủ tất cả rủi ro. Một test gắn mã yêu cầu nhưng không kiểm tra điều kiện quan trọng vẫn có thể bỏ sót lỗi. Review nên tập trung sản phẩm công việc, dùng ví dụ cụ thể và ghi kết luận; tránh biến thành đánh giá cá nhân.

## 1. Checklist review yêu cầu
- Rõ chủ thể, hành động và tài nguyên không?
- Có điều kiện trước, biên và trường hợp lỗi không?
- Thuật ngữ có nhất quán với màn hình và API không?
- Có thể quan sát kết quả bằng quyền và công cụ hiện có không?
- Có xung đột giữa hai yêu cầu hoặc thiếu quyết định nghiệp vụ không?
Ví dụ “người dùng xem được kết quả” cần làm rõ kết quả của ai, vai trò nào, thời điểm nào và có che đáp án trước lượt cuối không.

## 2. Ma trận truy vết tối thiểu
```text
Yêu cầu   Test                Mục tiêu                 Kết quả/Lỗi
REQ-01    RES-OWN             Xem bài của chính mình   Điền sau chạy
REQ-01    RES-OTHER           Chặn bài người khác      Điền sau chạy
REQ-02    RES-HIDE            Che đáp án khi còn lượt  Điền sau chạy
```
Không lấy việc một ô đã có tên test làm chứng cứ test đầy đủ. Kiểm tra xem kỳ vọng có thực sự bám điều kiện của yêu cầu hay chỉ gắn mã để hoàn thành bảng.

## 3. Xử lý yêu cầu đổi
Nếu đổi quy tắc hiện đáp án, tìm test liên quan lịch sử, nộp bài và quyền giảng viên. Cập nhật kỳ vọng có chủ ý và giữ lịch sử phiên bản. Không chỉnh test chỉ để khớp hành vi hiện tại khi hành vi đó chưa được xác nhận đúng.

## 4. Bài tập và lời giải
Viết lại “gợi ý phải chính xác” thành tiêu chí quan sát: đúng phần kiến thức, số câu đúng/tổng, ngưỡng, thiếu dữ liệu và link hợp lệ. Chọn một tiêu chí còn mơ hồ để ghi câu hỏi cho người phụ trách. Đáp án phải nêu được đầu vào minh họa, kỳ vọng cụ thể và giới hạn, ví dụ chưa đủ 5 câu không kết luận yếu.

## Bài tập vận dụng bổ sung
Viết lại yêu cầu “đăng ký dễ dàng” thành hành vi quan sát được. Lập bảng ba yêu cầu với ít nhất hai test mỗi yêu cầu và chỉ rõ bằng chứng cần thu thập.

## Hướng giải bài tập bổ sung
Có test cho đường thành công, lỗi và ràng buộc dữ liệu. Không dùng tỉ lệ test chạy qua làm bằng chứng duy nhất về mức bao phủ.

## Câu hỏi tự kiểm tra
1. Review tĩnh có bắt buộc chạy phần mềm không?
2. Yêu cầu nào cần làm rõ trước khi kiểm thử?
3. Truy vết giúp điều gì khi yêu cầu thay đổi?
4. Một yêu cầu gắn đúng một test có luôn đủ bao phủ không?
5. Review nên tập trung vào đâu?

## Gợi ý đáp án và điểm cần nhớ
- Không. Review sản phẩm công việc có thể diễn ra trước thực thi.
- Trang phải nhanh. Từ nhanh thiếu ngữ cảnh và tiêu chí đo.
- Tìm các test có thể bị ảnh hưởng. Liên kết yêu cầu và test hỗ trợ phân tích tác động.
- Không. Một yêu cầu có thể có nhiều nhánh và điều kiện cần kiểm tra.
- Sản phẩm công việc và bằng chứng cụ thể. Mục đích là cải thiện sản phẩm và phát hiện vấn đề.

## Cách tự đánh giá sau bài
- Giải thích được thuật ngữ mà không đọc lại định nghĩa.
- Thực hiện lại ví dụ với dữ liệu khác và nêu được giới hạn áp dụng.
- Hoàn thành bài tập, đối chiếu bằng chứng hoặc đầu ra với hướng giải.
- Nếu còn nhầm, ghi câu hỏi cụ thể để hỏi giảng viên hoặc AI Tutor cùng ngữ cảnh bài.
Các câu tự kiểm tra có thể trùng trọng tâm quiz. Làm đúng câu đã đọc không tự chứng nhận thành thạo; cần thêm bài vận dụng và minh chứng thực hành.

## Tài liệu đọc thêm
- https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
