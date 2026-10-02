=== LESSON 85 ===
## Mục tiêu bài học
- Nhận biết mệnh đề và xác định giá trị chân lý của mệnh đề
- Thực hiện các phép toán logic: phủ định, hội, tuyển, kéo theo, tương đương
- Lập bảng chân trị và nhận biết hai mệnh đề tương đương logic

## 1. Mệnh đề
Mệnh đề là một câu khẳng định có giá trị chân lý xác định: đúng (T) hoặc sai (F), không thể vừa đúng vừa sai. Ví dụ "2 + 3 = 5" là mệnh đề đúng, "7 là số chẵn" là mệnh đề sai. Câu hỏi "Mấy giờ rồi?" hay câu chứa biến "x > 3" (khi chưa biết x) không phải mệnh đề.

## 2. Các phép toán logic
Cho hai mệnh đề p và q:
- Phủ định ¬p: đúng khi p sai, sai khi p đúng.
- Hội p ∧ q ("p và q"): chỉ đúng khi cả p và q cùng đúng.
- Tuyển p ∨ q ("p hoặc q"): chỉ sai khi cả p và q cùng sai.
- Kéo theo p → q ("nếu p thì q"): chỉ sai khi p đúng và q sai; khi p sai thì p → q luôn đúng.
- Tương đương p ↔ q ("p khi và chỉ khi q"): đúng khi p và q có cùng giá trị chân lý.

Trong lập trình, các phép này tương ứng với toán tử `!`, `&&`, `||` trong điều kiện `if`.

## 3. Bảng chân trị và tương đương logic
Bảng chân trị liệt kê giá trị của biểu thức với mọi tổ hợp giá trị của các biến; n biến có 2^n dòng. Hai biểu thức tương đương logic (ký hiệu ≡) khi có cùng giá trị ở mọi dòng của bảng chân trị.

Các tương đương quan trọng:
- p → q ≡ ¬p ∨ q
- Luật De Morgan: ¬(p ∧ q) ≡ ¬p ∨ ¬q và ¬(p ∨ q) ≡ ¬p ∧ ¬q
- Phản đảo: p → q ≡ ¬q → ¬p

Ví dụ áp dụng De Morgan khi viết code: điều kiện `!(a > 0 && b > 0)` tương đương `a <= 0 || b <= 0`.

## Tóm tắt
- Mệnh đề là câu khẳng định có giá trị đúng hoặc sai xác định.
- p → q chỉ sai khi p đúng và q sai.
- Luật De Morgan: phủ định của hội là tuyển các phủ định và ngược lại.

## Bài tập vận dụng
1. Lập bảng chân trị của (p → q) ∧ (q → p) và so sánh với p ↔ q.
2. Dùng luật De Morgan viết lại điều kiện `!(x < 0 || x > 100)`.

=== LESSON 86 ===
## Mục tiêu bài học
- Hiểu vị từ và hai lượng từ với mọi (∀), tồn tại (∃)
- Phủ định đúng các mệnh đề có lượng từ
- Áp dụng phương pháp chứng minh trực tiếp, phản chứng và phản ví dụ

## 1. Vị từ và lượng từ
Vị từ là câu chứa biến, trở thành mệnh đề khi thay biến bằng giá trị cụ thể. Ví dụ P(x): "x > 3" thì P(5) đúng, P(1) sai.

Lượng từ biến vị từ thành mệnh đề:
- ∀x P(x) ("với mọi x, P(x)"): đúng khi P(x) đúng với mọi x trong miền xét.
- ∃x P(x) ("tồn tại x, P(x)"): đúng khi có ít nhất một x làm P(x) đúng.

Ví dụ trên tập số nguyên: ∀x (x² ≥ 0) là đúng; ∃x (x² = 2) là sai vì không có số nguyên nào bình phương bằng 2.

## 2. Phủ định mệnh đề có lượng từ
Khi phủ định, đổi lượng từ và phủ định vị từ:
- ¬∀x P(x) ≡ ∃x ¬P(x)
- ¬∃x P(x) ≡ ∀x ¬P(x)

