=== LESSON 28 ===
## Mục tiêu bài học
- Hiểu HTML là gì và vai trò của nó
- Nắm cấu trúc cơ bản của một tài liệu HTML
- Sử dụng các thẻ tiêu đề, đoạn văn, liên kết, hình ảnh và danh sách

## 1. HTML là gì
HTML (HyperText Markup Language) là ngôn ngữ đánh dấu dùng để mô tả cấu trúc của trang web. HTML không phải ngôn ngữ lập trình vì không có biến, vòng lặp hay điều kiện. Trình duyệt đọc mã HTML và hiển thị nội dung theo các thẻ (tag) được khai báo.

## 2. Cấu trúc tài liệu HTML
Dòng khai báo `<!DOCTYPE html>` cho trình duyệt biết tài liệu dùng chuẩn HTML5. Thẻ gốc của mọi trang web là `html`, bên trong gồm hai phần `head` và `body`. Phần `head` chứa thông tin mô tả trang như `title`, `meta charset` và liên kết tới file CSS. Phần `body` chứa toàn bộ nội dung hiển thị cho người dùng.

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Trang đầu tiên</title>
</head>
<body>
  <h1>Xin chào</h1>
  <p>Đây là đoạn văn.</p>
</body>
</html>
```

## 3. Thẻ và thuộc tính
Một phần tử HTML gồm thẻ mở, nội dung và thẻ đóng, ví dụ `<p>Xin chào</p>`. Thuộc tính (attribute) là thông tin bổ sung đặt trong thẻ mở, ví dụ `href` hoặc `class`. Thẻ tự đóng như `img`, `br` và `input` không có nội dung và không cần thẻ đóng.

## 4. Các thẻ thường dùng
Các thẻ tiêu đề từ `h1` đến `h6`, trong đó `h1` là tiêu đề quan trọng nhất của trang. Liên kết được tạo bằng thẻ `a`, địa chỉ đích nằm trong thuộc tính `href`; thuộc tính `target="_blank"` mở liên kết trong tab mới. Hình ảnh chèn bằng thẻ `img`, đường dẫn ảnh nằm trong `src` và mô tả thay thế nằm trong `alt`. Danh sách không thứ tự dùng `ul`, có thứ tự dùng `ol`, mỗi mục là một thẻ `li`.

```html
<a href="https://example.com" target="_blank">Trang chủ</a>
<img src="logo.png" alt="Logo StudyOnline">
<ul>
  <li>HTML</li>
  <li>CSS</li>
</ul>
```

## Tóm tắt
- HTML mô tả cấu trúc trang; `head` chứa thông tin, `body` chứa nội dung.
- Thuộc tính đặt trong thẻ mở; `a` dùng `href`, `img` dùng `src` và `alt`.
- `ul`/`ol` với `li` tạo danh sách.

## Bài tập vận dụng
1. Tạo trang giới thiệu bản thân gồm tiêu đề, đoạn văn, một ảnh và một danh sách sở thích.
2. Thêm liên kết tới một trang web và cho mở trong tab mới.
3. Giải thích vì sao thuộc tính `alt` của ảnh quan trọng.

=== LESSON 29 ===
## Mục tiêu bài học
- Tạo bảng biểu bằng các thẻ table, tr, th, td
- Xây dựng form nhập liệu với các kiểu input phổ biến
- Gắn nhãn cho ô nhập liệu và hiểu cách form gửi dữ liệu

## 1. Bảng biểu
Bảng trong HTML được tạo bằng thẻ `table`. Mỗi hàng của bảng là thẻ `tr`, ô tiêu đề là thẻ `th` và ô dữ liệu là thẻ `td`. Thuộc tính `colspan` dùng để gộp nhiều cột, thuộc tính `rowspan` dùng để gộp nhiều hàng.

```html
<table>
  <tr><th>Tên</th><th>Điểm</th></tr>
  <tr><td>An</td><td>8.5</td></tr>
  <tr><td>Bình</td><td>7.0</td></tr>
