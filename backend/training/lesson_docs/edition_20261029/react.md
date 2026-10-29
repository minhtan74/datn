# React — thực hành trạng thái, API và điều hướng

Các ví dụ tập trung React 18 như dự án hiện tại, dùng function component và Hooks. Không giả định API của phiên bản router khác với phiên bản được cài. Mỗi ví dụ UI cần thử thao tác, không chỉ xác nhận build thành công.

## Giới thiệu React & JSX
**Tình huống:** viết HTML vào JSX gây lỗi. JSX gần HTML nhưng có quy tắc JavaScript: dùng className, đóng thẻ và bọc các phần tử cùng cấp. Biểu thức đặt trong dấu ngoặc nhọn; không đặt câu lệnh if trực tiếp vào vị trí biểu thức.
```jsx
function Greeting({name}) {
  return <section className="greeting"><h2>Chào {name}</h2></section>;
}
```
**Tự luyện:** render tên trống và tên dài. **Hướng giải:** chọn thông điệp thay thế có ý nghĩa; React hiển thị chuỗi như dữ liệu, không dùng dangerouslySetInnerHTML cho dữ liệu chưa tin cậy. Component cần tên viết hoa để được hiểu là component.

## Component & Props
**Tình huống:** sửa props rồi giao diện không đúng hoặc làm dữ liệu cha thay đổi. Props là đầu vào; cập nhật dữ liệu ở nơi sở hữu state và truyền callback xuống.
```jsx
function CourseCard({course, onOpen}) {
  return <button onClick={() => onOpen(course.id)}>{course.title}</button>;
}
```
**Tự luyện:** render danh sách card, tìm lại một card sau khi sắp xếp. **Hướng giải:** key ổn định theo id, không theo vị trí nếu dữ liệu có đổi thứ tự. Tránh đặt nút bên trong nút; tách vùng điều hướng và hành động phụ để dùng được bằng bàn phím.

## State & useState
**Tình huống:** gọi setCount nhiều lần nhưng tăng không như dự đoán. Khi state mới phụ thuộc state trước, dùng updater. Không sửa trực tiếp mảng/object rồi truyền lại cùng tham chiếu.
```jsx
setCount(previous => previous + 1);
setCourses(previous => previous.map(c => c.id === id ? {...c, title} : c));
```
**Tự luyện:** đếm hai lần tăng trong một handler và sửa tên một khóa. **Hướng giải:** coi state như snapshot của lần render; console.log ngay sau setState có thể vẫn thấy snapshot cũ. Trạng thái suy ra từ dữ liệu, như số mục đã hoàn thành, thường có thể tính khi render thay vì lưu thêm state dễ lệch nhau.

## useEffect & vòng đời component
**Tình huống:** đổi khóa nhanh làm response cũ ghi đè response mới. Effect đồng bộ với hệ thống bên ngoài, cần cleanup và dependency đúng; không dùng effect để thay thế mọi phép tính.
```jsx
useEffect(() => {
  const controller = new AbortController();
  loadCourses(controller.signal);
  return () => controller.abort();
}, [courseId]);
```
**Tự luyện:** làm chậm mạng và chuyển giữa hai khóa. **Hướng giải:** bỏ qua response đã hết hiệu lực; xử lý AbortError phù hợp. StrictMode trong phát triển có thể chạy thêm chu kỳ setup/cleanup để phát hiện lỗi; không tắt nó chỉ để che request/side effect bị viết sai. Không để dependency rỗng khi effect thực sự phụ thuộc courseId.

## useContext & useReducer
**Tình huống:** nhiều trang cần user hiện tại hoặc giỏ thao tác. Context truyền giá trị, reducer mô tả cách chuyển trạng thái; không thay thế mọi state cục bộ bằng context toàn ứng dụng.
```javascript
function reducer(state, action) {
  switch (action.type) {
    case "reset": return {items: []};
    case "add": return {...state, items: [...state.items, action.item]};
    default: return state;
  }
}
```
**Tự luyện:** thêm rồi reset, kiểm tra state đầu không bị sửa. **Hướng giải:** reducer không gửi HTTP hoặc tạo side effect; auth context không phải lớp bảo mật thay cho API. Backend vẫn kiểm tra token và quyền ở mọi request.

## Custom Hooks
**Tình huống:** ba trang lặp logic loading/error và hủy request. Custom Hook tái sử dụng logic stateful, không tự làm các component dùng chung cùng một state nếu không thiết kế như vậy.

**Tự luyện:** thiết kế `useCourse(id)` trả data, loading, error và reload; viết trước hợp đồng khi id rỗng và khi request thất bại. **Hướng giải:** gọi Hooks ở cấp cao nhất của component/Hook, không gọi có điều kiện hoặc trong vòng lặp. Hook nên trả lỗi để UI quyết định thông báo; không nuốt lỗi thành dữ liệu rỗng vì người dùng sẽ hiểu nhầm “không có khóa”.

## Kết nối API với Axios
**Tình huống:** server trả 401, 403 và 500 nhưng UI đều hiện danh sách rỗng. Phân biệt lỗi xác thực, quyền, dữ liệu đầu vào và lỗi hệ thống; không hiển thị token hoặc stack trace cho người học.

**Tự luyện:** mô phỏng 200 có dữ liệu, 200 rỗng, 401, 403, 422 và mất kết nối. **Hướng giải:** mỗi trạng thái có thông báo/hành động phù hợp. Khi gửi mutation, chống click lặp bằng trạng thái chờ và kiểm soát trùng phía backend. Nếu dự án bọc Axios thành `{ok, data}`, hãy kiểm tra hợp đồng wrapper thay vì dùng lẫn cú pháp response Axios nguyên bản.

## Routing với React Router
**Tình huống:** copy URL trang kết quả sang tab mới nhưng thiếu dữ liệu. Navigation state chỉ là tiện ích trong phiên điều hướng; nội dung cần mở lại phải có id trong URL và tải lại được từ API có xác thực.
```jsx
<Link to={`/courses/${course.id}`}>{course.title}</Link>
```
**Tự luyện:** điều hướng, F5, nút Back và URL không tồn tại. **Hướng giải:** dùng API của phiên bản React Router đang cài; guard phía client hỗ trợ UX, backend mới quyết định quyền. Trang 404 và thiếu tham số cần thông báo rõ, không âm thầm hiển thị dữ liệu khóa mặc định khác.

## Dự án: Trang quản lý khoá học
**Bài thực hành:** danh sách có tìm kiếm, lọc trạng thái, chi tiết và form tạo/sửa trên API lab. Phân biệt trạng thái “chưa làm”, “đang làm”, “đã nộp” nếu có quiz; điểm đạt là thông tin phụ, không đồng nghĩa đã nộp và đạt là cùng một trạng thái.

**Tự luyện:** tìm không có kết quả, gửi lỗi, thao tác nhanh, mở trên điện thoại và đăng xuất rồi Back. **Hướng giải:** sau mutation chỉ cập nhật UI khi server xác nhận hoặc có cơ chế rollback rõ; kiểm tra quyền trước và sau khi tải lại. Báo cáo cần ghi những thao tác đã thử, không suy ra toàn bộ backend an toàn chỉ từ việc menu bị ẩn.

# Tài liệu tham khảo
https://react.dev/learn
