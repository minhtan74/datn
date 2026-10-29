"""Add three introductory IT courses without modifying existing learning records.

Run from backend: .venv/Scripts/python training/seed_it_courses.py
Defaults to a read-only preview; pass --apply to commit one transaction.
Each course contains two chapters, four reading lessons and a 20-question quiz.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.core.database import engine
from app.services.analytics_service import normalize_topic
from training.normalize_it_chapters import chapter_title


# Question format: prompt, correct answer, three distractors, explanation.
COURSES = [
    dict(title='Mạng máy tính cơ bản', slug='mang-may-tinh-co-ban',
         description='Nhập môn mạng máy tính: mô hình TCP/IP, IPv4, DNS và HTTP. Học qua 4 bài đọc, bài tập tự luyện và bài kiểm tra 20 câu; không yêu cầu kiến thức mạng trước đó.', chapters=[
        ('Nền tảng kết nối mạng', [
            ('Mô hình TCP/IP và thiết bị mạng', '''Mục tiêu: phân biệt chức năng các tầng và thiết bị mạng cơ bản.

Mạng máy tính cho phép các thiết bị trao đổi dữ liệu theo giao thức chung. Mô hình TCP/IP thường được trình bày với bốn tầng: ứng dụng, giao vận, Internet và truy nhập mạng. HTTP và DNS thuộc tầng ứng dụng; TCP và UDP thuộc tầng giao vận; IP thực hiện địa chỉ hóa và chuyển gói ở tầng Internet.

Switch chuyển tiếp khung trong mạng LAN dựa trên địa chỉ MAC. Router chuyển tiếp gói giữa các mạng IP dựa trên bảng định tuyến. Điểm truy cập không dây kết nối thiết bị Wi-Fi vào mạng; không nên đồng nhất mọi điểm truy cập với router dù thiết bị gia đình thường tích hợp nhiều chức năng.

TCP cung cấp luồng byte có thứ tự và cơ chế truyền lại. UDP gửi datagram, không tự bảo đảm giao hàng hoặc thứ tự. Ứng dụng chọn giao thức theo nhu cầu; không thể kết luận UDP luôn tốt hơn TCP.

Tự luyện: vẽ đường đi từ máy tính qua switch và router tới máy chủ; ghi giao thức ứng dụng và giao vận tại mỗi đầu.''', [
                ('HTTP thuộc tầng nào của mô hình TCP/IP?', 'Ứng dụng', 'Giao vận', 'Internet', 'Truy nhập mạng', 'HTTP quy định trao đổi thông điệp giữa ứng dụng khách và máy chủ.'),
                ('Thiết bị nào thường chuyển tiếp gói giữa hai mạng IP?', 'Router', 'Bàn phím', 'Switch lớp 2 thuần túy', 'Màn hình', 'Router dùng địa chỉ IP và bảng định tuyến để chuyển gói giữa các mạng.'),
                ('Switch lớp 2 thường chuyển tiếp khung dựa trên thông tin nào?', 'Địa chỉ MAC', 'Tên tệp', 'Mã HTTP', 'Tên miền', 'Switch học địa chỉ MAC và cổng tương ứng trong LAN.'),
                ('Đặc điểm nào do TCP cung cấp?', 'Luồng byte có thứ tự và truyền lại khi cần', 'Không dùng cổng', 'Không cần địa chỉ IP', 'Luôn mã hóa nội dung', 'TCP hỗ trợ thứ tự và độ tin cậy; bản thân TCP không mã hóa dữ liệu.'),
                ('Phát biểu nào đúng về UDP?', 'Không tự bảo đảm giao hàng và thứ tự datagram', 'Luôn truyền lại mọi gói mất', 'Thay thế DNS trong mọi hệ thống', 'Chỉ dùng cho kết nối có dây', 'Ứng dụng sử dụng UDP phải tự xử lý các bảo đảm bổ sung nếu cần.'),
            ]),
            ('Địa chỉ IPv4 và mạng con', '''Mục tiêu: đọc địa chỉ IPv4, ký hiệu CIDR và xác định mạng con đơn giản.

IPv4 dùng địa chỉ 32 bit, thường viết thành bốn số thập phân từ 0 đến 255. Ký hiệu /24 cho biết 24 bit đầu là phần mạng; mặt nạ tương ứng là 255.255.255.0. Với mạng thông thường 192.168.1.0/24, địa chỉ mạng là 192.168.1.0, broadcast là 192.168.1.255 và các địa chỉ host thông thường là .1 đến .254.

Hai host 192.168.1.10/24 và 192.168.1.20/24 cùng mạng con. Host 192.168.2.10/24 nằm ở mạng khác. Khi đích ngoài mạng con, máy thường gửi gói đến default gateway để chuyển tiếp; gateway không phải máy chủ DNS.

Các dải riêng gồm 10.0.0.0/8, 172.16.0.0/12 và 192.168.0.0/16. Chúng không được định tuyến công khai trên Internet. Không suy ra mọi địa chỉ bắt đầu bằng 172 đều là địa chỉ riêng.

Tự luyện: với 10.0.5.0/24, tìm địa chỉ mạng, broadcast và hai địa chỉ host hợp lệ. Quy tắc trừ hai địa chỉ chỉ áp dụng mạng con thông thường; /31 và /32 có cách sử dụng riêng.''', [
                ('Địa chỉ IPv4 có bao nhiêu bit?', '32', '16', '64', '128', 'IPv4 có 32 bit; IPv6 có 128 bit.'),
                ('Mặt nạ nào tương ứng với /24?', '255.255.255.0', '255.0.0.0', '255.255.0.0', '0.0.0.0', '/24 đặt 24 bit đầu của mặt nạ thành 1.'),
                ('Host nào cùng mạng con với 192.168.1.10/24?', '192.168.1.20/24', '192.168.2.20/24', '10.0.0.20/24', '172.16.0.20/24', 'Với /24, hai host có cùng ba octet đầu thuộc cùng mạng con.'),
                ('Broadcast của mạng thông thường 192.168.1.0/24 là gì?', '192.168.1.255', '192.168.1.0', '192.168.0.255', '192.168.1.1', 'Địa chỉ broadcast đặt toàn bộ 8 bit host thành 1.'),
                ('Default gateway thường được dùng khi nào?', 'Gửi gói tới đích ngoài mạng con', 'Đổi tên mọi tệp', 'Tạo mật khẩu Wi-Fi', 'Biên dịch chương trình', 'Gateway là bước chuyển tiếp ra khỏi mạng con hiện tại.'),
            ]),
        ]),
        ('Dịch vụ và ứng dụng mạng', [
            ('DNS và phân giải tên miền', '''Mục tiêu: giải thích vai trò DNS và đọc các loại bản ghi cơ bản.

DNS là hệ thống phân giải tên phân tán. Ứng dụng có thể hỏi resolver để tìm địa chỉ gắn với tên miền. Resolver tận dụng bộ nhớ đệm hoặc truy vấn các máy chủ thích hợp; không phải mọi yêu cầu đều đi lại toàn bộ chuỗi truy vấn.

Bản ghi A ánh xạ tên tới IPv4, AAAA tới IPv6. CNAME khai báo tên bí danh trỏ tới một tên khác. MX mô tả máy chủ nhận thư cho miền. TTL hướng dẫn thời gian lưu bộ nhớ đệm, không phải thời gian tải trang hay thời hạn đăng ký tên miền.

DNS thường sử dụng cổng 53 với UDP hoặc TCP. Phân giải tên thành công chỉ cho biết có câu trả lời DNS; không chứng minh máy chủ web đang hoạt động. Khi gỡ lỗi, tách kiểm tra DNS khỏi kiểm tra kết nối và HTTP.

Tự luyện: mô tả vì sao đổi bản ghi chưa chắc mọi người dùng thấy ngay. Nêu khác biệt giữa tên miền, địa chỉ IP và URL; URL còn có thể chứa giao thức, đường dẫn và tham số.''', [
                ('Vai trò chính của DNS là gì?', 'Phân giải tên miền thành thông tin như địa chỉ IP', 'Nén ảnh', 'Tăng dung lượng RAM', 'Mã hóa mọi kết nối', 'DNS cung cấp bản ghi gắn với tên miền.'),
                ('Bản ghi nào ánh xạ tên miền tới IPv4?', 'A', 'AAAA', 'MX', 'CNAME', 'Bản ghi A chứa địa chỉ IPv4.'),
                ('Bản ghi nào chứa địa chỉ IPv6?', 'AAAA', 'A', 'MX', 'TXT luôn luôn', 'AAAA là loại bản ghi dành cho địa chỉ IPv6.'),
                ('TTL trong DNS liên quan tới điều gì?', 'Thời gian lưu bản ghi trong bộ nhớ đệm', 'Dung lượng ổ cứng', 'Số trang của website', 'Số lần đăng nhập tối đa', 'TTL giúp resolver xác định thời gian có thể tái sử dụng bản ghi.'),
                ('DNS phân giải thành công có bảo đảm website hoạt động không?', 'Không, dịch vụ web vẫn có thể gặp lỗi', 'Có, mọi dịch vụ đều hoạt động', 'Có, mật khẩu chắc chắn đúng', 'Có, mạng không thể mất gói', 'DNS và dịch vụ HTTP là các bước khác nhau.'),
            ]),
            ('HTTP và HTTPS', '''Mục tiêu: nhận biết request, response, phương thức và nhóm mã trạng thái.

HTTP tổ chức trao đổi yêu cầu và phản hồi. Request có phương thức, đường dẫn, header và có thể có body; response có mã trạng thái, header và có thể có body. GET thường dùng để lấy biểu diễn tài nguyên; POST thường gửi dữ liệu để máy chủ xử lý. Không đặt dữ liệu bí mật vào URL chỉ vì đang dùng HTTPS, vì URL có thể xuất hiện trong lịch sử và nhật ký.

Nhóm 2xx báo thành công, 3xx chuyển hướng, 4xx lỗi phía yêu cầu và 5xx lỗi máy chủ. 404 nghĩa là không tìm thấy tài nguyên theo yêu cầu; 500 là lỗi nội bộ máy chủ. Cần đọc cả phản hồi và ngữ cảnh để chẩn đoán.

HTTPS là HTTP được bảo vệ bằng TLS: hỗ trợ bảo mật đường truyền, toàn vẹn và xác thực máy chủ theo chứng thư hợp lệ. HTTPS không bảo đảm nội dung website đáng tin hoặc ứng dụng không có lỗ hổng.

Tự luyện: mô tả một request GET lấy trang khóa học; nêu cách xử lý khác nhau khi nhận 404 và 500.''', [
                ('Phương thức HTTP nào thường dùng để lấy tài nguyên?', 'GET', 'POST luôn luôn', 'DELETE', 'PATCH luôn luôn', 'GET được thiết kế để lấy biểu diễn của tài nguyên.'),
                ('Mã 404 thường có ý nghĩa gì?', 'Không tìm thấy tài nguyên được yêu cầu', 'Thành công', 'Lỗi nội bộ máy chủ', 'Chuyển hướng vĩnh viễn', '404 thuộc nhóm lỗi yêu cầu 4xx.'),
                ('Mã 500 thuộc nhóm nào?', 'Lỗi máy chủ', 'Thành công', 'Chuyển hướng', 'Thông tin 1xx', '500 là Internal Server Error thuộc nhóm 5xx.'),
                ('HTTPS bổ sung cơ chế nào cho HTTP?', 'Bảo vệ đường truyền bằng TLS', 'Tự sửa mọi lỗi ứng dụng', 'Loại bỏ nhu cầu xác thực người dùng', 'Bảo đảm mọi nội dung đều đúng', 'TLS cung cấp các bảo đảm đường truyền, không thay thế bảo mật ứng dụng.'),
                ('Một HTTP response thường chứa thành phần nào?', 'Mã trạng thái và header', 'Chỉ địa chỉ MAC', 'Chỉ mật khẩu', 'Chỉ tên tệp', 'Response có mã trạng thái, header và có thể có body.'),
            ]),
        ]),
    ]),
    dict(title='Cấu trúc dữ liệu và giải thuật cơ bản', slug='cau-truc-du-lieu-giai-thuat-co-ban',
         description='Nền tảng lựa chọn cấu trúc dữ liệu và phân tích thuật toán: mảng, danh sách liên kết, stack, queue, tìm kiếm và sắp xếp. Gồm 4 bài đọc và quiz 20 câu.', chapters=[
        ('Cấu trúc dữ liệu tuyến tính', [
            ('Mảng và danh sách liên kết', '''Mục tiêu: chọn cấu trúc phù hợp với thao tác truy cập, tìm kiếm và cập nhật.

Mảng lưu các phần tử ở vùng nhớ liên tiếp trong mô hình cơ bản. Truy cập theo chỉ số có thời gian O(1), nhưng tìm một giá trị trong mảng chưa sắp xếp thường cần O(n). Chèn vào giữa mảng có thể phải dịch chuyển nhiều phần tử nên thường là O(n).

Danh sách liên kết gồm các nút, mỗi nút chứa dữ liệu và liên kết. Danh sách đơn có liên kết tới nút sau; muốn tới phần tử thứ k phải đi từ đầu nên thường O(k). Nếu đã biết nút đứng trước vị trí cần chèn, việc nối một nút mới có thể O(1), chưa tính thời gian tìm vị trí.

Không có cấu trúc luôn tốt nhất: mảng phù hợp truy cập ngẫu nhiên và thường có tính cục bộ bộ nhớ tốt; danh sách liên kết phù hợp một số thao tác nối/tách khi đã có vị trí. Big-O mô tả tốc độ tăng chi phí, không phải số giây chính xác.

Tự luyện: mô phỏng chèn X vào giữa [A,B,C,D], rồi mô phỏng thao tác đó với danh sách liên kết. Đếm thao tác phải thay đổi.''', [
                ('Truy cập phần tử theo chỉ số trong mảng cơ bản có độ phức tạp nào?', 'O(1)', 'O(n)', 'O(n²)', 'O(log n) luôn luôn', 'Địa chỉ phần tử được tính trực tiếp từ chỉ số.'),
                ('Tìm một giá trị trong mảng chưa sắp xếp có trường hợp xấu nhất là gì?', 'O(n)', 'O(1)', 'O(log n)', 'O(0)', 'Có thể cần kiểm tra tất cả n phần tử.'),
                ('Danh sách liên kết đơn cơ bản có đặc điểm nào?', 'Mỗi nút có dữ liệu và liên kết tới nút tiếp theo', 'Mọi nút bắt buộc nằm liên tiếp', 'Truy cập mọi chỉ số đều O(1)', 'Không thể chèn nút', 'Các nút nối với nhau bằng liên kết, không yêu cầu liên tiếp trong bộ nhớ.'),
                ('Chèn vào giữa mảng thường cần thao tác gì?', 'Dịch chuyển các phần tử phía sau', 'Sắp xếp lại toàn bộ theo tên', 'Xóa mọi phần tử', 'Đổi địa chỉ IP', 'Dịch phần tử tạo chỗ trống nên thường tốn O(n).'),
                ('Khi đã biết nút đứng trước, nối một nút mới vào danh sách đơn thường là gì?', 'O(1), chưa tính tìm vị trí', 'O(n²) bắt buộc', 'Không thể thực hiện', 'O(log n) bắt buộc', 'Chỉ cần thay đổi một số hữu hạn liên kết.'),
            ]),
            ('Ngăn xếp và hàng đợi', '''Mục tiêu: mô phỏng LIFO, FIFO và chọn stack hoặc queue đúng tình huống.

Stack là ngăn xếp theo nguyên tắc LIFO: phần tử vào sau được lấy trước. push thêm vào đỉnh, pop lấy khỏi đỉnh, peek xem đỉnh mà không xóa. Với triển khai phù hợp, các thao tác cơ bản có thể O(1). Gọi pop trên stack rỗng cần được xử lý theo quy ước của chương trình.

Queue là hàng đợi theo nguyên tắc FIFO: phần tử vào trước được lấy trước. enqueue thêm vào cuối, dequeue lấy ở đầu. Có thể dùng danh sách liên kết hoặc bộ đệm vòng để tránh dịch toàn bộ phần tử mỗi lần lấy đầu.

Stack hữu ích cho kiểm tra dấu ngoặc và quay lui; queue hữu ích cho xử lý công việc theo thứ tự đến và duyệt BFS. Cấu trúc mô tả quy tắc lấy dữ liệu, không đồng nghĩa với một kiểu lưu bộ nhớ duy nhất.

Tự luyện: thực hiện push(A), push(B), pop(), push(C), pop() trên stack. Làm chuỗi tương tự với enqueue và dequeue rồi so sánh kết quả.''', [
                ('Stack tuân theo nguyên tắc nào?', 'LIFO', 'FIFO', 'Ngẫu nhiên bắt buộc', 'Sắp xếp tăng dần', 'LIFO nghĩa là vào sau, ra trước.'),
                ('Queue tuân theo nguyên tắc nào?', 'FIFO', 'LIFO', 'Lấy số lớn nhất trước', 'Lấy số nhỏ nhất trước', 'FIFO nghĩa là vào trước, ra trước.'),
                ('push(A), push(B), pop() trên stack trả về gì?', 'B', 'A', 'Cả A và B', 'Không phần tử nào', 'B được đưa vào sau nên nằm trên đỉnh.'),
                ('Thao tác peek trên stack thường làm gì?', 'Xem đỉnh mà không xóa', 'Xóa toàn bộ', 'Thêm hai phần tử', 'Đảo ngược bắt buộc', 'peek đọc phần tử trên đỉnh nhưng giữ nguyên stack.'),
                ('Thuật toán BFS thường dùng cấu trúc nào?', 'Queue', 'Stack thay cho queue trong mọi trường hợp', 'Chỉ một biến số nguyên', 'Không cần lưu đỉnh chờ', 'Queue giúp xử lý các đỉnh theo thứ tự khám phá từng lớp.'),
            ]),
        ]),
        ('Tìm kiếm và sắp xếp', [
            ('Tìm kiếm tuyến tính và nhị phân', '''Mục tiêu: xác định điều kiện áp dụng và so sánh chi phí tìm kiếm.

Tìm kiếm tuyến tính kiểm tra lần lượt các phần tử; dùng được với dữ liệu chưa sắp xếp. Trường hợp xấu nhất phải xét n phần tử nên là O(n). Kết quả tìm kiếm nên quy ước rõ vị trí tìm thấy hoặc dấu hiệu không có dữ liệu.

Tìm kiếm nhị phân trên mảng đã sắp xếp so sánh mục tiêu với phần tử giữa rồi bỏ một nửa khoảng tìm kiếm. Số bước so sánh trong trường hợp xấu nhất là O(log n). Điều kiện sắp xếp phải phù hợp phép so sánh; không được áp dụng trực tiếp lên một mảng tùy ý chưa sắp xếp.

Trong biến thể dùng hai biên đóng, nếu mục tiêu nhỏ hơn phần tử giữa thì cập nhật biên phải thành mid-1; nếu lớn hơn thì biên trái thành mid+1. Cần bảo đảm khoảng tìm kiếm giảm sau mỗi bước để tránh vòng lặp vô hạn.

Tự luyện: tìm 13 trong [2,5,8,13,21,34,55]. Ghi hai biên và phần tử giữa ở từng bước. Thử tiếp một giá trị không có trong mảng.''', [
                ('Tìm kiếm nhị phân trực tiếp trên mảng cần điều kiện nào?', 'Mảng đã sắp xếp theo phép so sánh sử dụng', 'Mảng phải chỉ có số âm', 'Mảng phải có đúng 10 phần tử', 'Mảng không được sắp xếp', 'Thứ tự cho phép loại bỏ một nửa không gian tìm kiếm.'),
                ('Trường hợp xấu nhất của tìm kiếm tuyến tính là gì?', 'O(n)', 'O(1)', 'O(log n)', 'O(n!) bắt buộc', 'Có thể phải đọc hết mảng trước khi kết luận.'),
                ('Trường hợp xấu nhất của tìm kiếm nhị phân trên mảng là gì?', 'O(log n)', 'O(n²)', 'O(n!)', 'O(1) với mọi n', 'Mỗi bước giảm khoảng tìm kiếm xuống khoảng một nửa.'),
                ('Nếu mục tiêu nhỏ hơn phần tử giữa của mảng tăng dần, nên xét đâu?', 'Nửa bên trái', 'Nửa bên phải', 'Chỉ phần tử cuối', 'Xóa cả mảng', 'Mọi phần tử bên phải giữa đều không nhỏ hơn phần tử giữa.'),
                ('Vì sao phải cập nhật biên sau mỗi bước tìm kiếm nhị phân?', 'Để khoảng tìm kiếm giảm và thuật toán kết thúc', 'Để mảng tự tăng kích thước', 'Để đổi kiểu dữ liệu', 'Để bắt buộc sắp xếp lại', 'Nếu biên không tiến triển, thuật toán có thể lặp vô hạn.'),
            ]),
            ('Sắp xếp và độ phức tạp', '''Mục tiêu: đọc Big-O và mô tả hai thuật toán sắp xếp cơ bản.

Big-O mô tả một chặn trên tiệm cận của chi phí theo kích thước đầu vào. O(n) tăng tuyến tính, O(n²) tăng theo bình phương. Khi so sánh cần cùng loại chi phí và trường hợp phân tích; không suy ra thời gian thực tế chỉ từ Big-O.

Selection sort chọn phần tử nhỏ nhất trong phần chưa sắp xếp rồi đưa về đầu phần đó. Thuật toán thường có O(n²) phép so sánh và có thể thực hiện tại chỗ. Merge sort chia dữ liệu, sắp xếp các nửa rồi trộn hai dãy đã có thứ tự; thời gian thường O(n log n).

Bản merge sort thông thường trên mảng cần O(n) bộ nhớ phụ. Một thuật toán ổn định giữ thứ tự tương đối của các phần tử có khóa bằng nhau. Ổn định và tại chỗ là hai thuộc tính khác nhau, không phải tên gọi của độ phức tạp thời gian.

Tự luyện: mô phỏng hai bước selection sort cho [4,2,5,1]. Trộn [1,4,7] với [2,3,8]. Với bản ghi cùng điểm, giải thích vì sao giữ thứ tự ban đầu có thể hữu ích.''', [
                ('O(n²) thường mô tả mức tăng chi phí như thế nào?', 'Theo bình phương kích thước đầu vào', 'Không đổi với mọi đầu vào', 'Luôn đúng hai giây', 'Luôn giảm khi n tăng', 'Big-O biểu diễn quan hệ tăng trưởng, không phải thời gian tuyệt đối.'),
                ('Selection sort thường chọn gì ở mỗi bước?', 'Phần tử nhỏ nhất trong phần chưa sắp xếp', 'Một phần tử ngẫu nhiên rồi dừng', 'Luôn phần tử ở giữa', 'Luôn phần tử cuối không so sánh', 'Phần tử nhỏ nhất được đưa về đầu phần chưa sắp xếp.'),
                ('Thời gian thông thường của merge sort là gì?', 'O(n log n)', 'O(1)', 'O(n!)', 'O(log n) tổng cộng', 'Có khoảng log n mức chia và O(n) công việc trộn mỗi mức.'),
                ('Sắp xếp ổn định có ý nghĩa gì?', 'Giữ thứ tự tương đối của phần tử có khóa bằng nhau', 'Không bao giờ dùng bộ nhớ', 'Luôn chạy O(1)', 'Không được đổi chỗ phần tử nào', 'Tính ổn định xét các phần tử có khóa so sánh bằng nhau.'),
                ('Merge sort thông thường trên mảng thường cần bộ nhớ phụ bao nhiêu?', 'O(n)', 'O(1) bắt buộc', 'O(n!)', 'Không có bộ nhớ nào', 'Bộ đệm trộn thông thường có kích thước tỉ lệ với số phần tử.'),
            ]),
        ]),
    ]),
    dict(title='Kiểm thử phần mềm nhập môn', slug='kiem-thu-phan-mem-nhap-mon',
         description='Làm quen quy trình kiểm thử, thiết kế test case, phân vùng tương đương, giá trị biên và báo cáo lỗi. Gồm 4 bài đọc, tình huống thực hành và quiz 20 câu.', chapters=[
        ('Nền tảng kiểm thử', [
            ('Mục tiêu và các mức kiểm thử', '''Mục tiêu: giải thích giá trị kiểm thử và phân biệt các mức kiểm thử phổ biến.

Kiểm thử cung cấp thông tin về chất lượng và rủi ro của phần mềm. Nó có thể phát hiện lỗi nhưng một tập kiểm thử hữu hạn không chứng minh chương trình không còn lỗi. Kiểm thử nên bám yêu cầu, ngữ cảnh sử dụng và mức độ ảnh hưởng của sai sót.

Unit test tập trung vào đơn vị nhỏ như hàm hoặc lớp; integration test kiểm tra tương tác giữa các thành phần; system test kiểm tra hệ thống hoàn chỉnh; acceptance test đánh giá khả năng đáp ứng nhu cầu chấp nhận đã thống nhất. Ranh giới cụ thể phụ thuộc thiết kế hệ thống.

Kiểm thử tĩnh xem xét sản phẩm công việc mà không chạy phần mềm, như review yêu cầu hoặc mã nguồn. Kiểm thử động thực thi phần mềm và quan sát kết quả. Hai cách bổ sung cho nhau.

Tự luyện: với website học trực tuyến, đề xuất một unit test cho hàm tính điểm, một integration test giữa ghi danh và quyền học, một acceptance test cho quy trình học viên nộp quiz.''', [
                ('Mục tiêu phù hợp của kiểm thử là gì?', 'Cung cấp thông tin chất lượng và phát hiện vấn đề', 'Chứng minh tuyệt đối không còn lỗi', 'Thay thế mọi yêu cầu', 'Bảo đảm không cần bảo trì', 'Kiểm thử giảm bất định nhưng không chứng minh tuyệt đối phần mềm không có lỗi.'),
                ('Kiểm tra riêng một hàm tính điểm thường thuộc mức nào?', 'Unit test', 'Acceptance test luôn luôn', 'System test luôn luôn', 'Kiểm tra tải bắt buộc', 'Unit test tập trung vào một đơn vị nhỏ.'),
                ('Kiểm tra tương tác giữa API và cơ sở dữ liệu thường là gì?', 'Integration test', 'Chỉ kiểm thử tĩnh', 'Chỉ kiểm tra chính tả', 'Không phải kiểm thử', 'Integration test kiểm tra sự phối hợp giữa các thành phần.'),
                ('Acceptance test tập trung vào điều gì?', 'Tiêu chí chấp nhận và nhu cầu đã thống nhất', 'Chỉ số dòng mã', 'Chỉ tên biến', 'Chỉ màu bàn phím', 'Acceptance test đánh giá khả năng đáp ứng nhu cầu sử dụng theo tiêu chí chấp nhận.'),
                ('Review mã nguồn mà không chạy chương trình là gì?', 'Kiểm thử tĩnh', 'Kiểm thử tải', 'Kiểm thử động', 'Kiểm thử mạng bắt buộc', 'Hoạt động tĩnh không yêu cầu thực thi phần mềm.'),
            ]),
            ('Thiết kế test case', '''Mục tiêu: viết test case có thể lặp lại và đánh giá được.

Một test case nên có mục tiêu, điều kiện trước, dữ liệu đầu vào, các bước và kết quả mong đợi. Kết quả mong đợi cần cụ thể theo yêu cầu; câu như “hệ thống chạy tốt” không đủ để xác định pass hay fail.

Phân biệt kết quả mong đợi với kết quả thực tế. Khi chạy test, ghi môi trường và phiên bản để có thể tái hiện. Dữ liệu thử cần kiểm soát, không dùng tài khoản hoặc giao dịch thật nếu có môi trường kiểm thử riêng.

Bao phủ cả luồng hợp lệ và các tình huống không hợp lệ: thiếu trường bắt buộc, sai kiểu, không đủ quyền hoặc tài nguyên không tồn tại. Không chỉ kiểm tra giao diện báo thành công mà bỏ qua việc dữ liệu thực sự được lưu đúng.

Tự luyện: viết test case cho học viên chưa ghi danh mở bài có giới hạn. Ghi điều kiện trước, bước truy cập, kết quả về quyền và xác nhận không phát sinh tiến độ học trái phép.''', [
                ('Thành phần nào giúp quyết định test pass hay fail?', 'Kết quả mong đợi cụ thể', 'Tên máy tính duy nhất', 'Màu tài liệu', 'Số ký tự tên test', 'Cần đối chiếu kết quả thực tế với kết quả mong đợi.'),
                ('Điều kiện trước mô tả điều gì?', 'Trạng thái cần có trước khi thực hiện test', 'Chỉ lỗi đã tìm thấy', 'Kết quả sau cùng bắt buộc', 'Tên lập trình viên', 'Ví dụ tài khoản đã ghi danh là một điều kiện trước.'),
                ('Test đăng nhập chỉ dùng mật khẩu đúng đã đủ chưa?', 'Chưa, cần tình huống sai và dữ liệu không hợp lệ phù hợp', 'Đủ cho mọi yêu cầu', 'Không cần kết quả mong đợi', 'Không cần kiểm tra quyền', 'Luồng không hợp lệ có thể bộc lộ lỗi xác thực và xử lý đầu vào.'),
                ('Kết quả mong đợi nào kiểm chứng được rõ hơn?', 'API trả 403 và không tạo bản ghi tiến độ', 'Hệ thống tốt', 'Trang có vẻ ổn', 'Máy chạy nhanh', 'Mã phản hồi và trạng thái dữ liệu là các quan sát cụ thể.'),
                ('Vì sao ghi phiên bản và môi trường khi chạy test?', 'Giúp tái hiện và phân tích kết quả', 'Để bỏ qua lỗi', 'Để tăng số test giả', 'Để thay thế bước kiểm tra', 'Hành vi có thể khác theo cấu hình hoặc phiên bản.'),
            ]),
        ]),
        ('Kỹ thuật kiểm thử và xử lý lỗi', [
            ('Phân vùng tương đương và giá trị biên', '''Mục tiêu: chọn dữ liệu đại diện thay vì kiểm tra ngẫu nhiên mọi giá trị.

Phân vùng tương đương chia miền dữ liệu thành các nhóm dự kiến được xử lý tương tự, rồi chọn đại diện cho mỗi nhóm. Phải xét cả nhóm hợp lệ và không hợp lệ theo yêu cầu; đây là kỹ thuật lựa chọn test, không phải chứng minh mọi giá trị trong nhóm chắc chắn có hành vi giống nhau.

Với trường tuổi chỉ chấp nhận số nguyên từ 18 tới 60, có các vùng nhỏ hơn 18, từ 18 đến 60 và lớn hơn 60. Có thể chọn 17, 30, 61 làm đại diện. Kiểu đầu vào không phải số nguyên cũng cần xem xét theo hợp đồng dữ liệu.

Phân tích giá trị biên tập trung vào ranh giới vì lỗi so sánh và lệch một đơn vị thường xuất hiện ở đó. Với ví dụ trên, các điểm sát biên như 17,18,19 và 59,60,61 giúp kiểm tra cách xử lý ngưỡng dưới và trên.

Tự luyện: trường điểm nhận số nguyên 0–100. Liệt kê vùng hợp lệ, các vùng không hợp lệ và dữ liệu biên; nêu kết quả mong đợi cho từng giá trị.''', [
                ('Phân vùng tương đương giúp làm gì?', 'Chọn đại diện cho các nhóm đầu vào xử lý tương tự', 'Xóa toàn bộ test không hợp lệ', 'Chứng minh không còn lỗi', 'Chỉ kiểm tra giao diện', 'Chọn đại diện giúp giảm số lượng test có chủ đích.'),
                ('Tuổi hợp lệ là số nguyên 18–60. Giá trị nào thuộc vùng hợp lệ?', '30', '17', '61', '-1', '30 nằm trong khoảng bao gồm cả 18 và 60.'),
                ('Bộ nào kiểm tra sát biên dưới 18 cho đầu vào nguyên?', '17, 18, 19', '30, 31, 32', '40, 41, 42', '50, 51, 52', 'Các điểm ngay dưới, tại và ngay trên biên kiểm tra điều kiện ngưỡng.'),
                ('Điểm hợp lệ từ 0 đến 100. Giá trị 101 thuộc vùng nào?', 'Không hợp lệ phía trên', 'Hợp lệ', 'Không hợp lệ phía dưới', 'Luôn được làm tròn thành 100', '101 vượt giới hạn trên; không tự suy đoán hành vi làm tròn.'),
                ('Vì sao cần kiểm tra giá trị biên?', 'Dễ xuất hiện lỗi điều kiện và lệch một đơn vị', 'Mọi lỗi chỉ ở biên', 'Để bỏ qua yêu cầu', 'Để không cần kết quả mong đợi', 'Kiểm tra biên nhắm vào một nhóm lỗi phổ biến, không bao phủ mọi lỗi.'),
            ]),
            ('Báo cáo lỗi và kiểm thử hồi quy', '''Mục tiêu: báo lỗi đủ thông tin và xác nhận bản sửa một cách có căn cứ.

Báo cáo lỗi nên có tiêu đề ngắn, môi trường, điều kiện trước, bước tái hiện, kết quả thực tế, kết quả mong đợi và bằng chứng liên quan. Không đưa mật khẩu hoặc token vào ảnh chụp và nhật ký chia sẻ.

Severity mô tả mức độ ảnh hưởng của lỗi; priority mô tả thứ tự cần xử lý theo quyết định của nhóm. Hai yếu tố liên quan nhưng không đồng nhất: một lỗi giao diện nhỏ trên trang chiến dịch sắp ra mắt có thể được ưu tiên sớm.

Sau sửa lỗi, confirmation testing kiểm tra lại lỗi cụ thể đã được sửa. Regression testing kiểm tra các hành vi liên quan để tìm tác động phụ ngoài ý muốn. Test tự động có ích cho tình huống lặp lại nhưng vẫn cần dữ liệu và kết quả mong đợi đúng.

Tự luyện: báo lỗi “học viên hết lượt vẫn mở được quiz”. Viết bước tái hiện, kiểm tra trạng thái dữ liệu và đề xuất các test hồi quy cho trường hợp còn lượt và tiếp tục lượt đang làm.''', [
                ('Báo cáo lỗi cần thông tin nào để tái hiện?', 'Điều kiện trước và các bước thực hiện', 'Chỉ câu hệ thống lỗi', 'Chỉ tên người dùng', 'Chỉ màu màn hình', 'Các bước và điều kiện trước giúp người khác tái hiện lỗi.'),
                ('Severity thường thể hiện điều gì?', 'Mức độ ảnh hưởng của lỗi', 'Thứ tự xử lý duy nhất', 'Số người trong nhóm', 'Độ dài tiêu đề', 'Severity đánh giá ảnh hưởng; priority đánh giá mức ưu tiên xử lý.'),
                ('Kiểm tra lại chính lỗi vừa sửa gọi là gì?', 'Confirmation testing', 'Regression testing trong mọi trường hợp', 'Không phải kiểm thử', 'Review yêu cầu tĩnh bắt buộc', 'Confirmation testing xác nhận lỗi cụ thể được khắc phục.'),
                ('Kiểm thử hồi quy nhằm mục đích gì?', 'Phát hiện tác động phụ tới hành vi đã hoạt động', 'Chỉ kiểm tra lỗi vừa sửa', 'Thay thế mọi test mới', 'Tự động chứng minh không còn lỗi', 'Thay đổi có thể ảnh hưởng chức năng khác nên cần kiểm tra hồi quy phù hợp.'),
                ('Thông tin nào nên che khi chia sẻ bằng chứng lỗi?', 'Mật khẩu và token truy cập', 'Mã trạng thái HTTP công khai', 'Tên test case', 'Bước tái hiện không chứa bí mật', 'Thông tin xác thực không được đưa vào bằng chứng chia sẻ.'),
            ]),
        ]),
    ]),
]


def seed(apply=False):
    # All inserts use a single transaction. Existing courses are skipped by slug/title.
    report = []
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            teacher = conn.execute(text("SELECT id FROM users WHERE role='teacher' AND is_active=1 ORDER BY id LIMIT 1")).scalar()
            if not teacher:
                raise RuntimeError('Cần có ít nhất một tài khoản giảng viên đang hoạt động.')
            for course in COURSES:
                existing = conn.execute(text('SELECT id FROM courses WHERE slug=:slug OR title=:title'), course).scalar()
                if existing:
                    report.append(dict(title=course['title'], id=existing, state='skipped'))
                    continue
                cid = conn.execute(text("INSERT INTO courses (teacher_id,title,slug,description,price,level,status) VALUES (:teacher,:title,:slug,:description,0,'beginner','published')"), {**course, 'teacher': teacher}).lastrowid
                quiz_id = conn.execute(text("INSERT INTO quizzes (course_id,title,description,source,duration,passing_score,grading_method) VALUES (:c,:t,:d,'manual',30,70,'latest')"), dict(c=cid,t=f"Kiểm tra: {course['title']}",d='20 câu, 5 câu mỗi bài. Kết quả dùng để gợi ý chương và bài cần củng cố.')).lastrowid
                lesson_count = question_count = 0
                for chapter_index, (chapter_name, lessons) in enumerate(course['chapters'], 1):
                    chapter_id = conn.execute(text('INSERT INTO chapters (course_id,chapter_name,order_index) VALUES (:c,:n,:o)'), dict(c=cid,n=chapter_title(chapter_name, chapter_index),o=chapter_index)).lastrowid
                    for lesson_index, (title, description, questions) in enumerate(lessons, 1):
                        assert len(questions) == 5
                        lesson_id = conn.execute(text("INSERT INTO lessons (chapter_id,title,description,duration,order_index,is_free,status) VALUES (:ch,:t,:d,0,:o,1,'published')"), dict(ch=chapter_id,t=title,d=description,o=lesson_index)).lastrowid
                        topic_id = conn.execute(text('INSERT INTO course_topics (course_id,name,normalized_name,lesson_id,confirmed) VALUES (:c,:n,:k,:l,1)'), dict(c=cid,n=title,k=normalize_topic(title),l=lesson_id)).lastrowid
                        lesson_count += 1
                        for prompt, correct, b, c, d, explanation in questions:
                            # Rotate correct positions instead of always using option A.
                            position = question_count % 4
                            options = [b,c,d]
                            options.insert(position,correct)
                            assert len(set(options)) == 4
                            question_count += 1
                            conn.execute(text('''INSERT INTO questions (quiz_id,content,option_a,option_b,option_c,option_d,correct_answer,topic,topic_id,difficulty,explanation,order_index,knowledge_chapter_id,knowledge_lesson_id)
                                VALUES (:q,:content,:a,:b,:c,:d,:answer,:topic,:tid,'easy',:explanation,:o,:ch,:l)'''), dict(q=quiz_id,content=prompt,a=options[0],b=options[1],c=options[2],d=options[3],answer='ABCD'[position],topic=title,tid=topic_id,explanation=explanation,o=question_count,ch=chapter_id,l=lesson_id))
                assert lesson_count == 4 and question_count == 20
                # Verify saved classification is complete and belongs to this course.
                classified = conn.execute(text('''SELECT COUNT(*) FROM questions q JOIN lessons l ON l.id=q.knowledge_lesson_id
                    JOIN chapters ch ON ch.id=q.knowledge_chapter_id WHERE q.quiz_id=:q AND l.chapter_id=ch.id AND ch.course_id=:c'''),dict(q=quiz_id,c=cid)).scalar()
                assert classified == 20
                report.append(dict(title=course['title'],id=cid,state='created' if apply else 'preview',chapters=2,lessons=lesson_count,questions=question_count))
            if apply:
                transaction.commit()
            else:
                transaction.rollback()
        except BaseException:
            transaction.rollback()
            raise
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    print(json.dumps(seed(args.apply), ensure_ascii=True, indent=2))
