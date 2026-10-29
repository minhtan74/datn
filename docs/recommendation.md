# Gợi ý học tập theo nội dung bài kiểm tra

Cập nhật 22/10/2026. Hệ thống dùng quy tắc Python trên dữ liệu đúng/sai từng câu. Không dùng LLM để kết luận năng lực; nhập tay, Word và AI dùng chung quy tắc sau khi giáo viên duyệt câu hỏi.

## Gợi ý theo chương và bài học — ba cấp kiểm tra

Trang kết quả quiz hiển thị **Bạn nên ôn phần nào?** theo cây **Chương → Bài học → Nút ôn**, dựa trên câu trả lời của chính lượt đang xem. Chương/bài cần củng cố được ưu tiên; phần dưới 5 câu có câu sai vẫn hiện để ôn nhưng ghi **Chưa đủ dữ liệu**. Mỗi mục có số câu đúng/tổng, tỷ lệ đúng và liên kết ôn nội dung còn tồn tại. Nút **Xem câu sai** dẫn tới từng câu sai tương ứng trong trang kết quả. Bài cần củng cố vẫn hiển thị khi tổng chương đạt ngưỡng. Các phần còn lại, bảng kết quả chi tiết và gợi ý hiện tại từ tất cả quiz trong khóa được thu gọn. Không suy luận về nội dung chưa có câu hỏi; gợi ý tổng hợp có thể khác kết quả của lượt cũ đang xem.

Câu hỏi có `knowledge_chapter_id` và `knowledge_lesson_id`. Giảng viên chọn ngay trong form soạn câu hỏi hoặc thẻ duyệt Word/AI; API kiểm tra chương/bài thuộc đúng khóa và đúng phạm vi bộ ôn tập. Sinh AI theo chương/đề cuối khóa giữ mã chương của từng câu và đề nghị mã bài từ danh sách cho phép; giảng viên cần kiểm tra trước khi duyệt. Câu tổng hợp có thể chỉ gắn chương, không bắt buộc gán một bài không chính xác.

- **Theo bài:** thống kê số câu đúng của bài, dẫn về bài và bộ luyện tương ứng.
- **Theo chương:** cộng số đúng/tổng số câu thuộc chương, thống kê từng bài đã phân loại; ưu tiên bài cụ thể có đủ căn cứ.
- **Cuối khóa/đề tổng hợp:** dùng chương/bài của từng câu, không gán toàn bộ đề cho một chương.

Khi nộp bài, `result_answers` lưu mã và tên chương/bài tại lúc nộp (`knowledge_version=2`). Trang kết quả hiển thị bảng kiến thức của riêng lượt đó, giữ nguyên khi giáo viên sửa phân loại sau này. Gợi ý bên dưới và Dashboard/Tiến độ dùng căn cứ hiện tại: lấy **lượt nộp mới nhất cho từng bài qua mọi loại đề**; kết quả luyện bài mới thay thế căn cứ cũ của bài đó, các bài khác giữ căn cứ gần nhất. Câu chỉ gắn chương có nhóm riêng theo chương và cũng lấy lượt mới nhất. Tổng chương có thể kết hợp các bài được kiểm tra ở các thời điểm khác nhau; không phải điểm chính thức của một đề. Một question ID không được đếm nhiều lần.

Cần 5 câu khác nhau; dưới 70% thì cần củng cố. Dưới 5 câu chỉ đề nghị kiểm tra thêm khi có câu sai. Nếu chương đủ căn cứ nhưng các bài còn ít câu, ưu tiên gợi ý chương. Nếu đã có bài yếu đủ căn cứ, bảng vẫn giữ tổng chương nhưng thẻ hành động ưu tiên bài, tránh gợi ý trùng. Có tối đa 3 hành động chương/bài ưu tiên; các phần còn lại xem trong bảng kiến thức. Gợi ý chủ đề cũ được dùng cho phần chưa được bao phủ bởi căn cứ chương/bài.