</table>
```

## 2. Form nhập liệu
Form là thành phần dùng để thu thập dữ liệu người dùng, được tạo bằng thẻ `form`. Thuộc tính `action` chỉ địa chỉ nhận dữ liệu, thuộc tính `method` chọn phương thức GET hoặc POST. Thẻ `input` có nhiều kiểu như `text`, `email`, `password`, `checkbox`, `radio` và `submit`.

```html
<form action="/dang-ky" method="post">
  <label for="email">Email</label>
  <input type="email" id="email" name="email" required>
  <label for="pw">Mật khẩu</label>
  <input type="password" id="pw" name="password">
  <button type="submit">Đăng ký</button>
</form>
```

## 3. Thẻ label và các thành phần khác
Thẻ `label` dùng để gắn nhãn cho ô nhập liệu: thuộc tính `for` của `label` trùng với `id` của `input`, bấm vào nhãn sẽ đưa con trỏ vào ô nhập. Ngoài ra còn có `textarea` (nhập nhiều dòng), `select` kèm `option` (danh sách chọn). Thuộc tính `required` bắt buộc nhập, `placeholder` hiện gợi ý.

## 4. GET và POST
GET đưa dữ liệu lên địa chỉ URL, phù hợp để tìm kiếm; POST gửi dữ liệu trong phần thân của yêu cầu, phù hợp với thông tin nhạy cảm như mật khẩu hoặc tạo dữ liệu mới.

## Tóm tắt
- `table`, `tr`, `th`, `td` tạo bảng; `colspan`/`rowspan` gộp ô.
- `form` có `action` và `method`; `input` có nhiều kiểu.
- `label for` gắn với `id` của ô nhập để dễ sử dụng.

## Bài tập vận dụng
1. Tạo bảng thời khoá biểu có gộp ô bằng `colspan`.
2. Tạo form đăng ký gồm họ tên, email, mật khẩu và nút gửi.
3. Giải thích khi nào nên dùng GET, khi nào dùng POST.

=== LESSON 30 ===
## Mục tiêu bài học
- Hiểu Semantic HTML và lợi ích của nó
- Sử dụng các thẻ ngữ nghĩa để dựng bố cục trang
- Phân biệt thẻ ngữ nghĩa với thẻ div và span

## 1. Semantic HTML là gì
Semantic HTML là cách dùng thẻ có ý nghĩa (thẻ ngữ nghĩa) để mô tả đúng vai trò của nội dung thay vì dùng `div` cho mọi thứ. Dùng thẻ ngữ nghĩa giúp trang tốt hơn cho công cụ tìm kiếm (SEO), dễ bảo trì và thân thiện với trình đọc màn hình của người khiếm thị.

## 2. Các thẻ ngữ nghĩa phổ biến
- `header`: phần đầu trang hoặc đầu một khối (logo, tiêu đề).
- `nav`: vùng chứa menu điều hướng.
- `main`: nội dung chính của trang, chỉ có một thẻ `main`.
- `section`: một phần nội dung có chủ đề riêng.
- `article`: nội dung độc lập có thể đứng riêng như bài viết, tin tức.
- `aside`: nội dung phụ như thanh bên, quảng cáo.
- `footer`: phần chân trang hoặc chân khối.

```html
<body>
  <header><h1>StudyOnline</h1></header>
  <nav><a href="/">Trang chủ</a> <a href="/khoa-hoc">Khoá học</a></nav>
  <main>
    <article>
      <h2>Bài viết đầu tiên</h2>
      <p>Nội dung...</p>
    </article>
    <aside>Khoá học nổi bật</aside>
  </main>
  <footer>© 2026 StudyOnline</footer>
