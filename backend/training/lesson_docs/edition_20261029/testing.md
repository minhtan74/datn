# Kiểm thử phần mềm — thực hành có bằng chứng

Thực hiện trên môi trường lab hoặc dữ liệu được phép. Phân biệt tình huống giả định, lỗi tái hiện thật và phần chưa kiểm tra. Không sửa điểm, thanh toán hoặc dữ liệu người dùng thật để tạo “bằng chứng” kiểm thử.

## Mục tiêu và các mức kiểm thử
**Tình huống:** unit test xanh nhưng người dùng không đăng nhập được. Unit, tích hợp và đầu cuối kiểm tra những ranh giới khác nhau; một mức không tự thay thế các mức còn lại. Chọn mức theo rủi ro và chi phí phản hồi.

**Tự luyện:** phân loại kiểm tra hàm tính điểm, API nộp bài và form nộp bài trong trình duyệt. **Hướng giải:** nêu phụ thuộc được dùng thật hay thay thế; kiểm tra quyền và dữ liệu lưu khi cần. Số test lớn không tự chứng minh đã phủ yêu cầu quan trọng.

## Thiết kế test case
**Tình huống:** test case chỉ ghi “đăng nhập thành công”. Cần điều kiện đầu, dữ liệu, bước hành động, kết quả quan sát được và cách dọn. Kết quả mong đợi phải đủ cụ thể để hai người chấm giống nhau.

**Tự luyện:** viết ca đăng nhập đúng, sai mật khẩu và tài khoản bị khóa. **Hướng giải:** nêu trang/response, trạng thái phiên và quyền sau tải lại; không ghi mật khẩu thật vào báo cáo. “Không crash” chưa đủ chứng minh nghiệp vụ đúng.

## Phân vùng tương đương và giá trị biên
**Tình huống:** điểm hợp lệ 0..10 nhưng chỉ thử 5. Chọn miền hợp lệ, dưới miền, trên miền và dữ liệu không phải số; thử sát biên theo kiểu dữ liệu được hỗ trợ.
```python
def valid_score(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 10

assert valid_score(0) and valid_score(10)
assert not valid_score(-1) and not valid_score(11)
assert not valid_score("5")
```
**Tự luyện:** làm rõ có nhận chuỗi số và NaN không. **Hướng giải:** xác định hợp đồng trước khi kết luận test fail; đổi kiểu dữ liệu có thể thay đổi tập biên.

## Báo cáo lỗi và kiểm thử hồi quy
**Tình huống:** lỗi “thỉnh thoảng” không có môi trường tái hiện. Báo cáo cần bước tối thiểu, dữ liệu giả lập, mong đợi/thực tế, phiên bản và bằng chứng đã loại thông tin nhạy cảm.

**Tự luyện:** mô tả một lỗi giả định rõ nhãn giả định, sau đó viết ca hồi quy. **Hướng giải:** phân biệt retest lỗi vừa sửa với hồi quy khu vực liên quan. Nếu script kiểm thử sai selector, ghi lỗi công cụ và thử lại; không báo thành lỗi ứng dụng, không xóa nhật ký lần đầu để làm báo cáo đẹp.

## SDLC, Agile và chiến lược kiểm thử
**Tình huống:** nhận tính năng quá muộn mới nghĩ dữ liệu kiểm thử. Xem yêu cầu sớm, làm rõ tiêu chí chấp nhận và khả năng quan sát; phân phối kiểm thử suốt quá trình thay đổi.

**Tự luyện:** lập chiến lược một trang cho ghi danh khóa học: phạm vi, rủi ro, mức kiểm tra, dữ liệu và điều kiện kết thúc. **Hướng giải:** ưu tiên quyền, thanh toán và dữ liệu học tập; nêu phần ngoài phạm vi. Không dùng Agile để bỏ tài liệu hoặc dùng “đã test” không có bằng chứng làm điều kiện phát hành.

## Review yêu cầu và truy vết kiểm thử
**Tình huống:** yêu cầu “quiz hoàn thành” chưa rõ là đã mở, đã nộp hay đạt. Làm rõ trạng thái và quy tắc điểm trước khi tạo test. Truy vết nối yêu cầu → ca → kết quả → lỗi, không chỉ đếm dòng trong bảng.

**Tự luyện:** viết tiêu chí cho chưa bắt đầu, đang làm, hết giờ chưa nộp và đã nộp. **Hướng giải:** đạt/chưa đạt là thuộc tính kết quả, không thay thế trạng thái lượt. Nếu mở rồi bỏ dở vẫn tốn lượt theo yêu cầu, test phải xác nhận quy tắc đó thay vì mặc định nộp mới tính lượt.

