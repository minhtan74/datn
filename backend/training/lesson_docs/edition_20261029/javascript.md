# JavaScript — thực hành trình duyệt và xử lý lỗi

Ví dụ JavaScript cơ bản chạy trong Node hoặc Console trình duyệt; ví dụ DOM cần một trang HTML. Với lỗi, ghi cả input, output mong đợi, output thực tế và vị trí script. Không dán token thật vào báo cáo lỗi.

## JavaScript là gì?
**Tình huống:** “Em mở file JS mà không có gì hiện ra.” Mã JavaScript cần môi trường thực thi. Node không có document của trình duyệt; trình duyệt chạy script trong trang và hiển thị console ở công cụ phát triển.
```javascript
console.log("Hello StudyOnline");
console.assert(2 + 3 === 5);
```
Trong HTML, dùng `<script src="app.js" defer></script>` để tải file ngoài và chạy sau khi phân tích HTML. Mở Network để xem app.js có tải thành công không; đường dẫn tương đối phụ thuộc vị trí trang. Phân biệt lỗi tải file với lỗi cú pháp và lỗi logic.

**Tự luyện:** in một dòng khi trang mở và một dòng khi nhấn nút. **Hướng giải:** dòng đầu chứng minh script chạy; dòng sau chứng minh sự kiện đã gắn đúng. Nếu có lỗi trước đoạn gắn sự kiện, cần sửa lỗi đó trước.

## Biến, kiểu dữ liệu & toán tử
**Hỏi thực tế:** “const rồi sao vẫn push được?” const giữ binding không được gán lại, không đóng băng đối tượng. let cho phép gán lại; ưu tiên const khi không cần gán lại biến.
```javascript
const items = [];
items.push("A");
console.assert(items.length === 1);
console.assert("2" + 3 === "23");
console.assert(Number("2") + 3 === 5);
console.assert(("2" == 2) === true);
console.assert(("2" === 2) === false);
```
Toán tử + có chuỗi sẽ nối chuỗi trong trường hợp trên. `==` có ép kiểu; `===` kiểm tra nghiêm ngặt, nên dùng khi không chủ đích ép kiểu. `Number("")` cho 0 nên kiểm tra rỗng trước khi đổi số.

**Tự luyện:** kiểm tra chuỗi khoảng trắng và `"abc"`. **Hướng giải:** loại input rỗng; sau chuyển đổi dùng `Number.isFinite`. Không dùng kiểm tra truthy để loại số 0 nếu 0 là dữ liệu hợp lệ.

## Hàm trong JavaScript
**Tình huống:** chương trình in đúng nhưng biến nhận kết quả lại undefined. Hàm phải return giá trị muốn truyền cho nơi gọi; console.log chỉ ghi ra console.
```javascript
function total(values) {
  return values.reduce((sum, value) => sum + value, 0);
}
console.assert(total([2, 3]) === 5);
console.assert(total([]) === 0);
const add = (a, b) => a + b;
console.assert(add(1, 2) === 3);
```
Hợp đồng hàm cần nêu mảng có chứa chuỗi không, cách xử lý dữ liệu sai và có sửa input hay không. Callback là hàm được truyền vào hàm khác; truyền `handler` khác với gọi ngay `handler()`.

**Tự luyện:** viết hàm tính giá sau giảm, kiểm tra phần trăm trong 0..100. **Hướng giải:** tách kiểm tra dữ liệu khỏi thao tác giao diện, thử 0%, 100% và giá trị ngoài miền.

## Tổng quan về DOM
**Hỏi thực tế:** “getElementById('btn') ra null nên nút không hoạt động.” Kiểm tra phần tử có đúng id không, có được render không và script có chạy trước khi HTML được phân tích không. Không kết luận một nguyên nhân khi chưa có HTML và vị trí script.
```javascript
const button = document.getElementById("btn");
if (!button) {
  console.error("Không tìm thấy #btn; kiểm tra HTML và thời điểm chạy");
} else {
  button.textContent = "Sẵn sàng";
}
```
`textContent` phù hợp để hiển thị văn bản người dùng nhập. Không ghép dữ liệu chưa tin cậy vào innerHTML. Dùng defer cho script ngoài hoặc gắn sau DOMContentLoaded khi cần.

**Tự luyện:** đổi id trong HTML rồi quan sát thông báo. **Hướng giải:** sau khi khớp id và thời điểm, đối tượng không còn null; tránh thêm setTimeout tùy ý để che lỗi thứ tự.