Nút làm bài luyện chỉ hiện khi bộ luyện hiện có có câu hỏi, học viên còn ghi danh và còn lượt hoặc có thể tiếp tục lượt đang làm. Chưa có bộ luyện bài thì có thể dẫn sang bộ luyện của chương, ghi rõ **Luyện cả chương**; không tự tạo đề hoặc gọi AI khi học viên bấm gợi ý. Phần giải thích nhắc luyện câu tương đương để giảm ảnh hưởng nhớ đáp án; hiện chưa tự thay bộ câu hỏi cho mỗi lượt.

Mở ôn bài/chương hoặc bài luyện ghi checkpoint riêng cho phần kiến thức. Sau bài mới, phần trước/sau so sánh đúng phần đó, báo khác bộ câu và mẫu nhỏ; không sửa điểm cuối khóa hoặc chứng nhận thành thạo. Học tiếp ưu tiên khóa chưa hoàn thành có lượt nộp quiz gần nhất.

Migration `0021_knowledge_scope` đã áp dụng local. Dữ liệu cũ chỉ được khôi phục từ phạm vi đề hoặc tên bài/chương khớp duy nhất (cho phép bỏ tiền tố số bài), ghi `knowledge_version=1` và thông báo giới hạn. Không suy đoán tên đồng nghĩa; các câu chưa rõ vẫn tính điểm và báo chưa phân loại. Trên môi trường khác chạy `alembic upgrade head` trước khi chạy code mới.

Kiểm chứng mới: **98 kiểm thử backend**, **3 kiểm thử Node**, **9 kiểm tra tích hợp trên bản sao MySQL**, **8 kiểm tra Chrome** và build frontend thành công. Xem [báo cáo triển khai](knowledge-recommendations-20261022.md).

## Hai mục đích đánh giá

- **Điểm chính thức:** giữ cấu hình cao nhất/lần đầu/lần cuối/trung bình của từng đề. Bộ ôn tập không tính vào điểm trung bình chính thức.
- **Gợi ý nội dung:** dùng lượt nộp gần nhất của mỗi quiz, bao gồm bài kiểm tra và bộ ôn tập. Một chủ đề được tính riêng theo từng khóa. Không gọi điểm cao nhất trong quá khứ là kiến thức hiện tại.

Tỷ lệ đúng theo chủ đề = số câu đúng / số câu khác nhau có kết quả × 100. Khi đề lấy trung bình nhiều lượt, phần gợi ý vẫn chỉ dùng lượt gần nhất. Câu trả lời ở các bài khác nhau có thể có thời điểm khác nhau; đây chưa phải phép đo năng lực tức thời hoặc đã kiểm chứng học thuật.

## Dữ liệu và ngưỡng

- Dùng `results`, `result_answers`, `questions.topic`, thông tin khóa/bài của quiz và `lesson_progress`.
- Cần ít nhất **5 question ID khác nhau** trong mỗi chủ đề để phân loại. Làm lại một câu nhiều lần không tăng số câu làm căn cứ.
- Dưới 5 câu: `Insufficient` — Chưa đủ dữ liệu; hiện số câu đúng/tổng số câu, khuyến khích luyện thêm.
- Từ 5 câu: dưới 50% Yếu; từ 50% đến dưới 70% Trung bình; từ 70% đến dưới 85% Khá; từ 85% Tốt. Dưới 70% ưu tiên ôn tập.
- Các ngưỡng là quy tắc cấu hình ban đầu (`MIN_TOPIC_QUESTIONS`, `TOPIC_REVIEW_THRESHOLD`), không phải chuẩn năng lực được nghiên cứu xác nhận.
- Tên chủ đề chuẩn hóa Unicode NFC, khoảng trắng và chữ hoa/thường; không tự suy đoán hai tên khác nghĩa là cùng chủ đề. Không gộp chủ đề cùng tên của hai môn.
- Câu không có chủ đề vẫn tính điểm tổng, được báo số lượng thiếu phân loại, không đưa vào nhóm kiến thức.
- Thời gian xem video không được cộng vào điểm kiến thức. Tiến độ chỉ dùng chọn bài chưa hoàn thành tiếp theo.

## Nội dung gợi ý

