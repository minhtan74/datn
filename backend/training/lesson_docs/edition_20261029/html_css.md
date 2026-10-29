# HTML/CSS — thực hành giao diện dễ dùng

Thực hiện trên một trang thử nghiệm riêng. Quan sát bằng công cụ phát triển, bàn phím và màn hình hẹp; hình ảnh đẹp trên một kích thước chưa đủ chứng minh giao diện dùng được.

## Cấu trúc tài liệu HTML
**Tình huống:** tiếng Việt lỗi hoặc trang co sai trên điện thoại. Dùng tài liệu HTML có charset UTF-8, lang phù hợp và viewport; lưu file đúng encoding.
```html
<!doctype html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Khóa học của tôi</title>
</head>
<body><main><h1>Khóa học</h1></main></body>
</html>
```
**Tự luyện:** đổi title và kiểm tra tên tab, thứ bậc heading và ký tự có dấu. **Hướng giải:** title mô tả trang; h1 mô tả nội dung chính; không dùng tiêu đề chỉ để chọn cỡ chữ.

## Form và bảng biểu
**Tình huống:** input không có nhãn hoặc người dùng không biết lỗi ở đâu. Kết nối label với id; type phù hợp hỗ trợ nhập liệu nhưng server vẫn phải kiểm tra dữ liệu.
```html
<label for="email">Email</label>
<input id="email" name="email" type="email" required>
<button type="submit">Gửi</button>
```
Bảng dùng cho dữ liệu có hàng/cột, không để bố trí toàn trang. Dùng caption và th cho tiêu đề; nội dung dài có thể cần vùng cuộn ngang có kiểm soát.

**Tự luyện:** gửi rỗng, nhập sai và dùng Tab/Enter. **Hướng giải:** thông báo chỉ ra trường cần sửa, vẫn giữ dữ liệu người dùng đã nhập; không truyền trạng thái lỗi bằng màu đỏ đơn độc.

## Semantic HTML
**Tình huống:** div có onclick nhưng không dùng được bằng bàn phím. Dùng button cho hành động và a có href cho điều hướng; không thay tất cả bằng div vì thuận CSS.

**Tự luyện:** trang gồm header, nav, main, section và footer; tạo liên kết bỏ qua điều hướng để tới main. **Hướng giải:** heading phản ánh cấu trúc; mỗi control có tên dễ hiểu. Ảnh mang thông tin cần alt mô tả; ảnh thuần trang trí dùng alt rỗng. Không thêm ARIA thừa để thay thế semantic sẵn có.

## Selector & thuộc tính CSS
**Tình huống:** CSS “không ăn” vì selector không khớp hoặc bị quy tắc khác ghi đè. Kiểm tra Styles/Computed, nguồn stylesheet tải được và tính kế thừa trước khi thêm !important.
```css
.course-card { color: #172033; padding: 1rem; }
.course-card:focus-within { outline: 2px solid #2563eb; }
button:disabled { cursor: not-allowed; opacity: .65; }
```
**Tự luyện:** tạo hai card, đổi một class và giải thích quy tắc nào áp dụng. **Hướng giải:** phân biệt class, id và pseudo-class; khai báo biến CSS cho màu dùng chung. Trạng thái focus không được xóa mà không có cách hiển thị thay thế.

## Box Model & Flexbox
**Tình huống:** phần tử width 100% vẫn tràn vì thêm padding và border. Dùng box-sizing phù hợp và kiểm tra kích thước thực.
```css
*, *::before, *::after { box-sizing: border-box; }
.actions { display: flex; flex-wrap: wrap; gap: .75rem; }
.actions > * { min-width: 0; }
```
Flexbox phù hợp sắp xếp theo một trục. Với chữ dài, xét min-width:0 và overflow-wrap thay vì giấu mọi phần tràn.

**Tự luyện:** đặt tiêu đề rất dài và tăng font. **Hướng giải:** nội dung vẫn đọc được, các nút xuống dòng được, không mất phần cuối do height cố định.

## CSS Grid
**Tình huống:** muốn card tự đổi số cột khi thay đổi vùng chứa. Grid tạo bố cục hai chiều; số cột cần dựa vào bề rộng tối thiểu của nội dung.
```css
.courses {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr));
  gap: 1rem;
}
```
**Tự luyện:** thử 1, 2, 7 card và một tiêu đề dài. **Hướng giải:** card không bị ép hẹp hơn nội dung; thứ tự DOM vẫn đúng thứ tự đọc. Tránh dùng thuộc tính order chỉ để sửa cấu trúc HTML đang sai ý nghĩa.

## Media Query
**Tình huống:** breakpoint được chọn theo tên thiết bị nhưng nội dung vẫn tràn giữa hai kích thước. Chọn điểm đổi bố cục khi nội dung cần, kiểm tra cả kích thước ở giữa.
```css
.layout { display: block; }
@media (min-width: 48rem) {
  .layout { display: grid; grid-template-columns: 14rem 1fr; gap: 1rem; }
}
```
**Tự luyện:** thử 390px, 768px và 1280px, cả phóng to chữ. **Hướng giải:** không chỉ thu nhỏ ảnh desktop. Thử người dùng muốn giảm chuyển động trước khi thêm animation dài; thông tin chính không phụ thuộc hover.

## Mobile First Design
**Tình huống:** màn hình nhỏ có quá nhiều nút và sidebar che nội dung. Thiết kế cấu trúc đơn cột dễ đọc trước, sau đó mở rộng. Menu phải mở/đóng được bằng bàn phím, có trạng thái và trả focus hợp lý khi đóng.

**Tự luyện:** form đăng ký với nhãn dài, lỗi dài, tên khóa dài và trạng thái đang gửi. **Hướng giải:** input không làm cả trang tràn ngang; bàn phím ảo không che hành động chính; nút có vùng chạm dễ dùng. Không giấu thông tin bắt buộc chỉ để ảnh chụp gọn hơn.

## Dự án: Landing Page Responsive
**Bài thực hành:** trang giới thiệu khóa học gồm lợi ích, đề cương, giảng viên mẫu và form liên hệ giả lập. Ghi rõ dữ liệu minh họa, không bịa chứng nhận hay lượt học viên như số liệu thật.

**Tự luyện:** kiểm tra liên kết, form lỗi, bàn phím, ba chiều rộng và mất ảnh. **Hướng giải:** báo cáo ghi trình duyệt/kích thước đã thử, lỗi còn lại và bằng chứng. Ảnh có width/height hợp lý, không tải ảnh khổng lồ chỉ để thu nhỏ bằng CSS. Một checklist đạt phải có tiêu chí cụ thể, không dùng “đẹp” làm kết quả kiểm thử duy nhất.

# Tài liệu tham khảo
https://developer.mozilla.org/en-US/docs/Learn_web_development