Ví dụ: phủ định của "Mọi sinh viên đều qua môn" là "Tồn tại sinh viên không qua môn", không phải "Mọi sinh viên đều trượt".

## 3. Các phương pháp chứng minh
- Chứng minh trực tiếp: giả sử p đúng, suy luận từng bước đến q. Ví dụ: nếu n lẻ thì n² lẻ, vì n = 2k + 1 nên n² = 4k² + 4k + 1 = 2(2k² + 2k) + 1 là số lẻ.
- Chứng minh phản chứng: giả sử điều cần chứng minh sai, suy ra mâu thuẫn. Ví dụ kinh điển: √2 là số vô tỉ.
- Phản ví dụ: để bác bỏ mệnh đề ∀x P(x), chỉ cần chỉ ra MỘT giá trị x làm P(x) sai. Ví dụ "mọi số nguyên tố đều lẻ" sai vì 2 là số nguyên tố chẵn.

## Tóm tắt
- ∀ cần đúng với mọi phần tử; ∃ chỉ cần một phần tử.
- Phủ định: đổi ∀ thành ∃ (và ngược lại), rồi phủ định vị từ.
- Một phản ví dụ đủ để bác bỏ mệnh đề "với mọi".

## Bài tập vận dụng
1. Viết phủ định của: "Tồn tại số thực x sao cho x² < 0".
2. Chứng minh trực tiếp: tổng của hai số chẵn là số chẵn.

=== LESSON 87 ===
## Mục tiêu bài học
- Biểu diễn tập hợp và xác định quan hệ tập con
- Thực hiện các phép hợp, giao, hiệu, phần bù và tích Descartes
- Tính số phần tử của tập lũy thừa

## 1. Tập hợp và tập con
Tập hợp là một bộ sưu tập các phần tử phân biệt, không quan tâm thứ tự. Ký hiệu x ∈ A nghĩa là x thuộc A. Có thể liệt kê A = {1, 2, 3} hoặc nêu tính chất A = {x ∈ ℕ | x < 4}. Tập rỗng ký hiệu ∅.

A là tập con của B (A ⊆ B) khi mọi phần tử của A đều thuộc B. Tập rỗng là tập con của mọi tập, và mọi tập là tập con của chính nó.

## 2. Các phép toán tập hợp
Với A = {1, 2, 3} và B = {2, 3, 4}:
- Hợp A ∪ B = {1, 2, 3, 4}: phần tử thuộc A hoặc B.
- Giao A ∩ B = {2, 3}: phần tử thuộc cả A và B.
- Hiệu A \ B = {1}: phần tử thuộc A nhưng không thuộc B.
- Phần bù của A trong tập vũ trụ U: các phần tử của U không thuộc A.

Luật De Morgan cho tập hợp tương tự logic: phần bù của (A ∪ B) bằng giao các phần bù, phần bù của (A ∩ B) bằng hợp các phần bù.

## 3. Tập lũy thừa và tích Descartes
Tập lũy thừa P(A) là tập tất cả các tập con của A. Nếu A có n phần tử thì P(A) có 2^n phần tử, vì mỗi phần tử có 2 lựa chọn: có mặt hoặc không có mặt trong tập con. Ví dụ A = {a, b} thì P(A) = {∅, {a}, {b}, {a, b}}.

Tích Descartes A × B là tập các cặp có thứ tự (a, b) với a ∈ A, b ∈ B; số phần tử |A × B| = |A| · |B|. Trong cơ sở dữ liệu, phép CROSS JOIN hai bảng chính là tích Descartes.

## Tóm tắt
- A ⊆ B khi mọi phần tử của A đều thuộc B; ∅ là tập con của mọi tập.
- ∪ là "hoặc", ∩ là "và", A \ B là "thuộc A nhưng không thuộc B".
- |P(A)| = 2^n; |A × B| = |A| · |B|.

## Bài tập vận dụng
1. Cho U = {1, …, 10}, A = các số chẵn, B = các số chia hết cho 3. Tìm A ∩ B, A ∪ B, A \ B.
2. Liệt kê mọi tập con của {1, 2, 3} và kiểm tra số lượng bằng 2^3.