Ví dụ: “Bạn trả lời đúng 2/6 câu về Đồng bộ hóa (33,3%) trong khóa HĐH. Ôn bài Các giải pháp đồng bộ hóa.”

Ưu tiên tối đa 3 chủ đề cần củng cố, sau đó gợi ý làm lại đề, tối đa 2 chủ đề cần thêm dữ liệu, thông báo thiếu phân loại và bài học tiếp theo. Giao diện dashboard có nút xem tất cả để các mục phía sau không bị ẩn vĩnh viễn. Toàn bộ điểm theo chủ đề xem ở trang Tiến độ.

Thẻ gợi ý dùng nhãn `ContentBased` (Theo chủ đề) hoặc `Insufficient` (Chưa đủ dữ liệu); không xếp hạng chung con người bằng trung bình mọi môn. Nhãn Yếu/Trung bình/Khá/Tốt chỉ dành cho kết quả nội dung có đủ số câu. Điểm chính thức vẫn hiển thị riêng ở phần phân tích tổng quan.

## Danh mục chủ đề và liên kết ôn tập

Mỗi khóa có danh mục `course_topics`, tên chuẩn hóa duy nhất và mã chủ đề. Các câu nhập tay, Word và AI chọn cùng danh mục. API kiểm tra chủ đề thuộc đúng khóa; client cũ gửi tên vẫn được đối chiếu theo Unicode/khoảng trắng/chữ hoa-thường. Không tự gộp các tên khác nghĩa.

Giảng viên chọn hoặc thêm chủ đề ngay trong form soạn câu hỏi, nhập Word và duyệt câu AI. Trang quản lý **Chủ đề kiến thức** riêng đã được gỡ; đường dẫn cũ `/teacher/topics` chuyển về `/teacher/quizzes`. Phân loại câu hỏi, kết quả đã lưu và gợi ý theo chủ đề vẫn được giữ.

Các liên kết bài học/bộ ôn tập đã xác nhận trước đây tiếp tục được sử dụng. Giao diện hiện không có bước tạo hoặc xác nhận liên kết riêng; chủ đề mới dùng thông tin bài học của câu hỏi hoặc liên kết về danh sách bài trong khóa khi chưa xác định được bài cụ thể. API quản lý liên kết vẫn kiểm tra bài học cùng khóa và bộ ôn có câu hỏi cùng chủ đề.

Gợi ý ưu tiên liên kết được xác nhận. Nếu chưa có liên kết xác nhận, chỉ dùng nguồn bài học rõ ràng hoặc tên bài trùng chính xác, không đoán theo từ khóa; khi không rõ thì dẫn đến danh sách bài trong khóa. Nút **Làm bài luyện** chỉ hiện với liên kết bộ ôn tập được xác nhận, có câu cùng chủ đề, còn quyền truy cập và còn lượt hoặc có lượt đang làm có thể tiếp tục.

## Căn cứ và lịch sử phân loại

Nút **Vì sao có gợi ý này?** hiện số câu đúng/tổng, ngưỡng, tình trạng xác nhận, đề làm căn cứ, thời điểm nộp và link kết quả. Gợi ý làm lại đề có cách tính điểm và số lượt đã dùng/còn lại.

Từ phiên bản này, `result_answers` lưu mã và tên chủ đề tại lúc nộp (`classification_version=2`). Sửa chủ đề của câu hỏi về sau không đổi phân loại của kết quả cũ. Dữ liệu trước migration chỉ có thể khôi phục theo thông tin câu hỏi ở thời điểm migration (`classification_version=1`), được nêu rõ trong phần căn cứ; không khẳng định đã biết phân loại chính xác tại thời điểm nộp trong quá khứ.

## So sánh trước/sau khi mở gợi ý ôn

Khi học viên bấm **Ôn bài học / Xem bài học / Làm bài luyện** ở một gợi ý có mã chủ đề, hệ thống lưu checkpoint: căn cứ hiện tại và mốc kết quả gần nhất. Bấm lại khi chưa có kết quả mới không tạo thêm mốc giống nhau.