</body>
```

## 3. Thẻ div và span
Thẻ `div` là thẻ khối không mang ý nghĩa, chỉ dùng để nhóm nội dung. Thẻ `span` là thẻ nội dòng không mang ý nghĩa, dùng để định dạng một phần văn bản. Chỉ dùng hai thẻ này khi không có thẻ ngữ nghĩa phù hợp.

## 4. Một số thẻ ngữ nghĩa khác
`figure` và `figcaption` cho hình minh hoạ kèm chú thích, `time` cho ngày giờ, `mark` để làm nổi bật văn bản, `strong` và `em` để nhấn mạnh.

## Tóm tắt
- Thẻ ngữ nghĩa mô tả đúng vai trò nội dung, tốt cho SEO và khả năng tiếp cận.
- Bố cục thường gồm `header`, `nav`, `main`, `section`/`article`, `aside`, `footer`.
- `div` và `span` không mang ý nghĩa, chỉ dùng khi không có thẻ phù hợp.

## Bài tập vận dụng
1. Dựng bố cục một trang blog bằng các thẻ ngữ nghĩa thay cho div.
2. Liệt kê ba lợi ích của Semantic HTML.
3. Nêu sự khác nhau giữa `section` và `article`.

=== LESSON 31 ===
## Mục tiêu bài học
- Hiểu CSS là gì và ba cách nhúng CSS vào HTML
- Sử dụng selector theo thẻ, class, id và pseudo-class
- Hiểu độ ưu tiên (specificity) và một số thuộc tính phổ biến

## 1. CSS là gì
CSS (Cascading Style Sheets) là ngôn ngữ dùng để định dạng giao diện cho trang HTML. HTML mô tả cấu trúc nội dung, còn CSS quy định màu sắc, phông chữ và bố cục. Có ba cách nhúng CSS: inline trong thuộc tính `style`, internal trong thẻ `style` và external qua file `.css`. Cách được khuyến khích là external CSS, liên kết bằng thẻ `link` đặt trong phần `head`.

```html
<link rel="stylesheet" href="style.css">
```

## 2. Selector
Selector là mẫu dùng để chọn phần tử HTML cần áp dụng kiểu. Selector theo tên thẻ viết trực tiếp tên thẻ, ví dụ `p` hoặc `h1`. Selector class bắt đầu bằng dấu chấm, ví dụ `.card`; selector id bắt đầu bằng dấu thăng, ví dụ `#header`. Pseudo-class chọn phần tử theo trạng thái, viết sau dấu hai chấm, ví dụ `:hover` áp dụng khi rê chuột lên.

```css
h1 { color: #1d4ed8; }
.card { padding: 16px; border: 1px solid #ddd; }
#header { background: #0f172a; }
a:hover { text-decoration: underline; }
```

## 3. Độ ưu tiên
Độ ưu tiên (specificity) quyết định quy tắc nào được áp dụng khi nhiều quy tắc cùng chọn một phần tử. Thứ tự ưu tiên tăng dần là selector thẻ, selector class, selector id; style inline mạnh hơn cả. Khi hai quy tắc có cùng độ ưu tiên, quy tắc viết sau sẽ được áp dụng.

## 4. Thuộc tính thường dùng
Thuộc tính `color` đổi màu chữ, `background-color` đổi màu nền. `font-size` đặt cỡ chữ, `font-family` chọn phông chữ. Đơn vị `px` là đơn vị tuyệt đối; `rem` là đơn vị tương đối theo cỡ chữ của phần tử `html`. Thuộc tính `display` điều khiển cách phần tử hiển thị: phần tử block như `div` và `p` luôn bắt đầu trên dòng mới, phần tử inline như `span` và `a` nằm trên cùng dòng, `display: none` ẩn hoàn toàn phần tử.

## Tóm tắt
- CSS định dạng giao diện; nên dùng file CSS ngoài.
- Selector: thẻ, `.class`, `#id`, `:hover`; id mạnh hơn class, class mạnh hơn thẻ.
- `display: none` ẩn phần tử; đơn vị `rem` tương đối theo cỡ chữ gốc.

## Bài tập vận dụng
1. Tạo file style.css định dạng tiêu đề, đoạn văn và liên kết cho trang của bạn.
2. Tạo class `.nut` làm nút bấm có đổi màu khi rê chuột.
3. Giải thích điều gì xảy ra khi một phần tử có cả style theo class và theo id.

=== LESSON 32 ===
## Mục tiêu bài học
- Hiểu Box Model và các thuộc tính margin, padding, border
- Sử dụng box-sizing: border-box
- Dựng bố cục một chiều bằng Flexbox