=== LESSON 88 ===
## Mục tiêu bài học
- Phân biệt và áp dụng quy tắc cộng, quy tắc nhân
- Giải bài toán đếm nhiều bước bằng quy tắc nhân
- Áp dụng nguyên lý bù trừ cho hai tập hợp

## 1. Quy tắc cộng
Nếu một công việc có thể làm theo phương án 1 với m cách HOẶC phương án 2 với n cách, và hai phương án không trùng nhau, thì có m + n cách làm. Ví dụ: chọn 1 cuốn sách từ 5 sách Toán hoặc 7 sách Tin có 5 + 7 = 12 cách.

## 2. Quy tắc nhân
Nếu một công việc gồm hai bước liên tiếp, bước 1 có m cách và VỚI MỖI cách đó bước 2 có n cách, thì có m · n cách. Mở rộng cho k bước: nhân số cách của từng bước.

Ví dụ: mật khẩu gồm 2 chữ cái (26 chữ) rồi 3 chữ số, cho phép lặp, có 26 · 26 · 10 · 10 · 10 = 676 000 khả năng. Một chuỗi bit dài n có 2^n giá trị, nên kiểu dữ liệu 8 bit biểu diễn được 2^8 = 256 giá trị.

Ví dụ trong code: hai vòng lặp lồng nhau, vòng ngoài chạy m lần và vòng trong chạy n lần, thì lệnh bên trong chạy m · n lần.

## 3. Nguyên lý bù trừ
Khi hai tập có phần chung, phép cộng đơn thuần sẽ đếm phần chung hai lần, nên phải trừ đi: |A ∪ B| = |A| + |B| − |A ∩ B|.

Ví dụ: trong lớp có 25 sinh viên học Python, 20 học Java, 8 học cả hai. Số sinh viên học ít nhất một môn là 25 + 20 − 8 = 37.

## Tóm tắt
- Quy tắc cộng: các phương án loại trừ nhau ("hoặc").
- Quy tắc nhân: các bước nối tiếp nhau ("và").
- Bù trừ: |A ∪ B| = |A| + |B| − |A ∩ B|.

## Bài tập vận dụng
1. Có bao nhiêu số tự nhiên có 3 chữ số khác nhau được lập từ các chữ số 1 đến 5?
2. Từ 1 đến 100 có bao nhiêu số chia hết cho 2 hoặc cho 5?

=== LESSON 89 ===
## Mục tiêu bài học
- Tính số hoán vị của n phần tử
- Phân biệt chỉnh hợp (có thứ tự) và tổ hợp (không thứ tự)
- Chọn đúng công thức cho bài toán đếm thực tế

## 1. Hoán vị
Hoán vị của n phần tử là một cách sắp xếp cả n phần tử theo thứ tự. Số hoán vị là P(n) = n! = n · (n − 1) · … · 2 · 1, quy ước 0! = 1. Ví dụ: xếp 4 người vào 4 ghế thẳng hàng có 4! = 24 cách.

## 2. Chỉnh hợp
Chỉnh hợp chập k của n là cách chọn k phần tử từ n phần tử VÀ sắp thứ tự chúng. Công thức A(n, k) = n! / (n − k)! = n · (n − 1) · … · (n − k + 1).

Ví dụ: chọn lớp trưởng, lớp phó, thủ quỹ từ 5 bạn (mỗi vị trí khác nhau, thứ tự có ý nghĩa) có A(5, 3) = 5 · 4 · 3 = 60 cách.

## 3. Tổ hợp
Tổ hợp chập k của n là cách chọn k phần tử từ n phần tử KHÔNG quan tâm thứ tự. Công thức C(n, k) = n! / (k! · (n − k)!). Tính chất: C(n, k) = C(n, n − k) và C(n, 0) = C(n, n) = 1.

Ví dụ: chọn 2 bạn trong 5 bạn đi trực nhật (không phân biệt vai trò) có C(5, 2) = 10 cách. Liên hệ: A(n, k) = C(n, k) · k!, vì mỗi nhóm k phần tử có k! cách sắp thứ tự.