Phần **Kết quả trước/sau khi mở gợi ý ôn** hiển thị tối đa 10 mốc gần nhất. Chỉ lấy kết quả nộp mới sau checkpoint của chính học viên, cùng chủ đề và khóa còn ghi danh. Chưa có bài mới thì báo đang chờ. Có bài mới thì hiện số câu đúng/tổng và chênh lệch **điểm phần trăm**. Báo rõ hai mốc có cùng bộ câu hay không và có đủ 5 câu ở cả hai mốc không.

Đây là thay đổi quan sát được sau khi mở gợi ý, không phải bằng chứng học viên đã học xong hoặc việc ôn gây ra cải thiện. Cùng câu có thể nhớ đáp án; khác câu có thể khác độ khó. Không dùng chênh lệch này để tự động chứng nhận thành thạo.

## Gợi ý làm lại đề

Dùng chính `_graded` và `_attempts_used` của luồng quiz để khớp điểm được tính, điểm đạt lưu lúc nộp và số lượt đã dùng (kể cả bỏ dở).

- Gợi ý khi chưa đạt yêu cầu đề **hoặc** điểm được tính dưới 70%. Thông báo phân biệt “chưa đạt yêu cầu đề” và “cần luyện thêm”.
- Đề lấy điểm lần đầu không được gợi ý làm lại nhằm tăng điểm chính thức; vẫn có gợi ý ôn chủ đề.
- Hết lượt thì không đề nghị mở lượt mới. Nếu lượt cuối đang làm và chưa hết giờ, nút là “Tiếp tục bài”.
- Chỉ tạo hành động theo khóa còn ghi danh; API theo khóa kiểm tra quyền truy cập.

## API và lưu lịch sử

- `GET /api/recommendations?course_id=` tính từ dữ liệu mới nhất, trả gợi ý và lịch sử.
- `POST /api/recommendations/refresh` tính lại và lưu lịch sử; snapshot không đổi thiếu điểm thành 0.
- `GET /api/analytics/topics` dùng cùng nguồn dữ liệu nội dung với thẻ gợi ý.
- `GET/POST/PUT /api/topics`: quản lý danh mục, kiểm tra quyền chủ khóa/admin.
- `POST /api/recommendations/study`: lưu mốc khi mở gợi ý ôn.
- `GET /api/recommendations/progress`: so sánh các mốc của chính học viên.
- `based_on` lưu phương thức, ngưỡng, số câu chưa phân loại và căn cứ đầy đủ từng chủ đề.

Migration `0019_content_recommendations` thêm trạng thái mới, cho phép điểm snapshot NULL. `0020_topic_catalog` tạo danh mục, lưu phân loại tại lúc nộp và checkpoint ôn tập. Đã áp dụng database local; môi trường khác cần chạy `alembic upgrade head` trước khi dùng code mới.

## Kiểm tra

27 kiểm thử riêng dùng SQLite trong bộ nhớ, cùng 49 kiểm thử Word/sinh quiz/đảo đề: **76 passed**. Kiểm tra dữ liệu thiếu, điểm cao nhưng chủ đề yếu, ngưỡng, điểm đạt/cách tính điểm, lượt bỏ dở/hết hạn/đang làm, cùng tên ở hai khóa, quyền giáo viên, liên kết sai khóa, bộ luyện không có chủ đề, sửa câu hỏi sau khi nộp và so sánh trước/sau. Các test không ghi database demo.

Build frontend thành công. TestClient với MySQL local xác nhận API danh mục, gợi ý, checkpoint/progress, nhập tay/Word/AI, liên kết giảng viên xác nhận và lưu snapshot lúc nộp. Các lượt ghi để kiểm tra được rollback; không thêm điểm hoặc checkpoint giả vào dữ liệu học viên.

[Bộ tình huống và hướng dẫn demo](recommendation-validation.md).

Giao diện gợi ý hiện tại cũng gom thành một danh sách chương, bên dưới là các bài nên ôn có căn cứ từ quiz. Không hiển thị thêm thẻ chương/bài rời trùng nhau. Các liên kết luyện tập hiện có và mốc khi bấm ôn trong gợi ý hiện tại được giữ lại; nếu mới xác định được chương, không tự suy đoán bài yếu.
