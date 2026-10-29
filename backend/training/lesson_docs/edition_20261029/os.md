# Hệ điều hành — tình huống và mô hình thực hành

Đọc cùng bài giảng hiện có. Các mô hình dưới đây giải thích cơ chế, không phải công cụ chẩn đoán máy thật. Khi mô tả hiện tượng, tách quan sát, giả thuyết và bằng chứng. Thực hành trên máy/lab được phép, không dừng tiến trình hệ thống tùy tiện.

## Bài 1: Khái niệm về hệ điều hành
**Hỏi thực tế:** “Máy mở nhiều app thì lag, liên quan gì hệ điều hành?” Ứng dụng cần CPU, bộ nhớ và thiết bị I/O. Hệ điều hành quản lý và phân phối các tài nguyên đó; nhiều công việc có thể cạnh tranh tài nguyên hoặc chờ I/O. Chỉ từ chữ “lag” chưa thể kết luận thiếu RAM hay ứng dụng nào lỗi.

**Tự luyện:** ghi nhận lúc lag, số ứng dụng, CPU, RAM và hoạt động đĩa từ công cụ hệ thống. **Hướng giải:** đối chiếu thời điểm thay vì nhìn một ảnh chụp bất kỳ. Không coi CPU thấp là chắc chắn máy không có vấn đề: công việc có thể đang chờ tài nguyên khác.

## Bài 2: Phân loại hệ điều hành
**Tình huống:** nhầm đa nhiệm, nhiều người dùng và thời gian thực là cùng một loại. Các tiêu chí phân loại có thể giao nhau: một hệ thống có thể đa nhiệm và hỗ trợ nhiều người dùng. Hệ thời gian thực quan tâm đáp ứng ràng buộc thời hạn, không chỉ “chạy nhanh”.

**Tự luyện:** so máy cá nhân, máy chủ và bộ điều khiển có thời hạn phản ứng. **Hướng giải:** nêu yêu cầu và hậu quả khi trễ, không chỉ gán nhãn theo tên thương mại. Phân biệt hệ đa xử lý có nhiều bộ xử lý với cảm giác nhiều tác vụ cùng chạy trên một CPU.

## Bài 3: Nhu cầu xử lí đồng thời
**Tình huống:** tải file trong khi nghe nhạc. Đồng thời là quản lý nhiều công việc có thời gian sống chồng nhau; song song là thực thi thực sự cùng lúc ở mức tài nguyên xử lý. Một lõi có thể xen kẽ công việc để tạo tính đáp ứng.

**Tự luyện:** vẽ timeline tác vụ A dùng CPU rồi chờ I/O, tác vụ B cần CPU. **Hướng giải:** cho B sử dụng CPU trong lúc A chờ có thể giảm thời gian nhàn rỗi; không kết luận tổng thời gian luôn giảm một nửa. Đo thời gian chờ và thời gian hoàn thành riêng.

## Bài 4: Khái niệm tiến trình và mô hình đa tiến trình
**Hỏi thực tế:** “Chương trình khác tiến trình thế nào?” Chương trình là mã và dữ liệu ở dạng thụ động; tiến trình là một lần thực thi có trạng thái, ngữ cảnh CPU và tài nguyên. Mở cùng ứng dụng hai lần có thể tạo nhiều tiến trình; chi tiết còn tùy thiết kế ứng dụng.

**Ví dụ:** quán cà phê có nhiều phiếu gọi món; mỗi phiếu là một công việc đang được xử lý, còn công thức là chỉ dẫn. Ví dụ chỉ giúp hình dung, không đồng nhất nhân viên với mọi thành phần của hệ điều hành.

**Tự luyện:** vẽ ready → running → blocked khi đọc file. **Hướng giải:** ready đang đợi CPU, blocked đang đợi sự kiện/tài nguyên; chưa được chạy không có nghĩa đã kết thúc.

## Bài 5: Khái niệm tiến trình và mô hình tiểu tiến trình
**Tình huống:** thêm thread nhưng không nhanh hơn. Các thread trong một tiến trình chia sẻ một số tài nguyên và không gian địa chỉ, nhưng mỗi thread có luồng điều khiển, ngữ cảnh và stack riêng. Công việc phải có phần có thể thực hiện đồng thời và không bị nút thắt khác lấn át.

**Tự luyện:** phân biệt dữ liệu dùng chung và biến cục bộ trong mô hình hai thread. **Hướng giải:** dữ liệu chia sẻ cần cơ chế truy cập đúng; “cùng tiến trình” không làm phép cập nhật nhiều bước tự trở nên nguyên tử. Tránh suy từ số thread sang tốc độ nếu chưa đo.