## Bảng quyết định và tổ hợp điều kiện
**Tình huống:** học viên muốn mua khóa phụ thuộc đăng nhập, trạng thái mở bán, giá và ghi danh hiện tại. Liệt kê điều kiện và kết quả cho tổ hợp quan trọng, phát hiện quy tắc mâu thuẫn hoặc chưa định nghĩa.

**Tự luyện:** bảng gồm khóa miễn phí/có phí, đã/chưa ghi danh và đang/không mở bán. **Hướng giải:** chọn ca kiểm tra mỗi quy tắc; không suy pairwise bảo đảm tìm mọi lỗi tương tác ba điều kiện. Khi số tổ hợp lớn, nêu lý do chọn và rủi ro tổ hợp chưa thử.

## Kiểm thử chuyển trạng thái
**Tình huống:** nộp cùng token hai lần tạo hai kết quả. Mô hình lượt làm gồm mở, đang làm, nộp, hết giờ; mô hình đơn hàng có pending/completed/failed/refunded theo nghiệp vụ. Kiểm tra cả chuyển hợp lệ và bị cấm.

**Tự luyện:** thử nộp lại lượt đã hoàn tất và mở lại lượt đang làm. **Hướng giải:** kết quả chỉ lưu một lần; tải lại không tự tạo lượt mới; kiểm tra số bản ghi và quyền sau thao tác. Chú ý callback lặp, request đến chậm và thao tác ở nhiều tab, không chỉ đường thành công một tab.

## Kiểm thử API và phân quyền
**Tình huống:** UI ẩn nút nhưng API vẫn cho người khác sửa khóa. Kiểm tra theo vai trò và theo tài nguyên thuộc ai, không chỉ đăng nhập/chưa đăng nhập.

**Tự luyện:** dùng tài khoản A tạo tài nguyên lab; B thử đọc/sửa/xóa theo hợp đồng. **Hướng giải:** mã từ chối phù hợp và dữ liệu không đổi; một số API dùng 404 để không tiết lộ sự tồn tại. Với AI Tutor, HTTP 200 có thể chứa lỗi LLM hoặc câu từ chối: chấm nội dung, nguồn và phạm vi riêng, không gọi mọi HTTP 200 là câu trả lời tốt.

## Kiểm thử cơ sở dữ liệu và tính toàn vẹn
**Tình huống:** API báo thất bại nhưng vẫn ghi một nửa giao dịch. Kiểm tra tính nguyên tử, khóa ngoại, unique và dữ liệu sau đường lỗi. Một số thử nghiệm cần transaction hoặc bản sao database lab.

**Tự luyện:** đăng ký trùng, xóa khóa có bài làm và hai request đồng thời trên dữ liệu riêng. **Hướng giải:** không đếm chỉ response; xác nhận số dòng và quan hệ. Chỉ dọn những id do lượt test tạo, không dùng DELETE theo từ khóa rộng trên dữ liệu có thể thuộc người khác.

## Hiệu năng, khả dụng và tương thích
**Tình huống:** “trang nhanh” không có số đo. Xác định môi trường, tải, thời gian đầu/cuối và phân vị; p95 không phải chậm nhất. Kiểm tra khả dụng gồm bàn phím, thông báo lỗi và màn hình hẹp.

**Tự luyện:** đo một tác vụ 20 lần trong điều kiện ghi rõ và liệt kê các trạng thái loading/error/rỗng. **Hướng giải:** báo cả mẫu chậm, không chỉ trung bình; phân biệt thời gian chờ cố ý trong script với độ trễ ứng dụng. Không suy tải đồng thời lớn từ một người chạy local hoặc suy mọi trình duyệt từ một lần thử Chromium.

## Dự án nhỏ: kế hoạch kiểm thử và tự động hóa
**Bài thực hành:** chọn ghi danh hoặc nộp quiz trong lab, tạo 12 ca có quyền/biên/trạng thái, ba test tự động có assertion và báo cáo kết quả. Tách dữ liệu chuẩn bị, hành động, xác minh và cleanup.
```python
def test_valid_boundary():
    assert valid_score(0)
    assert valid_score(10)
```
Đoạn trên chạy sau định nghĩa valid_score của bài biên; không phải test kết nối vào hệ thống thật.

**Hướng giải:** test tự động phải phát hiện được hành vi sai có ý nghĩa, không chỉ khẳng định dữ liệu vừa tự tạo bằng đúng đoạn code tương tự. Ghi rõ test qua, fail, chưa chạy và giới hạn. Kết quả mẫu không phải bằng chứng tác vụ đó đã được chạy thật.

# Tài liệu tham khảo
https://docs.pytest.org/en/stable/how-to/assert.html