## 1. Box Model
Box Model là mô hình coi mỗi phần tử HTML như một hộp chữ nhật. Hộp gồm bốn lớp từ trong ra ngoài: content, padding, border và margin. Padding là khoảng đệm bên trong viền, margin là khoảng cách bên ngoài viền.

```css
.the {
  width: 300px;
  padding: 16px;
  border: 2px solid #94a3b8;
  margin: 24px auto;
}
```

## 2. Thuộc tính box-sizing
Mặc định `width` chỉ tính phần content, nên thêm padding và border sẽ làm hộp to hơn. Khi đặt `box-sizing: border-box`, chiều rộng đã bao gồm cả padding và border, giúp tính kích thước dễ hơn. Nhiều dự án đặt `* { box-sizing: border-box; }` ngay từ đầu.

## 3. Flexbox
Flexbox là mô hình bố cục một chiều, dùng để sắp xếp các phần tử theo hàng hoặc theo cột. Để bật Flexbox, đặt `display: flex` cho phần tử cha (flex container). Flexbox thường dùng để làm thanh menu, căn giữa phần tử hoặc chia đều khoảng cách.

```css
.menu {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
```

## 4. Các thuộc tính của Flexbox
Thuộc tính `justify-content` căn các phần tử theo trục chính, `align-items` căn theo trục phụ. Thuộc tính `flex-direction` chọn hướng trục chính là `row` (hàng) hoặc `column` (cột). Thuộc tính `flex-wrap: wrap` cho phép các phần tử xuống dòng khi không đủ chỗ. Ở phần tử con, `flex: 1` cho phép phần tử giãn ra chiếm phần không gian còn trống.

## Tóm tắt
- Box Model: content, padding, border, margin.
- `box-sizing: border-box` tính cả padding và border vào chiều rộng.
- Flexbox bố cục một chiều với `justify-content`, `align-items`, `flex-direction`, `flex-wrap`.

## Bài tập vận dụng
1. Tạo thanh menu ngang bằng Flexbox, các mục cách đều nhau.
2. Căn giữa một hộp theo cả chiều ngang và chiều dọc bằng Flexbox.
3. Giải thích khác nhau giữa margin và padding.

=== LESSON 33 ===
## Mục tiêu bài học
- Hiểu CSS Grid và khi nào dùng Grid
- Khai báo lưới bằng grid-template-columns
- Phân biệt Grid và Flexbox

## 1. CSS Grid là gì
CSS Grid là mô hình bố cục hai chiều, chia vùng hiển thị thành hàng và cột. Để bật Grid, đặt `display: grid` cho phần tử cha. Grid phù hợp để dựng bố cục tổng thể của trang hoặc lưới các thẻ nội dung.

## 2. Khai báo cột và hàng
Thuộc tính `grid-template-columns` khai báo các cột, ví dụ `repeat(3, 1fr)` tạo ba cột bằng nhau. Đơn vị `fr` là phần của không gian còn trống trong lưới; `gap` đặt khoảng cách giữa các ô.

```css
.luoi {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
```

## 3. Đặt phần tử vào vùng
Một phần tử có thể chiếm nhiều ô bằng `grid-column: span 2` hoặc được đặt theo đường lưới `grid-column: 1 / 3`. Với bố cục trang, dùng `grid-template-areas` để đặt tên các vùng (`header`, `menu`, `noidung`) rất trực quan.

```css
.trang {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-areas:
    "header header"
    "menu   noidung";
}
.header { grid-area: header; }
```

## 4. Phân biệt Grid và Flexbox
Flexbox là bố cục một chiều, chỉ sắp xếp theo một hàng hoặc một cột tại một thời điểm. Grid là bố cục hai chiều, điều khiển đồng thời cả hàng và cột. Thường dùng Flexbox cho các thành phần nhỏ như menu, dùng Grid cho bố cục tổng thể của trang. Hai mô hình có thể kết hợp với nhau.