## Xử lý sự kiện click, submit
**Tình huống:** bấm nút trong form làm tải lại trang. Nút mặc định trong form có thể submit; với hành động riêng dùng `type="button"`, với gửi form xử lý sự kiện submit và preventDefault khi ứng dụng tự gửi request.
```javascript
const form = document.querySelector("form");
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const name = new FormData(form).get("name");
  console.log(String(name ?? "").trim());
});
```
**Tự luyện:** nhấn Enter trong input và nhấn nút gửi, mỗi hành động chỉ được xử lý một lần. **Hướng giải:** nghe submit trên form thay vì chỉ click trên nút; tránh gắn lại handler mỗi lần render. Khi gửi bất đồng bộ, khóa nút trong lúc chờ và mở lại ở finally; backend vẫn phải kiểm soát thao tác trùng.

## Dự án: To-do List
**Yêu cầu:** thêm việc không rỗng, đánh dấu hoàn thành, xóa theo id và hiển thị số việc còn lại. Id dùng để nhận diện ổn định, không dùng vị trí mảng khi có xóa/sắp xếp.
```javascript
const tasks = [
  {id: "a", title: "Đọc bài", done: false},
  {id: "b", title: "Thực hành", done: true}
];
const next = tasks.map(t => t.id === "a" ? {...t, done: true} : t);
console.assert(tasks[0].done === false);
console.assert(next.filter(t => !t.done).length === 0);
```
**Tự luyện:** lưu localStorage, tải lại và xử lý JSON hỏng. **Hướng giải:** dùng try/catch khi đọc, xác thực cấu trúc mảng; lưu trạng thái thay vì HTML sinh ra. Thử tiêu đề chứa dấu < và > để chắc chúng hiển thị như chữ, không trở thành thẻ.

## Arrow function & Destructuring
**Tình huống:** arrow function có dấu ngoặc nhọn nhưng không return nên cho undefined. Arrow viết một biểu thức có thể trả ngầm; trả object cần bọc bằng ngoặc tròn.
```javascript
const toLabel = ({id, title = "Chưa có tên"}) => ({id, label: title});
const item = toLabel({id: 1});
console.assert(item.label === "Chưa có tên");
const [first, ...rest] = [1, 2, 3];
console.assert(first === 1 && rest.length === 2);
```
Arrow không tạo this riêng. Đừng đổi mọi method sang arrow chỉ vì cú pháp ngắn; this cần hiểu theo nơi định nghĩa hoặc cách gọi. Spread object/mảng là bản sao nông, không sao chép sâu mọi đối tượng lồng.

**Tự luyện:** đổi tên thuộc tính khi destructuring và đặt giá trị mặc định. **Hướng giải:** giá trị mặc định được dùng cho undefined, không tự thay thế null.

## Promise & Async/Await
**Hỏi thực tế:** “promsie là gì, then catch để làm gì?” Promise biểu diễn kết quả bất đồng bộ: pending, fulfilled hoặc rejected. then xử lý kết quả, catch xử lý lỗi; async trả Promise, await chờ bên trong hàm async.
```javascript
async function readValue() {
  const value = await Promise.resolve(5);
  return value * 2;
}
readValue().then(value => console.assert(value === 10));
```
Không đọc biến kết quả ngay sau khi khởi động request rồi cho rằng dữ liệu đã về. Với nhiều việc độc lập, Promise.all cho phép chờ chung nhưng sẽ reject khi một Promise reject; chọn cách xử lý theo nghiệp vụ, không nuốt lỗi bằng mảng rỗng tùy tiện.

**Tự luyện:** giả lập thao tác thất bại và bảo đảm nút được mở lại. **Hướng giải:** dùng try/catch/finally, phân biệt đang tải, thành công, rỗng và lỗi trong giao diện.

## Module & Fetch API
**Tình huống:** fetch trả 404 nhưng catch không chạy. fetch không tự coi HTTP 4xx/5xx là Promise rejection; phải kiểm tra response.ok. JSON lỗi cũng cần được xử lý.
```javascript
export async function getCourses(url, signal) {
  const response = await fetch(url, {signal});
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const body = await response.json();
  if (!Array.isArray(body.data)) throw new Error("Sai cấu trúc dữ liệu");
  return body.data;
}
```
**Tự luyện:** thử 200 có dữ liệu, 200 rỗng, 404, JSON hỏng và hủy request. **Hướng giải:** mỗi trạng thái có cách hiển thị rõ; AbortController không đồng nghĩa backend hoàn tác hành động đã nhận. Module trình duyệt cần `type="module"`; lỗi CORS phải sửa cấu hình đúng phía server, không tắt bảo vệ trình duyệt.

# Tài liệu tham khảo
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide
