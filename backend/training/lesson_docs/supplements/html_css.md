## HTML và CSS — Học thêm về khả năng truy cập và responsive
Tài liệu thực hành nối tiếp HTML, form, semantic, Flexbox, Grid và mobile first. Mục tiêu là một trang dùng được bằng chuột, bàn phím và màn hình nhỏ.

## Mục tiêu học thêm
- Chọn phần tử theo ý nghĩa và hành vi mặc định
- Giải thích kích thước theo box model
- Tạo bố cục responsive và kiểm tra tràn nội dung

## 1. HTML có ngữ nghĩa
Một nút thao tác nên là button, một liên kết điều hướng nên là a có href. Dùng div giả nút sẽ phải tự thêm xử lý bàn phím và các trạng thái mà button có sẵn. Dùng heading theo cấu trúc nội dung, không chọn h1 hay h3 chỉ vì kích thước chữ; kích thước được chỉnh bằng CSS.
```html
<main>
  <h1>Đăng ký khóa học</h1>
  <form>
    <label for="email">Email</label>
    <input id="email" name="email" type="email" required>
    <button type="submit">Đăng ký</button>
  </form>
</main>
```
Label liên kết với input qua for/id; placeholder không thay thế label vì có thể biến mất khi nhập. required và type=email hỗ trợ kiểm tra trình duyệt nhưng backend vẫn phải kiểm tra dữ liệu. Ảnh truyền đạt nội dung cần alt phù hợp; ảnh trang trí dùng alt rỗng để không gây nhiễu.

## 2. Box model và kích thước thực
Với content-box, width chỉ tính nội dung; padding và border cộng thêm bên ngoài. Với border-box, width bao gồm cả nội dung, padding và border.
```css
*, *::before, *::after { box-sizing: border-box; }
.card {
  width: 300px;
  padding: 20px;
  border: 2px solid #ddd;
}
```
Nếu dùng content-box, chiều rộng ngoài của thẻ trên là 344px, chưa tính margin. Với border-box là 300px. Margin tạo khoảng cách bên ngoài và không nằm trong width. Khi bố cục tràn, dùng DevTools xem hộp thật thay vì thêm overflow:hidden để che lỗi.

## 3. Grid, Flexbox và mobile first
Flexbox thường phù hợp sắp xếp một hàng hoặc cột. Grid thuận tiện cho bố cục có hàng và cột. Không có quy tắc buộc luôn dùng một loại; chọn theo cấu trúc cần kiểm soát.
```css
.courses {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
.course { min-width: 0; overflow-wrap: anywhere; }
img { max-width: 100%; height: auto; }
@media (min-width: 48rem) {
  .courses { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 72rem) {
  .courses { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
```
Mobile first bắt đầu từ bố cục đơn giản cho không gian hẹp rồi mở rộng khi đủ chỗ. Breakpoint nên phản ánh lúc nội dung cần thay bố cục, không phải một danh sách thiết bị cố định. Giữ thứ tự HTML hợp lý; đổi thứ tự bằng CSS có thể khiến thứ tự nhìn thấy khác thứ tự đi bằng phím Tab.

## 4. Form, focus và nội dung dài
Không xóa outline mà không cung cấp dấu hiệu focus thay thế. Thông báo lỗi cần nói trường nào sai và cách sửa, không chỉ đổi màu đỏ. Trạng thái cũng cần chữ hoặc biểu tượng kèm mô tả để không phụ thuộc duy nhất vào màu.
```css
button:focus-visible, a:focus-visible, input:focus-visible {
  outline: 3px solid #1d4ed8;
  outline-offset: 3px;
}
```
Thử trang ở độ rộng 320px, zoom 200%, tiêu đề dài và dữ liệu trống. Bảng dữ liệu lớn có thể cần vùng cuộn ngang riêng thay vì làm toàn trang tràn. Không đặt chiều cao cố định cho khối văn bản nếu nội dung có thể dài hơn.

## Bài tập và hướng dẫn
1. Dễ: tính chiều rộng ngoài của width=200px, padding=10px, border=1px với hai chế độ. Đáp án: content-box 222px; border-box 200px, chưa tính margin.
2. Trung bình: làm form đăng ký có label, input email, nút submit và focus nhìn thấy. Tự kiểm tra chỉ dùng Tab và Enter; mọi phần tử thao tác phải tới được.
3. Khó: xây landing page khóa học gồm header, danh sách khóa và form; giữ hoạt động với tiêu đề dài và zoom 200%. Kiểm tra không mất nội dung khi đổi từ ba cột sang một cột.

## Tiêu chí hoàn thành
Trang có cấu trúc heading rõ; điều hướng dùng liên kết, thao tác dùng nút; ảnh có alt phù hợp; form có label; bàn phím thấy focus; nội dung không bị cắt trên màn hình hẹp. Lưu ảnh chụp và ghi lại kích thước đã thử để chứng minh responsive.

## Nguồn học tiếp
https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/HTML
https://developer.mozilla.org/en-US/docs/Web/CSS/box-sizing
https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