## Tóm tắt
- Grid là bố cục hai chiều; bật bằng `display: grid`.
- `grid-template-columns` với `repeat()` và đơn vị `fr` tạo lưới linh hoạt.
- Flexbox cho thành phần nhỏ, Grid cho bố cục tổng thể.

## Bài tập vận dụng
1. Tạo lưới 3 cột hiển thị 6 thẻ khoá học.
2. Dựng bố cục trang có header, thanh bên và nội dung bằng `grid-template-areas`.
3. Nêu ba khác biệt giữa Grid và Flexbox.

=== LESSON 34 ===
## Mục tiêu bài học
- Hiểu Responsive Design và thẻ meta viewport
- Sử dụng Media Query để thay đổi giao diện theo kích thước màn hình
- Hiểu khái niệm điểm ngắt (breakpoint)

## 1. Responsive Design là gì
Responsive Design là kỹ thuật thiết kế giúp trang web hiển thị tốt trên mọi kích thước màn hình, từ điện thoại đến máy tính. Để trang hiển thị đúng tỉ lệ trên điện thoại cần khai báo thẻ meta viewport trong phần `head`. Ảnh co giãn theo khung thường dùng `max-width: 100%`.

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

## 2. Media Query
Media Query là cú pháp CSS dùng để áp dụng kiểu theo điều kiện của thiết bị, bắt đầu bằng `@media`. Ví dụ `@media (max-width: 768px)` chỉ áp dụng kiểu khi màn hình rộng không quá 768px.

```css
.luoi { display: grid; grid-template-columns: repeat(3, 1fr); }

@media (max-width: 768px) {
  .luoi { grid-template-columns: 1fr; }
}
```

## 3. Điểm ngắt
Điểm ngắt (breakpoint) là độ rộng màn hình mà tại đó bố cục thay đổi. Một cách chia phổ biến: dưới 576px là điện thoại, 576 đến 992px là máy tính bảng, trên 992px là máy tính. Nên chọn điểm ngắt dựa trên nơi nội dung bị vỡ chứ không gắn với thiết bị cụ thể.

## 4. Đơn vị linh hoạt
Dùng `%`, `rem`, `vw`, `fr` thay cho `px` cố định để bố cục co giãn tự nhiên. Kết hợp Flexbox với `flex-wrap` hoặc Grid với `repeat(auto-fit, minmax(240px, 1fr))` để tự xuống dòng mà ít cần media query.

## Tóm tắt
- Cần thẻ meta viewport để trang hiển thị đúng trên điện thoại.
- `@media (max-width: …)` áp dụng kiểu theo độ rộng màn hình.
- Chọn điểm ngắt theo nội dung, dùng đơn vị linh hoạt.

## Bài tập vận dụng
1. Làm lưới 3 cột chuyển thành 1 cột khi màn hình nhỏ hơn 768px.
2. Làm thanh menu ngang chuyển thành dọc trên điện thoại.
3. Giải thích vai trò của thẻ meta viewport.

=== LESSON 35 ===
## Mục tiêu bài học
- Hiểu nguyên tắc thiết kế Mobile First
- Viết CSS cho màn hình nhỏ trước rồi mở rộng bằng min-width
- Ưu tiên nội dung quan trọng trên điện thoại

## 1. Mobile First là gì
Mobile First là cách viết CSS cho màn hình nhỏ trước, sau đó mở rộng cho màn hình lớn. Theo cách này, media query thường dùng `min-width` thay vì `max-width`. Lý do: phần lớn người dùng truy cập bằng điện thoại, và thiết kế cho màn hình nhỏ buộc ta tập trung vào nội dung thiết yếu.

## 2. Cách viết
CSS mặc định (không có media query) dành cho điện thoại; các media query `min-width` bổ sung bố cục cho màn hình lớn hơn.

```css
/* Mặc định: điện thoại, một cột */
.luoi { display: grid; gap: 12px; }

/* Máy tính bảng trở lên: hai cột */
@media (min-width: 768px) {
  .luoi { grid-template-columns: repeat(2, 1fr); }
}

/* Máy tính: ba cột */
@media (min-width: 1024px) {
  .luoi { grid-template-columns: repeat(3, 1fr); }
}
```