Cách nhận biết: đổi chỗ hai phần tử đã chọn mà ra kết quả khác thì dùng chỉnh hợp; ra kết quả giống nhau thì dùng tổ hợp.

## Tóm tắt
- Hoán vị: sắp xếp toàn bộ n phần tử, n! cách.
- Chỉnh hợp A(n, k): chọn k phần tử có thứ tự.
- Tổ hợp C(n, k): chọn k phần tử không thứ tự; A(n, k) = C(n, k) · k!.

## Bài tập vận dụng
1. Có bao nhiêu cách chọn đội 4 người từ 10 người? Nếu cần thêm 1 đội trưởng trong 4 người đó thì có bao nhiêu cách?
2. Tính C(6, 2), A(6, 2) và kiểm tra hệ thức A = C · k!.

=== LESSON 90 ===
## Mục tiêu bài học
- Chứng minh mệnh đề bằng phương pháp quy nạp toán học
- Thiết lập và tính các số hạng của hệ thức truy hồi
- Liên hệ hệ thức truy hồi với hàm đệ quy trong lập trình

## 1. Quy nạp toán học
Để chứng minh P(n) đúng với mọi số tự nhiên n ≥ n₀, thực hiện hai bước:
1. Bước cơ sở: chứng minh P(n₀) đúng.
2. Bước quy nạp: giả sử P(k) đúng (giả thiết quy nạp), chứng minh P(k + 1) đúng.

Ví dụ: chứng minh 1 + 2 + … + n = n(n + 1)/2. Cơ sở: n = 1 thì vế trái bằng 1, vế phải bằng 1·2/2 = 1. Quy nạp: giả sử đúng với k, khi đó 1 + … + k + (k + 1) = k(k + 1)/2 + (k + 1) = (k + 1)(k + 2)/2, đúng với k + 1.

## 2. Hệ thức truy hồi
Hệ thức truy hồi định nghĩa số hạng của dãy qua các số hạng trước nó, kèm điều kiện ban đầu.
- Dãy Fibonacci: F(0) = 0, F(1) = 1, F(n) = F(n − 1) + F(n − 2). Các số hạng: 0, 1, 1, 2, 3, 5, 8, 13, …
- Dãy a(n) = 2·a(n − 1) + 1 với a(0) = 1 cho 1, 3, 7, 15, 31, …; công thức tường minh a(n) = 2^(n+1) − 1, có thể kiểm chứng bằng quy nạp.

Bài toán tháp Hà Nội: số bước chuyển n đĩa thỏa H(n) = 2·H(n − 1) + 1, H(1) = 1, nên H(n) = 2^n − 1.

## 3. Liên hệ với hàm đệ quy
Hệ thức truy hồi chuyển trực tiếp thành hàm đệ quy: điều kiện ban đầu là điểm dừng, công thức truy hồi là lời gọi đệ quy.

```python
def fib(n):
    if n < 2:          # điều kiện ban đầu = điểm dừng
        return n
    return fib(n - 1) + fib(n - 2)
```

Cài đặt trên tính lại nhiều lần cùng một giá trị nên rất chậm khi n lớn; có thể lưu kết quả đã tính (memoization) hoặc tính lặp từ dưới lên.

## Tóm tắt
- Quy nạp gồm bước cơ sở và bước quy nạp P(k) ⇒ P(k + 1).
- Hệ thức truy hồi = công thức theo số hạng trước + điều kiện ban đầu.
- Điều kiện ban đầu tương ứng điểm dừng của hàm đệ quy.

## Bài tập vận dụng
1. Chứng minh bằng quy nạp: 2^n > n với mọi n ≥ 1.
2. Tính 10 số hạng đầu của Fibonacci và viết hàm tính F(n) bằng vòng lặp.

=== LESSON 91 ===
## Mục tiêu bài học
- Nắm các khái niệm đỉnh, cạnh, bậc, đồ thị có hướng và vô hướng
- Áp dụng định lý bắt tay để tính số cạnh từ bậc các đỉnh
- Biểu diễn đồ thị bằng ma trận kề và danh sách kề