## Bài 6: Tổ chức quản lí tiến trình
**Tình huống:** một tác vụ ngắn phải đợi sau tác vụ dài. Mô phỏng FCFS với thời lượng 6, 2, 1 cùng đến lúc 0: thứ tự đó cho thời gian chờ 0, 6, 8; trung bình 14/3. Thay chính sách có thể cải thiện một chỉ số nhưng ảnh hưởng công bằng hoặc chi phí chuyển ngữ cảnh.

**Tự luyện:** đổi thứ tự rồi mô phỏng Round Robin quantum 2. **Hướng giải:** ghi thời điểm đến, CPU burst, giả định chi phí và timeline trước khi tính. Không so hai kết quả dựa trên hai bộ giả định khác nhau hoặc bỏ qua starvation khi bàn về ưu tiên.

## Bài 7: Lập trình tiến trình
**Tình huống:** chương trình cha kết thúc khi công việc con chưa xong hoặc không thu kết quả. Phải xác định cách tạo, chờ, trao đổi trạng thái thoát và giải phóng tài nguyên của tiến trình. API cụ thể phụ thuộc hệ điều hành và ngôn ngữ.

**Tự luyện:** mô tả cha tạo hai tác vụ lab, chờ cả hai và ghi lỗi nếu một tác vụ thất bại. **Hướng giải:** tách tạo tiến trình khỏi việc chờ; không coi in “đã tạo” là công việc đã hoàn thành. Không dùng ví dụ fork trên Windows mà không giải thích nền tảng hoặc lớp trừu tượng thay thế.

## Bài 8: Liên lạc tiến trình
**Tình huống:** hai chương trình cần trao đổi kết quả. Chọn cơ chế dựa vào lượng dữ liệu, yêu cầu độ trễ, phạm vi máy và đồng bộ: pipe, hàng đợi thông điệp, socket hoặc vùng nhớ chia sẻ có thể phù hợp các bài khác nhau.

**Tự luyện:** thiết kế thông điệp gồm loại, id yêu cầu và dữ liệu cho hai tiến trình lab. **Hướng giải:** quy định thông điệp lỗi, bên đóng kết nối và tình huống bên kia dừng. Vùng nhớ chia sẻ giảm việc sao chép trong một số thiết kế nhưng không tự giải quyết đồng bộ hoặc tính hợp lệ dữ liệu.

## Bài 9: Các cơ chế thông tin liên lạc
**Tình huống:** gửi một tín hiệu không đồng nghĩa đã chuyển toàn bộ một bản ghi dữ liệu. Cơ chế thông báo sự kiện khác với giao thức truyền dữ liệu có cấu trúc; cần hiểu giới hạn và thứ tự xử lý của API cụ thể.

**Tự luyện:** mô tả gửi thông báo “có dữ liệu mới” và cách nhận dữ liệu thật từ hàng đợi. **Hướng giải:** bên nhận phải xử lý trường hợp trễ, đóng và lỗi; không làm thao tác phức tạp trong signal handler mà không kiểm tra quy tắc nền tảng. Xác định quyền và định danh tiến trình để tránh gửi nhầm.

## Bài 10: Nhu cầu đồng bộ hóa
**Tình huống:** hai thread cùng tăng số lượt đăng ký. Phép đọc–cộng–ghi gồm nhiều bước; nếu cùng đọc 10 rồi đều ghi 11 thì mất một cập nhật. Đây là mô hình minh họa race condition, không phải bảo đảm mọi runtime đều xen kẽ đúng như vậy.

**Tự luyện:** viết các bước xen kẽ gây kết quả sai và đánh dấu vùng tới hạn. **Hướng giải:** tìm dữ liệu dùng chung và bất biến cần giữ, rồi chọn đồng bộ phù hợp. Deadlock khác race: ví dụ T1 giữ A chờ B, T2 giữ B chờ A nên cả hai không tiến được.

## Bài 11: Các giải pháp đồng bộ hóa
**Tình huống:** dùng lock nhưng vẫn treo vì thứ tự lấy nhiều khóa không nhất quán. Quy định cùng một thứ tự lấy khóa và giải phóng ở mọi đường thoát. Semaphore đếm tài nguyên; mutex bảo vệ vùng truy cập theo hợp đồng API, không dùng hai khái niệm như đồng nghĩa tuyệt đối.

**Tự luyện:** mô hình hàng đợi hữu hạn producer/consumer: giới hạn sức chứa, số phần tử và chỗ trống. **Hướng giải:** kiểm tra bất biến 0 ≤ size ≤ capacity, không giữ khóa lâu trong I/O nếu không cần. Với condition variable, kiểm tra lại điều kiện sau khi thức dậy. Muốn tìm ứng dụng nên đóng trên máy lag phải có dữ liệu thực; không đoán tên chương trình từ tài liệu. Bộ nhớ ảo mở rộng mô hình không gian địa chỉ nhưng paging ra đĩa không làm RAM vật lý nhanh hơn.

# Tài liệu tham khảo
https://pages.cs.wisc.edu/~remzi/OSTEP/