## 3. Nguyên tắc thiết kế cho điện thoại
- Nội dung quan trọng nhất đặt lên đầu, bỏ bớt phần phụ.
- Nút bấm đủ lớn (khoảng 44px) để chạm bằng ngón tay.
- Cỡ chữ tối thiểu 16px để dễ đọc; giãn dòng hợp lý.
- Hạn chế ảnh nặng; tối ưu ảnh để tải nhanh trên mạng di động.

## 4. So sánh hai hướng
Desktop First viết cho màn hình lớn rồi dùng `max-width` để thu gọn; thường phải ghi đè nhiều quy tắc. Mobile First bắt đầu từ bố cục đơn giản và chỉ thêm khi cần nên CSS gọn hơn và tải nhanh hơn trên điện thoại.

## Tóm tắt
- Mobile First viết CSS cho màn hình nhỏ trước, mở rộng bằng `min-width`.
- Ưu tiên nội dung thiết yếu, nút bấm đủ lớn, chữ dễ đọc.
- CSS thường gọn và tải nhanh hơn so với Desktop First.

## Bài tập vận dụng
1. Viết lại một bố cục Desktop First sang Mobile First.
2. Tạo trang có thanh menu gập gọn trên điện thoại và trải ngang trên máy tính.
3. Nêu ba lợi ích của Mobile First.

=== LESSON 36 ===
## Mục tiêu bài học
- Xây dựng landing page hoàn chỉnh và responsive
- Kết hợp HTML ngữ nghĩa, Flexbox, Grid và media query
- Rèn quy trình làm dự án giao diện từ phác thảo đến hoàn thiện

## 1. Landing page là gì
Landing Page là trang giới thiệu một sản phẩm hoặc dịch vụ với mục tiêu kêu gọi hành động (đăng ký, mua hàng, tải về). Một landing page thường gồm header, phần giới thiệu (hero), tính năng, đánh giá và footer.

## 2. Bố cục các phần
- **Header**: logo và menu điều hướng, dùng Flexbox để căn đều.
- **Hero**: tiêu đề lớn, mô tả ngắn và nút kêu gọi hành động (CTA).
- **Tính năng**: lưới 3 thẻ dùng Grid; trên điện thoại còn 1 cột.
- **Đánh giá**: vài trích dẫn của học viên.
- **Footer**: liên kết phụ và thông tin liên hệ.

## 3. Khung HTML mẫu

```html
<header class="dau-trang">
  <a class="logo" href="#">StudyOnline</a>
  <nav><a href="#tinh-nang">Tính năng</a> <a href="#lien-he">Liên hệ</a></nav>
</header>
<main>
  <section class="hero">
    <h1>Học lập trình trực tuyến</h1>
    <p>Khoá học chất lượng, học mọi lúc mọi nơi.</p>
    <a class="cta" href="#dang-ky">Bắt đầu miễn phí</a>
  </section>
  <section id="tinh-nang" class="luoi-tinh-nang">...</section>
</main>
<footer>© 2026 StudyOnline</footer>
```

## 4. Quy trình thực hiện
Phác thảo bố cục trên giấy, dựng HTML ngữ nghĩa trước, thêm CSS cho màn hình nhỏ, sau đó mở rộng bằng media query. Kiểm tra trên nhiều kích thước bằng công cụ giả lập thiết bị của trình duyệt (F12).

## Tóm tắt
- Landing page gồm header, hero, tính năng, đánh giá, footer với nút CTA nổi bật.
- Flexbox cho menu, Grid cho lưới tính năng, media query cho điện thoại.
- Làm theo thứ tự: phác thảo, HTML ngữ nghĩa, CSS Mobile First, kiểm tra nhiều thiết bị.

## Bài tập vận dụng
1. Hoàn thiện landing page giới thiệu một khoá học của bạn.
2. Thêm hiệu ứng rê chuột cho nút CTA và thẻ tính năng.
3. Kiểm tra trang trên ít nhất ba kích thước màn hình và chỉnh lại chỗ bị vỡ bố cục.