## 1. Khái niệm đồ thị
Đồ thị G = (V, E) gồm tập đỉnh V và tập cạnh E, mỗi cạnh nối hai đỉnh. Đồ thị vô hướng có cạnh không chiều (mạng bạn bè), đồ thị có hướng có cạnh mang chiều (theo dõi trên mạng xã hội, liên kết trang web). Đồ thị có trọng số gắn mỗi cạnh một giá trị như khoảng cách, chi phí.

Bậc của đỉnh v, ký hiệu deg(v), là số cạnh liên thuộc với v (khuyên được tính 2 lần).

## 2. Định lý bắt tay
Trong đồ thị vô hướng, tổng bậc của tất cả các đỉnh bằng hai lần số cạnh: Σ deg(v) = 2|E|, vì mỗi cạnh góp 1 bậc cho mỗi đầu mút. Hệ quả: số đỉnh bậc lẻ luôn là số chẵn.

Ví dụ: đồ thị 5 đỉnh có bậc 3, 3, 2, 2, 2 thì tổng bậc 12 nên có 6 cạnh. Không tồn tại đồ thị có bậc 3, 3, 3, 2, 2 vì có 3 đỉnh bậc lẻ.

## 3. Biểu diễn đồ thị
- Ma trận kề: ma trận n × n, ô (i, j) bằng 1 nếu có cạnh từ i đến j (hoặc bằng trọng số). Kiểm tra cạnh nhanh O(1) nhưng tốn bộ nhớ O(n²).
- Danh sách kề: mỗi đỉnh lưu danh sách các đỉnh kề. Tốn bộ nhớ O(|V| + |E|), phù hợp đồ thị thưa.

```python
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C"],
}
```

## Tóm tắt
- Đồ thị gồm đỉnh và cạnh; có hướng / vô hướng; có / không trọng số.
- Định lý bắt tay: tổng bậc = 2 × số cạnh; số đỉnh bậc lẻ là số chẵn.
- Ma trận kề cho đồ thị dày, danh sách kề cho đồ thị thưa.

## Bài tập vận dụng
1. Một đồ thị có 10 đỉnh, mỗi đỉnh bậc 4. Đồ thị có bao nhiêu cạnh?
2. Vẽ đồ thị từ danh sách kề ở trên và viết ma trận kề tương ứng.

=== LESSON 92 ===
## Mục tiêu bài học
- Duyệt đồ thị theo chiều rộng (BFS) và chiều sâu (DFS)
- Dùng BFS tìm đường đi ít cạnh nhất trên đồ thị không trọng số
- Tìm đường đi ngắn nhất trên đồ thị có trọng số không âm bằng Dijkstra

## 1. Duyệt theo chiều rộng (BFS)
BFS bắt đầu từ một đỉnh, thăm hết các đỉnh kề trước rồi mới đi xa hơn, dùng hàng đợi (queue). Các đỉnh được thăm theo thứ tự khoảng cách (số cạnh) tăng dần, nên BFS tìm được đường đi ít cạnh nhất trên đồ thị không trọng số.

```python
from collections import deque

def bfs(graph, start):
    visited, queue = {start}, deque([start])
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return visited
```

## 2. Duyệt theo chiều sâu (DFS)
DFS đi sâu theo một nhánh đến khi không đi tiếp được rồi quay lui, dùng ngăn xếp (stack) hoặc đệ quy. DFS dùng để kiểm tra liên thông, phát hiện chu trình, sắp xếp tô pô. Cả BFS và DFS có độ phức tạp O(|V| + |E|) với danh sách kề.

## 3. Thuật toán Dijkstra
Dijkstra tìm đường đi ngắn nhất từ một đỉnh nguồn đến mọi đỉnh trên đồ thị có trọng số KHÔNG ÂM. Ý tưởng: luôn chọn đỉnh chưa xét có khoảng cách tạm thời nhỏ nhất, chốt khoảng cách của nó, rồi cập nhật (nới lỏng) các đỉnh kề: nếu d[u] + w(u, v) < d[v] thì gán d[v] = d[u] + w(u, v).

