"""Original Vietnamese introductory lessons; questions are explicitly authored.

Q format: prompt | correct | distractor 1 | distractor 2 | distractor 3 | explanation.
"""


def lesson(title, goal, theory, example, task, solution, questions):
    items = [tuple(line.split(' | ')) for line in questions.strip().splitlines()]
    if len(items) != 5 or any(len(q) != 6 for q in items):
        raise ValueError(f'Invalid question set: {title}')
    return dict(title=title, body=f'''## Mục tiêu
{goal}

## Kiến thức trọng tâm
{theory}

## Ví dụ có hướng dẫn
{example}

## Bài tập thực hành
{task}

## Gợi ý tự kiểm tra
{solution}

## Tóm tắt
Sau bài này, hãy tự giải thích mục tiêu bằng lời của bạn và thực hiện lại ví dụ mà không nhìn hướng dẫn. Kết quả quiz giúp chọn phần cần ôn, không thay thế việc hoàn thành bài thực hành.
''', questions=items)


CURRICULUM = {
 'kiem-thu-phan-mem-nhap-mon': [
  ('Kiểm thử trong vòng đời phát triển', [
   lesson('SDLC, Agile và chiến lược kiểm thử',
    'Chọn hoạt động kiểm thử phù hợp giai đoạn phát triển và rủi ro sản phẩm.',
    '''SDLC mô tả hoạt động phát triển từ hiểu nhu cầu tới vận hành. Kiểm thử nên tham gia sớm qua review yêu cầu và tiêu chí chấp nhận, không chờ mã nguồn hoàn thành mới bắt đầu. Phát hiện yêu cầu mơ hồ sớm có thể tránh xây sai chức năng.

Trong phát triển lặp, kiểm thử được thực hiện xuyên suốt từng vòng. Definition of Done là thỏa thuận về điều kiện hoàn tất, khác tiêu chí chấp nhận cụ thể cho từng câu chuyện. Chất lượng là trách nhiệm chung; có tester không có nghĩa lập trình viên không cần kiểm tra.

Chiến lược chọn phạm vi, mức kiểm thử và mức tự động hóa theo rủi ro. Luồng thanh toán hoặc phân quyền có tác động lớn nên cần được ưu tiên hợp lý. Không thể kiểm thử mọi kết hợp vô hạn; cần ghi giả định, phần đã kiểm tra và rủi ro còn lại. Mô hình phát triển ảnh hưởng cách tổ chức nhưng không xóa nhu cầu có kết quả mong đợi.''',
    'Câu chuyện “học viên ghi danh khóa miễn phí” có tiêu chí: tài khoản hợp lệ, khóa xuất bản, không tạo ghi danh trùng và phản hồi rõ. Review các tiêu chí trước khi phát triển giúp làm rõ hành vi bấm hai lần.',
    'Viết tiêu chí chấp nhận cho đăng ký khóa, đề xuất hoạt động review, unit, integration và system trong một vòng phát triển. Nêu ba rủi ro cần ưu tiên.',
    'Phân biệt điều kiện hoàn tất chung với tiêu chí riêng của chức năng. Bao phủ tính đúng dữ liệu và quyền, không chỉ màu thông báo.',
    '''Kiểm thử nên bắt đầu khi nào? | Từ sớm, gồm review yêu cầu | Chỉ sau triển khai thật | Chỉ khi khách báo lỗi | Chỉ khi hết thời gian | Review sớm giúp phát hiện vấn đề trước khi viết mã.
Trong Agile, trách nhiệm chất lượng thuộc về ai? | Cả nhóm theo vai trò phối hợp | Chỉ tester | Chỉ khách hàng | Không ai | Chất lượng không được giao hoàn toàn cho một vai trò.
Tiêu chí chấp nhận mô tả điều gì? | Điều kiện cụ thể chức năng cần đáp ứng | Chỉ lịch nghỉ | Chỉ số dòng mã | Chỉ tên nhóm | Tiêu chí giúp đánh giá hành vi theo nhu cầu.
Khi thời gian có hạn, nên ưu tiên test theo gì? | Rủi ro và tác động nghiệp vụ | Thứ tự chữ cái tên test | Chỉ màu nút | Chọn ngẫu nhiên mọi lần | Ưu tiên dựa trên xác suất và ảnh hưởng sai sót.
Có thể kiểm tra hết mọi kết hợp đầu vào của mọi hệ thống không? | Thường không, cần chọn phạm vi có căn cứ | Luôn có thể trong một phút | Không cần test nào | Chỉ cần một tài khoản | Kiểm thử toàn bộ thường không khả thi với hệ thống thực tế.'''),
   lesson('Review yêu cầu và truy vết kiểm thử',
    'Phát hiện yêu cầu mơ hồ và liên kết test với mục tiêu nghiệp vụ.',
    '''Review tĩnh có thể áp dụng cho yêu cầu, thiết kế, test case và mã nguồn. Một yêu cầu tốt cần rõ ràng, nhất quán và có thể kiểm chứng. “Trang phải nhanh” cần ngữ cảnh đo như thao tác, tải, môi trường và ngưỡng trước khi chuyển thành kiểm thử hiệu năng.

Truy vết nối yêu cầu với test và kết quả hoặc lỗi liên quan. Ma trận có thể đơn giản: mã yêu cầu, ca kiểm thử, trạng thái, mã lỗi. Truy vết giúp nhìn phần chưa có test và xác định test bị ảnh hưởng khi yêu cầu đổi.

Bao phủ yêu cầu không chứng minh bao phủ tất cả rủi ro. Một test gắn mã yêu cầu nhưng không kiểm tra điều kiện quan trọng vẫn có thể bỏ sót lỗi. Review nên tập trung sản phẩm công việc, dùng ví dụ cụ thể và ghi kết luận; tránh biến thành đánh giá cá nhân.''',
    'REQ-01: một học viên chỉ có một ghi danh cho một khóa. Liên kết test đăng ký lần đầu, đăng ký lại và hai yêu cầu đồng thời; chỉ kiểm tra lần đầu chưa đủ.',
    'Viết lại yêu cầu “đăng ký dễ dàng” thành hành vi quan sát được. Lập bảng ba yêu cầu với ít nhất hai test mỗi yêu cầu và chỉ rõ bằng chứng cần thu thập.',
    'Có test cho đường thành công, lỗi và ràng buộc dữ liệu. Không dùng tỉ lệ test chạy qua làm bằng chứng duy nhất về mức bao phủ.',
    '''Review tĩnh có bắt buộc chạy phần mềm không? | Không | Có với mọi review | Chỉ khi đọc yêu cầu | Không thể review tài liệu | Review sản phẩm công việc có thể diễn ra trước thực thi.
Yêu cầu nào cần làm rõ trước khi kiểm thử? | Trang phải nhanh | Người chưa ghi danh nhận 403 khi mở bài giới hạn | Điểm là số nguyên từ 0 đến 100 | Tên khóa không được rỗng | Từ nhanh thiếu ngữ cảnh và tiêu chí đo.
Truy vết giúp điều gì khi yêu cầu thay đổi? | Tìm các test có thể bị ảnh hưởng | Tự sửa mọi lỗi | Thay thế kết quả mong đợi | Bỏ tất cả test cũ | Liên kết yêu cầu và test hỗ trợ phân tích tác động.
Một yêu cầu gắn đúng một test có luôn đủ bao phủ không? | Không | Có vô điều kiện | Có nếu tên test dài | Có nếu chạy nhanh | Một yêu cầu có thể có nhiều nhánh và điều kiện cần kiểm tra.
Review nên tập trung vào đâu? | Sản phẩm công việc và bằng chứng cụ thể | Phán xét cá nhân | Chỉ số giờ làm | Chỉ chức danh | Mục đích là cải thiện sản phẩm và phát hiện vấn đề.'''),
  ]),
  ('Thiết kế kiểm thử theo hành vi', [
   lesson('Bảng quyết định và tổ hợp điều kiện',
    'Chuyển quy tắc nghiệp vụ nhiều điều kiện thành các ca kiểm thử rõ ràng.',
    '''Bảng quyết định biểu diễn điều kiện và hành động theo từng quy tắc. Hữu ích khi kết quả phụ thuộc nhiều điều kiện kết hợp. Mỗi cột có thể mô tả một tổ hợp cùng hành vi mong đợi; cần phân biệt tổ hợp không thể xảy ra với tổ hợp chưa được kiểm tra.

Ví dụ quyền học phụ thuộc tài khoản hợp lệ, trạng thái ghi danh và nội dung miễn phí. Đặt giả định rõ trước khi lập bảng. Không mặc định mọi ứng dụng có cùng thứ tự ưu tiên giữa các điều kiện; cần hỏi hoặc xác nhận yêu cầu nếu quy tắc xung đột.

Khi số điều kiện tăng, số tổ hợp tăng nhanh. Có thể nhóm các quy tắc tương đương hoặc chọn kỹ thuật giảm tổ hợp theo rủi ro, nhưng phải ghi giới hạn. Pairwise không bảo đảm tìm mọi lỗi cần ba điều kiện tương tác. Dữ liệu test phải thực sự tạo được trạng thái đã mô tả.''',
    'Giả sử bài miễn phí cho phép xem không cần ghi danh; bài trả phí chỉ cho người đã ghi danh. Lập bốn tổ hợp free/enrolled và gắn kết quả cho phép hoặc chặn, trong phạm vi tài khoản hợp lệ.',
    'Lập bảng cho giảm giá chỉ khi có mã hợp lệ và tổng tiền đạt ngưỡng. Viết test cho bốn tổ hợp, thêm tình huống mã hết hạn theo yêu cầu cụ thể.',
    'Hai điều kiện nhị phân có bốn tổ hợp trước khi rút gọn. Với phép AND, chỉ tổ hợp cả hai đúng được giảm giá.',
    '''Bảng quyết định phù hợp khi nào? | Kết quả phụ thuộc tổ hợp nhiều điều kiện | Chỉ đo màu ảnh | Không có quy tắc nào | Chỉ đếm dòng mã | Bảng nối các tổ hợp điều kiện với hành động.
Hai điều kiện đúng/sai độc lập có bao nhiêu tổ hợp? | 4 | 2 | 3 | 8 | Mỗi điều kiện có hai giá trị nên có 2 nhân 2 tổ hợp.
Với giảm giá khi A AND B, trường hợp nào được giảm? | A và B đều đúng | Chỉ A đúng | Chỉ B đúng | Cả hai sai | AND yêu cầu cả hai điều kiện thỏa.
Tổ hợp không thể xảy ra nên được xử lý thế nào? | Ghi rõ lý do loại trừ theo yêu cầu | Âm thầm coi đã test qua | Tạo kết quả giả | Luôn giữ như test thành công | Cần minh bạch giả định và giới hạn của bảng.
Pairwise có bảo đảm tìm mọi lỗi ba điều kiện tương tác không? | Không | Có vô điều kiện | Có nếu đặt tên đẹp | Không cần dữ liệu | Bao phủ cặp không tương đương bao phủ mọi bộ ba.'''),
   lesson('Kiểm thử chuyển trạng thái',
    'Mô hình hóa vòng đời nghiệp vụ và kiểm tra chuyển trạng thái hợp lệ, không hợp lệ.',
    '''Mô hình trạng thái gồm trạng thái, sự kiện và chuyển tiếp. Kết quả của một hành động có thể phụ thuộc trạng thái trước đó. Ví dụ quiz đang làm, đã nộp hoặc hết thời gian không nên xử lý thao tác nộp giống nhau trong mọi trường hợp.

Bảng chuyển tiếp mô tả trạng thái đầu, hành động, trạng thái cuối và phản hồi. Ngoài đường hợp lệ, kiểm tra chuyển tiếp bị cấm như sửa câu trả lời sau khi đã nộp. Bao phủ trạng thái không đồng nghĩa bao phủ mọi chuyển tiếp giữa chúng.

Một lần chạy cần điều kiện khởi tạo rõ ràng và khả năng khôi phục dữ liệu. Với tác vụ bất đồng bộ, trạng thái giao diện và trạng thái server có thể cập nhật ở các thời điểm khác nhau; cần kiểm tra trạng thái có thẩm quyền. Không coi một nút bị ẩn là bằng chứng server đã ngăn hành động trái phép.''',
    'Luồng quiz: chưa bắt đầu → đang làm → đã nộp. Nộp lại cùng attempt không được tạo thêm kết quả ngoài quy tắc. Trạng thái hết giờ có thể dẫn tới tự nộp hoặc chặn theo yêu cầu đã xác nhận.',
    'Vẽ trạng thái của đơn hàng pending, paid, cancelled theo hợp đồng hệ thống. Viết ba chuyển tiếp hợp lệ và hai chuyển tiếp bị cấm; không dùng thanh toán thật.',
    'Nêu rõ sự kiện dẫn tới chuyển trạng thái và kiểm tra cả dữ liệu server. Yêu cầu nộp trùng cần có kết quả mong đợi cụ thể.',
    '''Kết quả thao tác trong hệ thống có trạng thái phụ thuộc gì? | Trạng thái trước và sự kiện | Chỉ màu nút | Chỉ tên người viết test | Chỉ độ dài URL | Cùng sự kiện có thể được xử lý khác ở mỗi trạng thái.
Bao phủ mọi trạng thái có bằng bao phủ mọi chuyển tiếp không? | Không | Có luôn luôn | Có nếu chỉ một tài khoản | Không cần xem chuyển tiếp | Các đường nối trạng thái là mục tiêu bao phủ riêng.
Ẩn nút nộp sau hoàn tất đã chứng minh server chặn nộp lại chưa? | Chưa | Có tuyệt đối | Có nếu nút màu xám | Không cần server kiểm tra | Phải kiểm tra quy tắc tại API hoặc server.
Test chuyển tiếp cần ghi thông tin nào? | Trạng thái đầu, sự kiện và kết quả mong đợi | Chỉ tiêu đề | Chỉ ảnh nền | Chỉ tổng số nút | Các thành phần mô tả được luồng cần xác minh.
Với chức năng bất đồng bộ nên đối chiếu thêm gì? | Trạng thái server có thẩm quyền | Chỉ văn bản nút | Chỉ âm thanh | Không cần chờ phản hồi | Giao diện có thể cập nhật trước hoặc sau dữ liệu thực.'''),
  ]),
  ('Kiểm thử dữ liệu và dịch vụ', [
   lesson('Kiểm thử API và phân quyền',
    'Thiết kế ca kiểm thử hợp đồng HTTP và quyền truy cập theo tài khoản.',
    '''API test cần kiểm tra phương thức, đường dẫn, tham số, kiểu dữ liệu, mã trạng thái và nội dung phản hồi theo hợp đồng. Mã 200 không đủ chứng minh đúng: cần xác nhận dữ liệu, tác dụng phụ và quyền. Lỗi có thể nằm ở nghiệp vụ dù phản hồi vẫn là JSON hợp lệ.

Phân biệt xác thực danh tính với phân quyền tài nguyên. Kiểm tra người chưa đăng nhập, đúng chủ sở hữu, người khác và vai trò quản trị theo yêu cầu. Thay ID tài nguyên là tình huống kiểm tra quyền ở mức đối tượng quan trọng; chỉ thực hiện trên dữ liệu lab được phép.

Test đầu vào gồm thiếu trường, sai kiểu, giá trị biên và tài nguyên không tồn tại. Không đưa token vào báo cáo hoặc nguồn mã. Tạo dữ liệu test riêng và dọn trong phạm vi đó. Các mã phản hồi cụ thể phụ thuộc hợp đồng API, không suy ra mọi lỗi đều phải cùng một mã.''',
    'GET kết quả quiz của chính mình được phép. Đổi result_id sang bài của tài khoản lab khác phải bị từ chối theo hợp đồng; kiểm tra nội dung phản hồi không lộ dữ liệu dù mã trạng thái có vẻ đúng.',
    'Lập năm test cho API đăng ký: hợp lệ, khóa không tồn tại, thiếu xác thực, đăng ký trùng và ID sai kiểu. Nêu điều kiện dữ liệu trước/sau, dùng môi trường thử nghiệm.',
    'Kiểm tra đồng thời mã, schema, quyền và tác dụng dữ liệu. Không ghi token thật vào minh chứng.',
    '''API trả 200 đã đủ kết luận đúng nghiệp vụ chưa? | Chưa, cần kiểm tra nội dung và dữ liệu | Đủ tuyệt đối | Đủ nếu JSON dài | Không cần hợp đồng | Thành công HTTP không bảo đảm kết quả nghiệp vụ đúng.
Xác thực trả lời câu hỏi nào? | Người gọi là ai | Người gọi được làm mọi việc gì | Máy có bao nhiêu RAM | Tài nguyên màu gì | Authentication xác định danh tính.
Phân quyền trả lời câu hỏi nào? | Người gọi được phép truy cập gì | Mật khẩu có bao nhiêu ký tự luôn luôn | Tên miền nào dài nhất | Trình duyệt nào mới | Authorization áp dụng quyền trên thao tác và tài nguyên.
Đổi ID sang tài nguyên của tài khoản khác nhằm kiểm tra gì? | Quyền ở mức đối tượng | Chỉ tốc độ tải ảnh | Chỉ chính tả | Chỉ dung lượng ổ đĩa | Server phải kiểm tra quyền với tài nguyên được yêu cầu.
Token test nên được quản lý thế nào? | Giữ bí mật và không đưa vào báo cáo | Dán công khai vào ảnh | Commit mọi token thật | Dùng chung tài khoản thật của khách | Token là thông tin xác thực cần bảo vệ.'''),
   lesson('Kiểm thử cơ sở dữ liệu và tính toàn vẹn',
    'Đối chiếu thao tác ứng dụng với ràng buộc dữ liệu và rollback trong môi trường test.',
    '''Kiểm thử dữ liệu xác nhận bản ghi được tạo, cập nhật hoặc giữ nguyên đúng yêu cầu. Kiểm tra khóa ngoại, tính duy nhất, giá trị NULL và ràng buộc miền. Với ghi danh, một cặp học viên–khóa có thể cần duy nhất; chỉ chặn bấm hai lần ở giao diện không đủ xử lý hai yêu cầu đồng thời.

Transaction nhóm thay đổi thành đơn vị công việc. Nếu một bước thất bại, rollback giúp tránh trạng thái một phần theo thiết kế giao dịch. Test cần xác minh trạng thái trước/sau, không chỉ thấy thông báo lỗi là cho rằng dữ liệu chưa đổi.

Dùng database test hoặc bản sao đã được phép, đánh dấu dữ liệu tạo cho test và dọn đúng phạm vi. Không chạy lệnh xóa hàng loạt trên dữ liệu học viên thật. Cần tính cả số bản ghi, liên kết và trường quan trọng; một phép COUNT không chứng minh mọi trường đã đúng.''',
    'Hai yêu cầu đăng ký cùng khóa đến gần nhau. Ràng buộc unique và xử lý server phải bảo đảm chỉ một ghi danh; giao diện cần phản hồi theo hợp đồng thay vì báo thành công hai bản ghi.',
    'Thiết kế test chèn trùng, khóa ngoại không tồn tại và lỗi ở bước hai của giao dịch. Ghi trạng thái mong đợi của cả hai bảng, thực hiện trên database test.',
    'Sau rollback đúng thiết kế, không còn thay đổi một phần trong giao dịch đó. Việc dọn test phải dựa vào ID test đã tạo.',
    '''Ràng buộc unique thường dùng để làm gì? | Ngăn giá trị hoặc tổ hợp khóa bị trùng theo quy tắc | Mã hóa dữ liệu | Tăng số bản ghi | Tự tạo video | Unique biểu diễn tính duy nhất ở mức database.
Khóa ngoại hỗ trợ điều gì? | Toàn vẹn tham chiếu | Tăng độ phân giải ảnh | Định tuyến mạng | Tự sửa mọi nghiệp vụ | Khóa ngoại liên kết tới bản ghi hợp lệ theo ràng buộc.
Chỉ khóa nút đăng ký có xử lý chắc chắn yêu cầu đồng thời không? | Không | Có vô điều kiện | Có nếu nút xanh | Không cần server | Hai client hoặc hai request vẫn có thể đến server.
Rollback được dùng để làm gì? | Hoàn tác thay đổi chưa commit của giao dịch | Xóa mọi dữ liệu hệ thống | Bỏ qua lỗi | Tự xác nhận thanh toán | Rollback xử lý thay đổi trong phạm vi transaction.
Môi trường nào phù hợp cho test ghi/xóa dữ liệu? | Database test hoặc bản sao được phép | Database thật tùy ý | Tài khoản khách bất kỳ | Mọi hệ thống công khai | Dữ liệu thử cần được cô lập và kiểm soát.'''),
  ]),
  ('Chất lượng và thực hành tổng hợp', [
   lesson('Hiệu năng, khả dụng và tương thích',
    'Viết tiêu chí đo chất lượng ngoài chức năng trong phạm vi lab.',
    '''Kiểm thử phi chức năng xem đặc tính như hiệu năng, khả dụng, khả năng tiếp cận và tương thích. Một chức năng đúng kết quả nhưng chậm hoặc không thao tác được bằng bàn phím vẫn có thể không đáp ứng nhu cầu người dùng.

Hiệu năng cần mô hình tải, dữ liệu, môi trường, thước đo và ngưỡng đã thống nhất. Thời gian phản hồi, thông lượng và tỉ lệ lỗi là các thước đo khác nhau. Percentile như p95 mô tả phần lớn mẫu tốt hơn một trung bình đơn lẻ khi có đuôi chậm. Đo tải chỉ trên hệ thống được phép và có giới hạn để tránh ảnh hưởng người dùng.

Kiểm tra giao diện với tên dài, màn hình hẹp, phóng to và thao tác bàn phím. Thông báo cần rõ, không chỉ dùng màu để truyền trạng thái. Kiểm tra tương thích theo tập trình duyệt/thiết bị được hỗ trợ; không tuyên bố đã thử mọi nền tảng nếu chỉ có một môi trường.''',
    'Thông báo đăng ký ở góc màn hình cần đọc được trên điện thoại, không che nút quan trọng và có thể đóng bằng bàn phím. Test kích thước hẹp và nội dung dài thay vì chỉ ảnh desktop.',
    'Viết checklist 8 mục cho trang khóa học: ít nhất hai mục về bàn phím, hai về màn hình hẹp, hai về nội dung dài và hai về hiệu năng có điều kiện đo.',
    'Ghi rõ môi trường và tiêu chí, không dùng câu “rất nhanh” hay “đẹp” làm kết quả mong đợi duy nhất. p95 không phải giá trị chậm nhất tuyệt đối.',
    '''Kiểm thử phi chức năng xem xét gì? | Đặc tính chất lượng như hiệu năng và khả dụng | Chỉ phép cộng điểm | Chỉ đăng nhập đúng mật khẩu | Chỉ số bản ghi | Phi chức năng đánh giá cách hệ thống đáp ứng ngoài kết quả nghiệp vụ.
Để tiêu chí hiệu năng kiểm chứng được cần gì? | Tải, môi trường, thước đo và ngưỡng | Chỉ từ nhanh | Chỉ ảnh chụp | Chỉ tên máy chủ | Các điều kiện đo làm kết quả có ý nghĩa.
p95 thời gian phản hồi thường diễn đạt điều gì? | Khoảng 95% mẫu không vượt ngưỡng đó | Mọi mẫu đều bằng nhau | Giá trị tối đa tuyệt đối | Số người đăng nhập | Percentile mô tả phân bố mẫu đo.
Vì sao không nên chỉ dùng màu báo lỗi? | Người dùng cần tín hiệu văn bản hoặc biểu tượng dễ hiểu | Mọi người nhìn màu giống nhau | Văn bản luôn thừa | Màu tự tạo âm thanh | Trạng thái cần được truyền bằng nhiều dấu hiệu có thể tiếp cận.
Test tải nên thực hiện ở đâu? | Hệ thống được phép với giới hạn đã xác định | Mọi website công khai | Máy chủ khách không thông báo | Chỉ chọn URL ngẫu nhiên | Hoạt động tải cần phạm vi và kiểm soát tác động.'''),
   lesson('Dự án nhỏ: kế hoạch kiểm thử và tự động hóa',
    'Tạo gói kiểm thử có thể chạy lại cho một chức năng học trực tuyến.',
    '''Tự động hóa phù hợp với ca lặp lại, kết quả mong đợi ổn định và giá trị phát hiện lỗi đủ lớn so với chi phí bảo trì. Không tự động hóa mọi thao tác chỉ vì có công cụ. Tách unit test nhanh, API/integration và một số luồng giao diện quan trọng theo nhu cầu sản phẩm.

Một test tốt có chuẩn bị, hành động và kiểm tra kết quả cụ thể. Các test nên độc lập, dữ liệu có thể tái tạo và dọn trong phạm vi đã tạo. Khi test chập chờn, tìm nguyên nhân như chờ bất đồng bộ hoặc phụ thuộc thứ tự, không đơn giản chạy lại tới khi xanh rồi bỏ qua.

Dự án chọn chức năng ghi danh hoặc nộp quiz: lập phạm vi, rủi ro, test case, dữ liệu, báo cáo lỗi và kết quả hồi quy. Phân biệt chức năng chưa kiểm tra với test đã qua. Tài liệu kết thúc phải nêu rủi ro còn lại; quiz không tự xác nhận bộ test thực tế đã được triển khai.''',
    'Test ghi danh xác nhận request thành công, bản ghi tồn tại đúng một lần và quyền mở bài được cập nhật. Một test khác dùng dữ liệu riêng cho đăng ký trùng; không phụ thuộc test trước đã chạy.',
    'Nộp kế hoạch một trang, 12 test gồm quyền/biên/trạng thái/dữ liệu, hai báo cáo lỗi mẫu ghi rõ là tình huống giả định và ba test tự động có thể chạy lại trên lab. Không tạo lỗi hoặc kết quả giả vào hệ thống thật.',
    'Đánh giá theo tiêu chí: truy vết yêu cầu, kết quả mong đợi rõ, dữ liệu độc lập, kiểm tra có ý nghĩa, bằng chứng chạy và giới hạn. Không tính số lượng test là thước đo duy nhất.',
    '''Ca nào thường phù hợp tự động hóa? | Ca lặp lại có kỳ vọng ổn định và giá trị rõ | Mọi ý tưởng chưa có yêu cầu | Mọi bước bất kể chi phí | Chỉ thao tác ngẫu nhiên | Cần cân nhắc giá trị và bảo trì.
Ba phần cơ bản của test thường là gì? | Chuẩn bị, hành động, kiểm tra | Đổi màu, chụp ảnh, thoát | Chỉ chạy chương trình | Chỉ ghi tên test | Test cần thiết lập trạng thái, thực hiện và xác minh.
Test độc lập có lợi ích gì? | Giảm phụ thuộc thứ tự chạy | Bắt buộc chia sẻ dữ liệu thật | Không cần kết quả mong đợi | Không cần dọn dữ liệu | Có thể chạy lại riêng và theo thứ tự khác.
Test chập chờn nên được xử lý thế nào? | Tìm nguyên nhân dữ liệu, thời gian hoặc phụ thuộc | Chạy lại tới khi qua rồi bỏ qua | Xóa mọi kiểm tra | Luôn kết luận sản phẩm đúng | Flaky test làm giảm độ tin cậy của phản hồi.
Báo cáo kết thúc kiểm thử cần nêu gì? | Phạm vi, kết quả và rủi ro còn lại | Chỉ tổng số test qua | Chỉ số giờ làm | Tuyên bố không còn lỗi tuyệt đối | Người đọc cần hiểu cả bằng chứng lẫn giới hạn.'''),
  ]),
 ],
 'mang-may-tinh-co-ban': [
  ('Ethernet và mạng cục bộ', [
   lesson('Ethernet, địa chỉ MAC và ARP',
    'Theo dõi việc gửi một gói IPv4 trong LAN; phân biệt địa chỉ IP với MAC.',
    '''Ethernet truyền khung giữa các giao diện trong một mạng cục bộ. Khung có địa chỉ MAC nguồn và đích; gói IP nằm trong phần tải của khung. Switch học MAC nguồn và cổng nhận, sau đó dùng bảng MAC để quyết định cổng chuyển tiếp. Không nên nhầm bảng MAC với bảng định tuyến.

ARP giúp tìm địa chỉ MAC tương ứng một IPv4 trên liên kết cục bộ. Host phát ARP request dạng broadcast, thiết bị sở hữu IPv4 trả lời. Kết quả có thể được lưu tạm trong ARP cache. IPv6 dùng Neighbor Discovery thay cho ARP.

Nếu đích nằm ngoài mạng con, host tìm MAC của gateway, không ARP trực tiếp địa chỉ máy chủ xa. Khi qua router, khung lớp liên kết được tạo lại cho chặng tiếp theo; địa chỉ MAC không đi xuyên suốt Internet. Chỉ quan sát ARP trong mạng lab hoặc mạng bạn được phép quản lý.''',
    'A có IP 192.168.10.2/24, B có IP 192.168.10.3/24. A chưa biết MAC của B nên gửi ARP request. Khi gửi tới 8.8.8.8, A sử dụng MAC của default gateway trong khung Ethernet.',
    'Vẽ khung và gói khi A gửi tới B, rồi tới máy chủ ngoài LAN. Ghi MAC đích của khung trong từng trường hợp. Quan sát bảng ARP bằng arp -a trong máy lab.',
    'Cùng mạng: MAC của B. Ngoài mạng: MAC gateway. Không kết luận rằng địa chỉ IP và MAC là hai cách viết của cùng một định danh.',
    '''ARP dùng trong tình huống nào? | Tìm MAC ứng với IPv4 trên liên kết cục bộ | Tìm mật khẩu Wi-Fi | Cấp tên miền | Mã hóa HTTP | ARP ánh xạ IPv4 sang MAC trong LAN.
Host gửi gói tới mạng khác thường dùng MAC đích nào trong khung đầu tiên? | MAC của gateway | MAC máy chủ xa lấy trực tiếp qua ARP | MAC của bàn phím | Không có MAC đích | Gateway là chặng tiếp theo trên liên kết cục bộ.
Switch lớp 2 học bảng MAC từ đâu? | MAC nguồn và cổng nhận khung | Tên miền trong URL | Điểm quiz | Tên tệp tải xuống | Switch học địa chỉ nguồn tại cổng nhận.
IPv6 sử dụng cơ chế nào thay ARP? | Neighbor Discovery | FTP | HTTP cookie | SMTP | IPv6 dùng Neighbor Discovery dựa trên ICMPv6.
Khi gói qua router, điều gì thường xảy ra với khung lớp liên kết? | Được tạo lại cho liên kết tiếp theo | Giữ nguyên MAC mọi chặng | Biến thành mật khẩu | Không còn gói IP | Router chuyển tiếp gói trong một khung phù hợp liên kết mới.'''),
   lesson('VLAN và kết nối Wi-Fi',
    'Giải thích phân đoạn LAN bằng VLAN và lựa chọn cấu hình Wi-Fi cơ bản.',
    '''VLAN chia hạ tầng switch thành các miền broadcast logic. Hai cổng access thuộc hai VLAN khác nhau không tự trao đổi như cùng một LAN chỉ vì nối chung switch. Muốn liên lạc giữa VLAN thường cần định tuyến và chính sách cho phép. Trunk có thể mang nhiều VLAN với cơ chế gắn thẻ như IEEE 802.1Q.

Wi-Fi là kết nối vô tuyến qua điểm truy cập. SSID là tên mạng được công bố, không phải mật khẩu. Nhiễu, vật cản, số thiết bị và vị trí AP đều ảnh hưởng chất lượng. Băng 5 GHz thường có nhiều lựa chọn kênh hơn 2,4 GHz nhưng không bảo đảm xuyên vật cản tốt hơn.

Dùng cơ chế bảo vệ được thiết bị hỗ trợ như WPA2 hoặc WPA3, mật khẩu riêng đủ mạnh và firmware được cập nhật. Không coi ẩn SSID là thay thế mã hóa. VLAN là phân đoạn logic, không tự mã hóa nội dung; quyền truy cập giữa các vùng vẫn cần được thiết kế.''',
    'Phòng thực hành chia VLAN 10 cho học viên, VLAN 20 cho giảng viên. Một trunk nối hai switch mang cả hai VLAN. SSID Guest có thể gắn vào một vùng riêng với chính sách hạn chế truy cập nội bộ.',
    'Vẽ sơ đồ hai nhóm người dùng trên hai switch. Chỉ ra cổng access, trunk, thiết bị định tuyến và chính sách cần kiểm tra khi mạng khách không được truy cập máy chủ nội bộ.',
    'Cùng VLAN có thể trải trên nhiều switch qua trunk. Khác VLAN cần đường định tuyến phù hợp; đặt tên SSID khác nhau chưa tự chứng minh đã cách ly mạng.',
    '''VLAN chủ yếu dùng để làm gì? | Chia miền broadcast logic | Mã hóa tất cả dữ liệu | Tăng RAM | Thay mọi router | VLAN phân đoạn lớp liên kết thành các miền logic.
Cổng trunk thường có nhiệm vụ gì? | Mang lưu lượng nhiều VLAN | Chỉ nhận bàn phím | Cấp mật khẩu | Chạy DNS bắt buộc | Trunk cho phép nhiều VLAN dùng chung liên kết.
SSID là gì? | Tên mạng Wi-Fi | Mật khẩu bắt buộc của router | Địa chỉ IPv4 | Mã HTTP | SSID nhận diện mạng không dây.
Hai VLAN khác nhau thường cần gì để trao đổi IP? | Định tuyến giữa VLAN và chính sách cho phép | Chỉ đặt cùng tên máy | Chỉ đổi ảnh nền | Không bao giờ liên lạc được | Phân đoạn VLAN cần lớp định tuyến để trao đổi giữa các mạng.
Ẩn SSID có thay thế mã hóa Wi-Fi không? | Không | Có trong mọi trường hợp | Chỉ cần ẩn là an toàn tuyệt đối | Ẩn SSID chính là HTTPS | Ẩn tên mạng không cung cấp bảo đảm mã hóa.'''),
  ]),
  ('Cấp phát địa chỉ và chuyển tiếp', [
   lesson('DHCP và NAT trong mạng gia đình',
    'Mô tả cấp phát cấu hình tự động và phân biệt với chuyển đổi địa chỉ.',
    '''DHCPv4 cấp cấu hình IP theo thời hạn thuê. Trong luồng cấp mới điển hình, client gửi Discover, server Offer, client Request rồi server Acknowledge. Cấu hình có thể gồm địa chỉ IP, subnet mask, gateway và DNS. DHCP không phải dịch vụ phân giải tên.

NAT chuyển đổi địa chỉ khi gói đi qua thiết bị biên. PAT thường cho nhiều host dùng chung một IPv4 công khai bằng cách phân biệt thêm cổng giao vận. Router duy trì trạng thái ánh xạ cho lưu lượng phản hồi. NAT không đồng nghĩa với tường lửa và không thay thế kiểm soát truy cập.

Nếu một máy không lấy được cấu hình, cần kiểm tra liên kết, DHCP server, phạm vi cấp phát và xung đột. Địa chỉ 169.254.x.x có thể là địa chỉ link-local tự gán, không mặc nhiên là cấu hình Internet hoạt động. Trước khi đổi cấu hình, ghi nhận giá trị hiện tại để có thể khôi phục.''',
    'Laptop nhận 192.168.1.20/24, gateway 192.168.1.1 từ DHCP. Khi truy cập web, router dùng NAT/PAT ánh xạ phiên của laptop ra địa chỉ công khai. Một việc cấp cấu hình, một việc chuyển đổi lưu lượng.',
    'Trên mạng lab, liệt kê địa chỉ IP, mask, gateway, DNS và thời hạn thuê. Vẽ hai máy truy cập cùng một web server qua PAT, đánh dấu cổng nguồn khác nhau.',
    'Không dùng IP riêng làm bằng chứng về địa chỉ công khai. Hai máy có thể chia sẻ IP công khai nhưng có các ánh xạ cổng riêng.',
    '''Chuỗi cấp mới DHCPv4 điển hình là gì? | Discover, Offer, Request, Acknowledge | GET, POST, PUT, DELETE | ARP, TLS, HTTP, DNS | SYN, FIN, RST, ACK | DORA mô tả luồng cấp mới DHCP phổ biến.
DHCP có thể cung cấp thông tin nào? | IP, mask, gateway và DNS | Chỉ mật khẩu tài khoản | Chỉ nội dung website | Chỉ địa chỉ MAC vật lý mới | DHCP phân phối các tùy chọn cấu hình mạng.
PAT phân biệt nhiều kết nối chung IP công khai bằng gì? | Cổng giao vận trong ánh xạ | Tên người dùng luôn luôn | Màu dây mạng | Tên khóa học | PAT sử dụng thông tin cổng cùng địa chỉ để phân biệt luồng.
NAT có thay thế tường lửa không? | Không | Có trong mọi mạng | NAT chính là TLS | NAT bảo đảm không có tấn công | Chuyển đổi địa chỉ khác với chính sách lọc truy cập.
Máy chỉ có 169.254.x.x sau khi không nhận DHCP cần kiểm tra gì? | Liên kết và khả năng cấp cấu hình DHCP | Chỉ đổi tên tệp | Xóa trình duyệt | Kết luận Internet chắc chắn hoạt động | Link-local không chứng minh đã nhận được cấu hình ra Internet.'''),
   lesson('Định tuyến cơ bản và làm quen IPv6',
    'Đọc tuyến mặc định, chọn tuyến theo tiền tố dài nhất và nhận diện IPv6.',
    '''Router chọn tuyến phù hợp địa chỉ đích; khi có nhiều tiền tố khớp, nguyên tắc tiền tố dài nhất giúp chọn tuyến cụ thể nhất. Tuyến mặc định IPv4 là 0.0.0.0/0, được dùng khi không có tuyến cụ thể hơn. Một tuyến mô tả mạng đích cùng next hop hoặc giao diện ra.

IPv6 có địa chỉ 128 bit, viết bằng các nhóm thập lục phân. Có thể bỏ số 0 đầu mỗi nhóm và rút gọn một chuỗi nhóm 0 bằng dấu :: một lần trong một địa chỉ. IPv6 không dùng broadcast như IPv4; multicast có vai trò quan trọng trong nhiều giao thức.

Địa chỉ link-local IPv6 dùng trên liên kết cục bộ. Host có thể chạy IPv4 và IPv6 đồng thời theo dual stack. Không chỉ kiểm tra có địa chỉ: muốn liên lạc còn cần tuyến, dịch vụ và chính sách phù hợp. Bài này chưa đi sâu OSPF, BGP hoặc cấu hình định tuyến động.''',
    'Bảng có 10.0.0.0/8 qua R1 và 10.1.0.0/16 qua R2. Gói tới 10.1.2.3 chọn tuyến /16. Nếu chỉ có default route cho một đích công khai, gói đi theo default route.',
    'Với các tuyến /0, 192.168.0.0/16 và 192.168.2.0/24, chọn tuyến cho 192.168.2.9. Rút gọn 2001:0db8:0000:0000:0000:0000:0000:0001.',
    'Chọn /24 vì cụ thể nhất. IPv6 rút gọn thành 2001:db8::1; không dùng hai dấu :: trong cùng địa chỉ.',
    '''Khi nhiều tuyến đều khớp đích, ưu tiên thông thường là gì? | Tiền tố dài nhất | Tiền tố ngắn nhất luôn luôn | Tên tuyến dài nhất | Chọn ngẫu nhiên bắt buộc | Longest-prefix match chọn tuyến cụ thể nhất.
Tuyến mặc định IPv4 viết thế nào? | 0.0.0.0/0 | 255.255.255.255/32 | 127.0.0.1/32 | 192.168.1.1/24 luôn luôn | /0 khớp mọi địa chỉ khi không có tuyến cụ thể hơn.
IPv6 có độ dài địa chỉ bao nhiêu? | 128 bit | 32 bit | 48 bit | 16 bit | IPv6 dùng không gian địa chỉ 128 bit.
Dấu :: có thể dùng tối đa mấy lần trong một địa chỉ IPv6? | Một lần | Hai lần bắt buộc | Tùy ý không giới hạn | Không bao giờ | Chỉ một vị trí rút gọn để khôi phục số nhóm 0 một cách rõ ràng.
Dual stack nghĩa là gì? | Cùng hỗ trợ IPv4 và IPv6 | Hai mật khẩu Wi-Fi | Hai trình duyệt | Chỉ dùng IPv6 | Dual stack vận hành hai bộ giao thức IP song song.'''),
  ]),
  ('Giao vận và vận hành an toàn', [
   lesson('Cổng, socket và vòng đời kết nối TCP',
    'Phân biệt cổng dịch vụ với địa chỉ IP; mô tả bắt tay TCP.',
    '''Địa chỉ IP nhận diện giao diện ở tầng mạng; cổng giúp phân biệt ứng dụng ở tầng giao vận. Một dịch vụ lắng nghe tại địa chỉ và cổng, còn client thường dùng cổng nguồn tạm thời. Cùng số cổng nhưng TCP và UDP là hai không gian khác nhau.

TCP mở kết nối điển hình bằng SYN, SYN-ACK, ACK. Số thứ tự và xác nhận hỗ trợ truyền luồng byte có thứ tự. TCP không giữ ranh giới thông điệp ứng dụng; chương trình cần tự xác định độ dài hoặc ký hiệu kết thúc thông điệp. Đóng kết nối và timeout cũng cần được xử lý.

Một phiên TCP thường được nhận diện bằng cặp IP/cổng hai đầu trong ngữ cảnh giao thức. Không thể kết luận dịch vụ an toàn chỉ vì dùng cổng quen thuộc. Khi kiểm tra kết nối, phân biệt không tới được host, không có dịch vụ lắng nghe, bị lọc và sai giao thức ứng dụng.''',
    'Client 192.168.1.20:51000 kết nối server:443 bằng TCP. Một client khác có thể cùng truy cập server:443 nhưng có địa chỉ hoặc cổng nguồn khác; server không nhầm hai phiên.',
    'Vẽ ba bước bắt tay. Giải thích tại sao hai lần ghi dữ liệu ở ứng dụng không bảo đảm bên nhận có đúng hai lần đọc tương ứng. Chỉ thử kết nối tới dịch vụ lab bạn được phép dùng.',
    'TCP là luồng byte; ứng dụng phải đóng khung thông điệp. Bắt tay thành công chưa chứng minh đăng nhập hoặc nghiệp vụ thành công.',
    '''Cổng ở tầng giao vận giúp phân biệt điều gì? | Ứng dụng hoặc dịch vụ | Độ dài dây mạng | Màu thiết bị | Số chương học | Cổng tách các endpoint ứng dụng trên host.
Bắt tay TCP điển hình có thứ tự nào? | SYN, SYN-ACK, ACK | FIN, DNS, ARP | GET, PUT, POST | DHCP, NAT, VLAN | Ba bước đồng bộ và xác nhận mở kết nối.
TCP cung cấp kiểu dữ liệu trao đổi nào? | Luồng byte có thứ tự | Các thông điệp luôn giữ nguyên ranh giới ghi | Chỉ video | Chỉ bản ghi DNS | TCP không bảo toàn ranh giới thông điệp ứng dụng.
Hai client cùng truy cập cổng 443 có thể được phân biệt nhờ gì? | IP và cổng hai đầu kết nối | Chỉ tên website | Chỉ mã 200 | Chỉ địa chỉ MAC server trên Internet | Các endpoint phân biệt từng kết nối TCP.
Kết nối TCP thành công chứng minh điều gì? | Đã thiết lập kết nối giao vận tới endpoint | Đăng nhập chắc chắn thành công | Mọi dữ liệu đã mã hóa | Mọi nghiệp vụ đúng | Giao vận thành công không đồng nghĩa nghiệp vụ thành công.'''),
   lesson('Tường lửa và phân vùng truy cập',
    'Đề xuất chính sách truy cập tối thiểu trong một mạng lab.',
    '''Tường lửa cho phép hoặc chặn lưu lượng theo chính sách như IP, cổng, giao thức và trạng thái kết nối. Chính sách nên xuất phát từ luồng nghiệp vụ cần thiết thay vì mở mọi cổng để thử. Stateful firewall theo dõi trạng thái để xử lý lưu lượng phản hồi phù hợp.

Phân vùng đặt thiết bị có nhu cầu và mức tin cậy khác nhau vào vùng riêng. Mạng khách thường chỉ cần Internet, không cần truy cập máy chủ quản trị nội bộ. Quyền tối thiểu nghĩa là chỉ cấp truy cập cần cho công việc, rồi kiểm tra cả luồng được phép và luồng phải bị chặn.

Ghi log có ích nhưng phải tránh lưu mật khẩu và token. Thay đổi chính sách cần kế hoạch khôi phục, đặc biệt nếu đang quản trị từ xa. HTTPS bảo vệ đường truyền, tường lửa kiểm soát luồng; hai công cụ không thay thế nhau. Không tiến hành quét hoặc thử vượt quyền trên mạng bên ngoài phạm vi được cho phép.''',
    'Mạng Guest được phép DNS tới resolver chỉ định và web ra Internet; bị chặn truy cập vùng quản trị. Kiểm tra từ thiết bị Guest và thiết bị quản trị để tránh một chính sách nhầm ảnh hưởng cả hai.',
    'Viết bảng nguồn, đích, giao thức/cổng và quyết định cho ba luồng: học viên mở web, khách vào trang quản trị nội bộ, quản trị viên kết nối máy lab. Ghi cách kiểm tra và hoàn nguyên.',
    'Không chỉ kiểm tra có thể truy cập web; cần xác nhận khách bị chặn đúng vùng. Không dùng việc NAT hoạt động để kết luận chính sách đã an toàn.',
    '''Nguyên tắc quyền tối thiểu là gì? | Chỉ cấp truy cập cần thiết cho nhiệm vụ | Mở mọi cổng | Chia sẻ tài khoản quản trị | Bỏ ghi nhận thay đổi | Quyền được giới hạn theo nhu cầu thực tế.
Stateful firewall theo dõi thông tin gì? | Trạng thái kết nối | Chỉ màu giao diện | Điểm bài kiểm tra | Tên tệp PDF | Trạng thái giúp áp dụng chính sách cho lưu lượng liên quan phiên.
Kiểm tra chính sách mạng khách nên bao gồm gì? | Cả truy cập được phép và bị chặn | Chỉ một trang web mở được | Chỉ ảnh chụp desktop | Chỉ kiểm tra tên SSID | Cần xác nhận cho phép và từ chối đều đúng.
Khi sửa firewall từ xa cần chuẩn bị gì? | Kế hoạch khôi phục truy cập | Xóa bản sao cấu hình | Mở mọi cổng vĩnh viễn | Tắt mọi log | Quy tắc sai có thể khóa chính người quản trị.
Thông tin nào không nên ghi vào log? | Mật khẩu và token | Mã sự kiện không bí mật | Thời điểm lỗi | Mã trạng thái HTTP | Bí mật xác thực cần được loại khỏi nhật ký.'''),
  ]),
  ('Chẩn đoán và bài thực hành tổng hợp', [
   lesson('Chẩn đoán lỗi mạng theo từng lớp',
    'Tạo giả thuyết và thu thập bằng chứng thay vì thay đổi cấu hình ngẫu nhiên.',
    '''Chẩn đoán bắt đầu bằng phạm vi: chỉ một máy hay nhiều máy, chỉ một dịch vụ hay toàn bộ kết nối, lỗi liên tục hay theo thời điểm. Ghi thông báo lỗi, thời gian và thay đổi gần nhất trước khi thử sửa.

Kiểm tra lần lượt liên kết, cấu hình địa chỉ và gateway, đường đi IP, phân giải DNS, kết nối cổng và phản hồi ứng dụng. ping dùng ICMP nên thất bại có thể do bị lọc, không đủ để khẳng định host tắt. nslookup giúp khảo sát DNS; curl có thể quan sát phản hồi HTTP. Tên và tùy chọn lệnh phụ thuộc hệ điều hành.

Chỉ đổi một yếu tố mỗi lần, đo lại rồi ghi kết quả. Nếu truy cập IP được nhưng tên miền không phân giải, DNS là giả thuyết hợp lý, chưa phải kết luận cuối cùng cho mọi lỗi trình duyệt. Không xóa dữ liệu hoặc thay đổi hàng loạt chỉ để thử vận may.''',
    'Một máy không vào được website nhưng máy bên cạnh được. So sánh IP/mask/gateway/DNS, kiểm tra resolver và kết nối tới dịch vụ. Ghi rõ bước nào thành công trước khi thay DNS.',
    'Lập checklist cho ba lỗi lab: sai gateway, sai DNS và server HTTP ngừng chạy. Với mỗi lỗi, dự đoán phép thử nào phân biệt được nó với hai lỗi còn lại.',
    'Sai DNS có thể vẫn kết nối được IP; server dừng có thể DNS vẫn trả lời. ping không thay thế kiểm tra cổng và HTTP.',
    '''Bước đầu khi chẩn đoán nên là gì? | Xác định phạm vi và ghi nhận hiện tượng | Đổi tất cả cấu hình | Xóa hệ điều hành | Tắt mọi chính sách | Xác định phạm vi giúp thu hẹp nguyên nhân.
ping thất bại có chắc host đã tắt không? | Không, ICMP có thể bị lọc | Có trong mọi tình huống | Có vì ping dùng HTTP | Có vì DNS luôn đúng | Một phép thử ICMP không đủ kết luận trạng thái mọi dịch vụ.
Công cụ nào phù hợp khảo sát phân giải tên? | nslookup | Trình soạn ảnh | Trình nén tệp | Máy tính số học | nslookup hỏi dịch vụ DNS.
DNS trả lời đúng nhưng web không mở, cần kiểm tra thêm gì? | Kết nối cổng và phản hồi ứng dụng | Chỉ tên miền lần nữa vô hạn | Kết luận chắc chắn không lỗi | Chỉ đổi MAC | DNS chỉ là một bước trong chuỗi truy cập dịch vụ.
Vì sao chỉ thay một yếu tố mỗi lần? | Giúp xác định tác động của thay đổi | Để lỗi không thể tái hiện | Để không cần ghi log | Để chắc chắn mạng không đổi | Thay đổi có kiểm soát giữ khả năng so sánh trước và sau.'''),
   lesson('Dự án nhỏ: thiết kế mạng cho phòng học',
    'Tổng hợp địa chỉ, phân vùng, dịch vụ và kiểm tra nghiệm thu thành một phương án mạng.',
    '''Một thiết kế nhập môn cần danh sách thiết bị, nhóm người dùng, nhu cầu truy cập và sơ đồ logic. Tách yêu cầu khỏi giải pháp: số máy và nhu cầu của khách là yêu cầu; VLAN và dải IP là lựa chọn triển khai. Không cấp địa chỉ trước khi ước lượng số host cần dùng.

Chọn các mạng con không chồng lấn, địa chỉ gateway, vùng DHCP và địa chỉ dành riêng cho hạ tầng. Ghi resolver DNS, đường ra Internet và các luồng bị giới hạn. Đề xuất vị trí AP dựa trên khảo sát, không chỉ số lượng thiết bị.

Bàn giao gồm sơ đồ, bảng địa chỉ, chính sách, kế hoạch kiểm tra và cách khôi phục. Chất lượng được đánh giá bằng bằng chứng: máy học viên có cấu hình đúng, web hoạt động, khách bị cách ly và lỗi có thể được chẩn đoán. Quiz chỉ kiểm tra quyết định thiết kế, không tự chấm sản phẩm thực hành.''',
    'Một phòng có 20 máy học viên và một nhóm khách. Có thể dùng hai mạng /24 riêng trong lab để dễ quản lý, nhưng phải nêu đây là lựa chọn đơn giản hóa chứ không phải phương án tiết kiệm địa chỉ tối ưu.',
    'Nộp sơ đồ hai vùng, bảng IP/gateway/DHCP, ba quy tắc truy cập và năm ca nghiệm thu. Thực hiện bằng mô phỏng hoặc mạng lab được phép; ghi ảnh bằng chứng không chứa bí mật.',
    'Tiêu chí đạt: dải IP không trùng; gateway thuộc mạng host; DHCP không cấp địa chỉ dành riêng; có cả kiểm tra được phép, bị chặn và tình huống DNS lỗi.',
    '''Trước khi chọn mạng con cần biết gì? | Số host và nhu cầu kết nối | Chỉ màu thiết bị | Chỉ tên phòng | Chỉ phiên bản trình duyệt | Yêu cầu dung lượng và luồng truy cập quyết định thiết kế.
Hai mạng con dùng cho hai vùng nên có đặc điểm gì? | Không chồng lấn địa chỉ | Luôn cùng mọi địa chỉ | Không cần gateway | Không thể dùng IPv4 | Dải không chồng lấn giúp định tuyến và quản lý rõ ràng.
DHCP pool cần tránh cấp gì? | Địa chỉ đã dành riêng cho hạ tầng | Mọi địa chỉ host hợp lệ | Địa chỉ chưa dùng bất kỳ | Không cần tránh gì | Tránh xung đột giữa cấp động và địa chỉ dành riêng.
Nghiệm thu cách ly khách cần làm gì? | Thử cả truy cập Internet và truy cập nội bộ bị cấm | Chỉ kiểm tra đèn nguồn | Chỉ đổi SSID | Chỉ in sơ đồ | Cần chứng minh chức năng và ràng buộc đều hoạt động.
Quiz của dự án có tự chứng nhận cấu hình thực tế đúng không? | Không, cần sản phẩm và bằng chứng thực hành | Có, không cần làm lab | Có nếu chọn cùng một đáp án | Có nếu đọc tên bài | Câu hỏi lý thuyết không thay thế kiểm chứng triển khai.'''),
  ]),
 ],
 'cau-truc-du-lieu-giai-thuat-co-ban': [
  ('Phân tích thuật toán và đệ quy', [
   lesson('Big-O, bất biến và kiểm tra thuật toán',
    'Phân tích chi phí theo kích thước đầu vào và nêu điều kiện để thuật toán đúng.',
    '''Kích thước đầu vào n cần được xác định trước khi phân tích. Một vòng lặp thăm n phần tử thường O(n); hai vòng lặp lồng nhau, mỗi vòng n bước, thường O(n²). Hai vòng nối tiếp có chi phí O(n)+O(n), vẫn là O(n). Vòng lặp chia đôi miền mỗi bước thường gợi ý O(log n).

Phân biệt trường hợp tốt nhất, xấu nhất và trung bình. Big-O là chặn trên tiệm cận; hằng số, kiểu dữ liệu và môi trường vẫn ảnh hưởng thời gian chạy thực tế. Bộ nhớ phụ phân tích riêng với bộ nhớ chứa đầu vào.

Bất biến là mệnh đề đúng tại các mốc trong vòng lặp, giúp lập luận đúng đắn. Khi tìm số lớn nhất, sau k bước, biến best phải chứa giá trị lớn nhất trong k phần tử đã xét. Test rỗng, một phần tử, trùng lặp và biên giúp tìm lỗi; một vài test qua chưa chứng minh đúng với mọi đầu vào.''',
    'Duyệt [3,1,5]: khởi tạo best=3, sau phần tử 1 vẫn là 3, sau 5 là 5. Nếu khởi tạo best=0 mà mọi số âm, thuật toán có thể trả kết quả không tồn tại trong mảng.',
    'Phân tích hai vòng nối tiếp và hai vòng lồng nhau. Viết hàm tìm max có quy ước khi đầu vào rỗng; thử [-5,-2,-9], [7], [2,2].',
    'Chi phí lần lượt O(n) và O(n²). Với mảng rỗng phải trả dấu hiệu không có kết quả hoặc báo lỗi đã quy định, không tự trả 0.',
    '''Hai vòng n bước chạy nối tiếp thường có Big-O nào? | O(n) | O(n²) bắt buộc | O(log n) | O(1) | Hệ số 2 được bỏ trong biểu diễn tiệm cận.
Hai vòng n bước lồng nhau thường có chi phí nào? | O(n²) | O(n) luôn luôn | O(1) | O(log n) | Tổng số lần thực hiện phần thân thường là n nhân n.
Bộ nhớ phụ nên được đánh giá thế nào? | Riêng với chi phí thời gian | Luôn bằng thời gian | Không cần quan tâm | Luôn O(1) | Thuật toán có thể nhanh hơn nhưng dùng nhiều bộ nhớ hơn.
Khởi tạo max bằng 0 dễ sai với dữ liệu nào? | Mảng chỉ có số âm | Mảng có số dương lớn | Mảng có số 0 | Mảng đã tăng dần và toàn số dương | 0 không thuộc mảng và lớn hơn mọi phần tử âm.
Bất biến vòng lặp dùng để làm gì? | Hỗ trợ lập luận trạng thái và tính đúng đắn | Đo số giây chính xác | Thay thế hoàn toàn yêu cầu | Chọn giao thức mạng | Bất biến mô tả điều được giữ đúng trong quá trình lặp.'''),
   lesson('Đệ quy và ngăn xếp lời gọi',
    'Xác định trường hợp cơ sở, bước tiến triển và chi phí của lời giải đệ quy.',
    '''Hàm đệ quy gọi lại chính nó để giải bài toán nhỏ hơn. Cần có trường hợp cơ sở và đại lượng giảm tới trường hợp đó. Với giai thừa n không âm: 0! = 1 và n! = n*(n-1)!. Nếu không kiểm tra miền đầu vào, lời gọi với số âm có thể không bao giờ tới cơ sở.

Mỗi lời gọi lưu trạng thái trên ngăn xếp lời gọi. Tính giai thừa theo cách trên có n bước và độ sâu O(n). Đệ quy không tự làm thuật toán nhanh hơn; phiên bản lặp có thể giảm bộ nhớ phụ.

Một bài toán chia thành nhiều nhánh có thể lặp lại tính toán. Fibonacci đệ quy trực tiếp tính nhiều lần cùng giá trị; memoization lưu lời giải bài toán con để tái sử dụng. Phải phân biệt số lời gọi với độ sâu ngăn xếp. Trong thực tế, giới hạn ngăn xếp có thể làm đệ quy sâu thất bại.''',
    'factorial(3) chờ 3*factorial(2), tiếp tục tới factorial(0)=1, rồi trả ngược 1,2,6. Độ sâu tăng theo n dù mỗi lời gọi chỉ làm ít phép toán.',
    'Viết giả mã giai thừa có kiểm tra n>=0. Vẽ cây lời gọi Fibonacci(5) và đánh dấu các giá trị được tính lại; đề xuất cách lưu kết quả.',
    'Có cơ sở, miền đầu vào và bước tiến triển rõ ràng. Memoization tránh tính lại, còn vòng lặp có thể tránh ngăn xếp sâu cho giai thừa.',
    '''Đệ quy kết thúc thường cần gì? | Cơ sở và bước tiến tới cơ sở | Chỉ gọi lại cùng đầu vào | Không kiểm tra đầu vào | Luôn hai hàm khác nhau | Bài toán phải giảm tới tình huống giải trực tiếp.
Giá trị 0! theo định nghĩa thông thường là gì? | 1 | 0 | -1 | Không xác định | 0! = 1 làm cơ sở cho công thức giai thừa.
Ngăn xếp lời gọi lưu gì? | Trạng thái các lời gọi chưa hoàn tất | Chỉ ảnh | Chỉ tên miền | Chỉ dữ liệu đã xóa | Lời gọi con trả về để tiếp tục lời gọi cha.
Memoization giúp gì? | Tái sử dụng kết quả bài toán con | Mã hóa đáp án | Luôn xóa mọi bộ nhớ | Biến mọi thuật toán thành O(1) | Các trạng thái đã giải được lưu lại.
Đệ quy có luôn nhanh hơn lặp không? | Không | Có trong mọi bài toán | Có nếu hàm ngắn | Có nếu không có cơ sở | Thời gian và bộ nhớ phụ thuộc cách phân rã và triển khai.'''),
  ]),
  ('Tra cứu và dữ liệu có thứ tự', [
   lesson('Bảng băm, tập hợp và ánh xạ',
    'Dùng ánh xạ đếm tần suất và giải thích va chạm băm.',
    '''Bảng băm biến khóa thành vị trí tra cứu thông qua hàm băm. Map lưu cặp khóa–giá trị; set lưu các phần tử phân biệt. Khi các khóa khác nhau có cùng vị trí băm, cấu trúc phải xử lý va chạm, chẳng hạn nối chuỗi hoặc địa chỉ mở.

Tra cứu, chèn và xóa thường có thời gian kỳ vọng O(1) trong điều kiện thích hợp; không phải bảo đảm xấu nhất O(1). Số lượng phần tử, số ô và chất lượng hàm băm ảnh hưởng hiệu năng. Khóa dùng trong bảng băm cần có tính băm và so sánh nhất quán theo ngôn ngữ.

Đếm từ bằng map tăng bộ đếm mỗi khi gặp từ. Nếu chuẩn hóa chữ hoa/thường, phải nêu quy tắc trước. Dùng set loại bản sao nhưng không tự tạo thứ tự sắp xếp. Nếu bài toán cần duyệt tăng dần, cần bước sắp xếp hoặc cấu trúc có thứ tự thích hợp.''',
    'Với [a,b,a,c,b,a], lần lượt cập nhật count[x]=count.get(x,0)+1, được a:3,b:2,c:1. Số khóa phân biệt là 3, khác tổng số phần tử 6.',
    'Viết bộ đếm ký tự và bài toán kiểm tra có phần tử trùng. Kiểm thử dữ liệu rỗng, tất cả giống nhau và phân biệt chữ A với a theo quy tắc đã chọn.',
    'Dùng set để phát hiện trùng, map để lưu tần suất. Giải thích thời gian kỳ vọng O(n), bộ nhớ O(k) với k khóa phân biệt.',
    '''Map lưu loại dữ liệu nào? | Cặp khóa–giá trị | Chỉ cạnh đồ thị | Chỉ chỉ số liên tiếp | Chỉ địa chỉ MAC | Map liên kết một khóa với một giá trị.
Set dùng chủ yếu để biểu diễn gì? | Các phần tử phân biệt | Tần suất bắt buộc của mọi phần tử | Thứ tự tăng dần bắt buộc | Một ngăn xếp LIFO | Set biểu diễn tính thuộc tập và tính duy nhất.
Va chạm băm xảy ra khi nào? | Khóa khác nhau ánh xạ tới cùng vị trí | Hai tên biến giống nhau trong tài liệu | Mạng bị chậm | Mảng đã sắp xếp | Cần chiến lược xử lý nhiều khóa chung vị trí.
O(1) của bảng băm thường cần hiểu ra sao? | Hiệu năng kỳ vọng với điều kiện phù hợp | Bảo đảm xấu nhất cho mọi dữ liệu | Luôn không tốn bộ nhớ | Luôn bằng một giây | Phân bố khóa và triển khai ảnh hưởng chi phí.
Với a,b,a,a thì tần suất a là bao nhiêu? | 3 | 1 | 2 | 4 | Map tăng bộ đếm cho mỗi lần xuất hiện của a.'''),
   lesson('Cây nhị phân và cây tìm kiếm nhị phân',
    'Phân biệt cây nhị phân với BST; mô phỏng tìm kiếm và duyệt inorder.',
    '''Cây có các nút và quan hệ cha–con. Cây nhị phân có tối đa hai con tại mỗi nút. BST bổ sung quy tắc thứ tự; trong phiên bản không có khóa trùng, mọi khóa bên trái nhỏ hơn nút và bên phải lớn hơn nút. Có hai con không đủ để kết luận là BST.

Tìm kiếm so sánh mục tiêu với khóa nút hiện tại rồi chọn một nhánh. Chi phí phụ thuộc chiều cao h, thường O(h). Nếu cây cân đối thì h là O(log n); nếu chèn khóa tăng dần vào BST không tự cân bằng, cây có thể lệch và tìm kiếm tới O(n).

Duyệt inorder đi trái, nút, phải; với BST hợp lệ cho dãy tăng dần. Kiểm tra BST phải xét ràng buộc toàn cây con, không chỉ hai nút con trực tiếp. Bài này giới thiệu nguyên lý; thuật toán tự cân bằng như AVL không thuộc yêu cầu thực hành bắt buộc.''',
    'Chèn 4,2,6,1,3 tạo gốc 4, nhánh trái 2 với con 1 và 3, nhánh phải 6. Inorder thu 1,2,3,4,6. Tìm 3 đi qua 4 rồi 2 rồi 3.',
    'Vẽ BST khi chèn 1,2,3,4 và so sánh chiều cao với thứ tự 3,1,4,2. Viết truy vết tìm một khóa không tồn tại.',
    'Cây chèn tăng dần có thể thành chuỗi. Không ghi mọi thao tác BST là O(log n) nếu chưa có điều kiện về chiều cao.',
    '''Cây nhị phân có đặc điểm nào? | Mỗi nút tối đa hai con | Luôn có thứ tự BST | Mọi nút đúng hai con | Luôn cân bằng | Giới hạn số con không tự tạo quy tắc tìm kiếm.
Trong BST không khóa trùng, khóa ở cây con trái so với nút thế nào? | Nhỏ hơn khóa nút | Luôn lớn hơn | Không có ràng buộc | Luôn bằng 0 | Quy tắc thứ tự áp dụng cho toàn cây con.
Inorder của BST hợp lệ cho thứ tự nào? | Tăng dần | Ngẫu nhiên bắt buộc | Giảm dần bắt buộc | Theo thời gian chèn luôn luôn | Inorder là trái–nút–phải.
Tìm kiếm BST có chi phí phụ thuộc gì? | Chiều cao cây | Chỉ tên biến | Chỉ kích thước màn hình | Luôn một phép so sánh | Mỗi bước đi xuống một mức.
Chèn tăng dần vào BST không tự cân bằng có thể gây gì? | Cây lệch và tìm kiếm O(n) | Luôn cây cân bằng hoàn hảo | Không có nút | Tự chuyển thành bảng băm | Trường hợp xấu cây có chiều cao tỉ lệ n.'''),
  ]),
  ('Ưu tiên và đồ thị', [
   lesson('Heap và hàng đợi ưu tiên',
    'Mô phỏng min-heap và phân biệt ưu tiên với FIFO.',
    '''Hàng đợi ưu tiên lấy phần tử theo độ ưu tiên, không nhất thiết theo thứ tự đến. Min-heap nhị phân thường biểu diễn bằng mảng và hình dạng cây nhị phân hoàn chỉnh; mỗi nút cha có khóa không lớn hơn các con. Phần tử nhỏ nhất ở gốc nhưng toàn bộ mảng chưa được sắp xếp.

Với chỉ số bắt đầu từ 0, con trái của i ở 2*i+1, con phải ở 2*i+2. Chèn phần tử vào cuối rồi đưa lên để khôi phục tính heap; lấy min thay gốc bằng phần tử cuối rồi đưa xuống. Chiều cao O(log n) dẫn tới chi phí chèn/lấy min O(log n); xem min O(1).

Heap hữu ích khi liên tục cần công việc ưu tiên hoặc k phần tử nổi bật. Nếu nhiều việc bằng ưu tiên và cần giữ thứ tự đến, bổ sung bộ đếm thứ tự. Không dùng heap để thay thế mọi yêu cầu tìm kiếm theo khóa tùy ý.''',
    'Chèn 5,2,8 vào min-heap, gốc là 2. Lấy min trả 2 rồi heap mới có gốc 5. Thứ tự mảng biểu diễn không phải dãy đã sắp xếp đầy đủ.',
    'Mô phỏng thêm 1 vào heap [2,5,8]. Lập lịch ba công việc có ưu tiên khác nhau và giải thích quy ước khi bằng ưu tiên.',
    'Kết quả lấy lần lượt là 1,2,5,8 nếu không thêm phần tử khác. Nêu rõ số ưu tiên nhỏ hay lớn được phục vụ trước.',
    '''Gốc min-heap chứa gì? | Khóa nhỏ nhất | Khóa lớn nhất bắt buộc | Phần tử chèn đầu luôn luôn | Một khóa ngẫu nhiên | Quy tắc heap đảm bảo min tại gốc.
Mảng biểu diễn heap có luôn sắp xếp tăng dần không? | Không | Có với mọi heap | Chỉ có hai phần tử | Heap không dùng mảng | Quy tắc cha–con yếu hơn thứ tự tuyến tính toàn mảng.
Con trái của chỉ số i trong heap mảng 0-based ở đâu? | 2*i+1 | i-1 | i/2 luôn luôn | 3*i | Công thức xuất phát từ biểu diễn cây theo từng mức.
Chèn vào heap nhị phân thường có chi phí nào? | O(log n) | O(n!) | O(1) trong mọi trường hợp | O(n²) bắt buộc | Phần tử có thể đi qua chiều cao heap.
Priority queue khác queue FIFO ở điểm nào? | Lấy theo ưu tiên thay vì bắt buộc thứ tự đến | Không thể thêm phần tử | Chỉ lưu chuỗi | Không thể có phần tử trùng | Tiêu chí lấy phần tử là độ ưu tiên.'''),
   lesson('Đồ thị, BFS và DFS',
    'Biểu diễn đồ thị và chọn chiến lược duyệt đúng mục tiêu.',
    '''Đồ thị gồm đỉnh và cạnh, có thể có hướng hoặc vô hướng. Danh sách kề lưu các láng giềng của mỗi đỉnh; ma trận kề dùng ô biểu diễn quan hệ từng cặp đỉnh. Với đồ thị thưa, danh sách kề thường tiết kiệm bộ nhớ hơn ma trận O(V²).

BFS dùng queue để duyệt theo lớp. Trong đồ thị không trọng số, BFS tìm số cạnh ít nhất từ đỉnh xuất phát tới các đỉnh đến được. DFS đi sâu theo nhánh, có thể dùng đệ quy hoặc stack. Cả hai cần quản lý đã thăm để tránh lặp với chu trình.

Với danh sách kề và cách triển khai chuẩn, duyệt toàn phần liên quan có chi phí O(V+E). Một lần duyệt từ s không bảo đảm thăm hết đồ thị không liên thông. Để duyệt toàn bộ, có thể bắt đầu lại ở đỉnh chưa thăm. BFS thông thường không tự giải đường đi ngắn nhất theo trọng số tùy ý.''',
    'Đồ thị A-B, A-C, B-D, C-D. BFS từ A phát hiện B,C trước D; đường đi tới D có hai cạnh. Thứ tự giữa B và C phụ thuộc thứ tự danh sách kề.',
    'Viết danh sách kề, vẽ vết queue BFS và stack DFS. Thêm đỉnh E cô lập rồi kiểm tra một lần BFS từ A có thăm E không.',
    'Không thăm E nếu không có đường nối. Đánh dấu phát hiện phù hợp để tránh đưa cùng đỉnh vào queue lặp lại nhiều lần.',
    '''BFS thường dùng cấu trúc nào? | Queue | Min-heap bắt buộc | Chỉ một số nguyên | Cây BST bắt buộc | Queue tạo thứ tự theo lớp.
DFS có thể triển khai bằng gì? | Stack hoặc đệ quy | Chỉ DNS | Chỉ sort | Không cần nhớ trạng thái | Ngăn xếp hỗ trợ quay lại sau nhánh sâu.
BFS tìm đường ít cạnh nhất trong loại đồ thị nào? | Đồ thị không trọng số | Mọi đồ thị trọng số bất kỳ | Chỉ đồ thị đầy đủ | Chỉ cây nhị phân tìm kiếm | Mỗi lớp BFS tương ứng thêm một cạnh.
Vì sao cần tập đã thăm? | Tránh lặp lại do chu trình | Sắp xếp mọi đỉnh | Xóa mọi cạnh | Chọn địa chỉ IP | Quản lý đã thăm giúp duyệt hữu hạn và hiệu quả.
Duyệt bằng danh sách kề thường có chi phí nào? | O(V+E) | O(V!) | O(1) luôn luôn | O(log E) luôn luôn | Xét đỉnh và cạnh một số lần hữu hạn.'''),
  ]),
  ('Thiết kế lời giải và thực hành', [
   lesson('Chia để trị và quy hoạch động nhập môn',
    'Phân biệt chia để trị với lưu trạng thái bài toán con.',
    '''Chia để trị chia bài toán thành các phần nhỏ, giải rồi kết hợp; merge sort là ví dụ. Quy hoạch động thường phù hợp khi có các bài toán con chồng lặp và cấu trúc tối ưu thích hợp. Không phải cứ có đệ quy là cần quy hoạch động.

Một lời giải quy hoạch động cần định nghĩa trạng thái, chuyển trạng thái, trường hợp cơ sở và thứ tự tính. Với số cách bước lên n bậc, mỗi bước 1 hoặc 2 bậc, có thể đặt ways[0]=1, ways[1]=1 và ways[n]=ways[n-1]+ways[n-2]. Bộ nhớ có thể giảm nếu chỉ cần hai trạng thái trước.

Tham lam chọn quyết định cục bộ, nhưng cần chứng minh cho bài toán cụ thể. Chẳng hạn đổi tiền với mệnh giá tùy ý không bảo đảm thuật toán luôn lấy đồng lớn nhất sẽ dùng ít đồng nhất. Bắt đầu từ mô hình bài toán và ví dụ phản chứng, không chọn kỹ thuật theo tên gọi hấp dẫn.''',
    'Bốn bậc có ways[2]=2, ways[3]=3, ways[4]=5. Đổi 6 với mệnh giá 1,3,4: tham lam 4+1+1 dùng ba đồng nhưng 3+3 dùng hai.',
    'Lập bảng ways từ 0 tới 6 và viết phiên bản dùng hai biến. Tự kiểm tra giả định mỗi bước chỉ là 1 hoặc 2, không áp công thức cho yêu cầu khác.',
    'ways[5]=8, ways[6]=13. Nêu rõ trạng thái 0 biểu diễn một cách không thực hiện bước nào, giúp công thức nhất quán.',
    '''Thành phần nào cần định nghĩa trong quy hoạch động? | Trạng thái và công thức chuyển | Chỉ tên hàm | Chỉ màu lưu đồ | Chỉ số luồng CPU | Trạng thái, cơ sở và thứ tự tính quyết định lời giải.
Merge sort minh họa kỹ thuật nào? | Chia để trị | Chỉ tham lam | Chỉ tìm kiếm tuyến tính | Chỉ bảng băm | Thuật toán chia, giải các nửa và trộn.
Với ways[0]=1, ways[1]=1 và bước 1 hoặc 2, ways[4] là gì? | 5 | 4 | 6 | 8 | Dãy tiếp theo là 2,3,5.
Tham lam lấy đồng lớn nhất có tối ưu cho mọi hệ mệnh giá không? | Không | Có vô điều kiện | Có vì luôn ít vòng lặp | Có nếu dùng đệ quy | Hệ 1,3,4 với số tiền 6 là một phản ví dụ.
Nếu chỉ cần hai trạng thái trước, có thể tối ưu gì? | Bộ nhớ lưu bảng | Thay đổi bài toán | Xóa điều kiện cơ sở | Bỏ mọi kiểm tra | Có thể lưu hai giá trị thay cho toàn bảng.'''),
   lesson('Dự án nhỏ: bộ tra cứu và thống kê dữ liệu',
    'Kết hợp lựa chọn cấu trúc, kiểm thử và phân tích chi phí trong một chương trình nhỏ.',
    '''Thiết kế một bộ tra cứu tên và tần suất xuất hiện. Yêu cầu gồm thêm dữ liệu, đếm, tìm và xuất báo cáo theo thứ tự. Tách quy tắc chuẩn hóa khỏi cấu trúc lưu: chẳng hạn có gộp chữ hoa/thường hay không phải được quyết định trước.

Map phù hợp cập nhật tần suất, set phù hợp kiểm tra duy nhất, danh sách sắp xếp phù hợp xuất thứ tự và tìm nhị phân trên bản dữ liệu đã sắp. Không tự dùng tìm nhị phân sau khi thêm dữ liệu mà không duy trì thứ tự. Nếu chỉ cần top k liên tục, cân nhắc heap và giải thích chi phí.

Sản phẩm cần tài liệu đầu vào/đầu ra, test và nhận xét Big-O cho từng chức năng. Tách dữ liệu rỗng, trùng lặp, Unicode và quy mô lớn. Benchmark phải cùng môi trường và cùng dữ liệu; không suy ra thuật toán đúng chỉ vì chạy nhanh.''',
    'Đầu vào An,Bình,An cho báo cáo An:2,Bình:1. Nếu không gộp hoa/thường, an và An là hai khóa khác nhau; nếu gộp phải nêu cách chuẩn hóa.',
    'Viết chương trình nhận một danh sách từ; xuất số từ phân biệt, tần suất và danh sách theo tên. Nộp ít nhất sáu test và phân tích thời gian cập nhật, sắp xếp, tra cứu.',
    'Kết quả đếm phải khớp tổng số phần tử. Với k khóa, xuất báo cáo sắp xếp thường O(k log k). Giữ lại test hồi quy khi sửa xử lý Unicode.',
    '''Cấu trúc nào phù hợp đếm tần suất theo khóa? | Map | Chỉ một biến tổng | Chỉ queue không tra cứu | Chỉ cây rỗng | Map liên kết mỗi khóa với bộ đếm.
Sau khi thêm phần tử làm mất thứ tự, trước tìm nhị phân cần gì? | Khôi phục hoặc duy trì thứ tự | Không cần gì | Xóa mọi test | Chỉ đổi tên biến | Tìm nhị phân yêu cầu thứ tự phù hợp.
Tổng các tần suất phải bằng gì? | Tổng số phần tử đầu vào đã tính | Số khóa luôn luôn | Số ký tự tên tệp | Số lần gọi sort | Mỗi phần tử đầu vào đóng góp một lần vào một bộ đếm.
Báo cáo sắp xếp k khóa thường cần bao nhiêu thời gian với thuật toán O(k log k)? | O(k log k) | O(1) | O(log k) tổng cộng | O(k!) bắt buộc | Chi phí sắp xếp áp dụng cho số khóa phân biệt k.
Benchmark nhanh có tự chứng minh chương trình đúng không? | Không | Có với mọi test | Có nếu dưới một giây | Có nếu không in log | Đúng đắn cần đối chiếu kết quả và yêu cầu.'''),
  ]),
 ],
}