Dùng hàng đợi ưu tiên (heap), độ phức tạp khoảng O((|V| + |E|) log |V|). Khi đồ thị có cạnh trọng số âm, Dijkstra có thể cho kết quả sai vì một đỉnh đã chốt vẫn có thể được rút ngắn sau đó; trường hợp này dùng thuật toán Bellman–Ford.

## Tóm tắt
- BFS dùng hàng đợi, tìm đường ít cạnh nhất; DFS dùng ngăn xếp / đệ quy.
- Dijkstra: chọn đỉnh có khoảng cách nhỏ nhất, nới lỏng các cạnh kề.
- Dijkstra chỉ đúng với trọng số không âm; có cạnh âm dùng Bellman–Ford.

## Bài tập vận dụng
1. Ghi thứ tự thăm đỉnh khi chạy BFS và DFS từ đỉnh A trên đồ thị bài trước.
2. Chạy tay Dijkstra trên đồ thị 4 đỉnh: A–B (1), A–C (4), B–C (2), C–D (1). Tìm khoảng cách từ A đến D.

=== LESSON 93 ===
## Mục tiêu bài học
- Nắm định nghĩa và các tính chất cơ bản của cây
- Hiểu khái niệm cây khung của đồ thị liên thông
- Tìm cây khung nhỏ nhất bằng thuật toán Kruskal và Prim

## 1. Cây và tính chất
Cây là đồ thị vô hướng liên thông và không có chu trình. Với cây có n đỉnh:
- Có đúng n − 1 cạnh.
- Giữa hai đỉnh bất kỳ có duy nhất một đường đi.
- Bỏ đi một cạnh bất kỳ thì cây mất liên thông; thêm một cạnh bất kỳ thì tạo ra đúng một chu trình.

Cây có gốc dùng nhiều trong lập trình: cây thư mục, cây DOM của trang web, cây nhị phân tìm kiếm.

## 2. Cây khung
Cây khung của đồ thị liên thông G là một cây con chứa TẤT CẢ các đỉnh của G. Một đồ thị có thể có nhiều cây khung; BFS hoặc DFS từ một đỉnh sẽ tạo ra một cây khung. Trên đồ thị có trọng số, cây khung nhỏ nhất (MST) là cây khung có tổng trọng số các cạnh nhỏ nhất, ứng dụng khi thiết kế mạng cáp, đường ống với chi phí thấp nhất.

## 3. Thuật toán Kruskal và Prim
- Kruskal: sắp xếp các cạnh theo trọng số tăng dần, lần lượt thêm cạnh vào cây nếu cạnh đó KHÔNG tạo chu trình với các cạnh đã chọn; dừng khi có n − 1 cạnh. Kiểm tra chu trình hiệu quả bằng cấu trúc Union–Find.
- Prim: bắt đầu từ một đỉnh, mỗi bước thêm cạnh có trọng số nhỏ nhất nối một đỉnh đã có trong cây với một đỉnh chưa có trong cây.

Cả hai thuật toán đều là thuật toán tham lam và cho kết quả là cây khung nhỏ nhất. Kruskal thuận tiện cho đồ thị thưa, Prim với heap thuận tiện cho đồ thị dày.

## Tóm tắt
- Cây: liên thông, không chu trình, n đỉnh có n − 1 cạnh.
- Cây khung chứa mọi đỉnh của đồ thị; MST có tổng trọng số nhỏ nhất.
- Kruskal chọn cạnh nhỏ nhất không tạo chu trình; Prim mở rộng cây từ một đỉnh.

## Bài tập vận dụng
1. Một rừng (đồ thị không chu trình) có 12 đỉnh và 3 thành phần liên thông. Rừng có bao nhiêu cạnh?
2. Chạy tay Kruskal trên đồ thị: A–B (4), A–C (1), B–C (2), B–D (5), C–D (8). Tổng trọng số MST bằng bao nhiêu?
