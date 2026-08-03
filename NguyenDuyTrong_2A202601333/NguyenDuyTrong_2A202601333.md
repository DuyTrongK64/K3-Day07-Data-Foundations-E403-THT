# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [BỔ SUNG HỌ TÊN TRƯỚC KHI NỘP]

**Nhóm:** [BỔ SUNG TÊN NHÓM]

**Ngày:** 03/08/2026

## 1. Khởi động (Warm-up) — 5 điểm

### 1.1. Độ tương tự cosine

Độ tương tự cosine cao nghĩa là hai vector embedding hướng gần giống nhau, do đó hai đoạn văn bản thường có nội dung hoặc ý định ngữ nghĩa gần nhau. Chỉ số gần 1 biểu thị rất tương đồng, gần 0 biểu thị ít liên quan, còn giá trị âm biểu thị hướng đối lập trong không gian vector.

**Ví dụ tương tự cao**

- Câu A: “Sinh viên được mượn tối đa 25 cuốn sách trong một tháng.”
- Câu B: “Hạn mức thư viện cho người học là 25 đầu sách trong 30 ngày.”
- Hai câu dùng từ khác nhau nhưng truyền đạt cùng đối tượng, hạn mức và thời gian.

**Ví dụ tương tự thấp**

- Câu A: “Ứng viên học bổng cần GPA tích lũy tối thiểu 3,4.”
- Câu B: “Thư viện cung cấp dịch vụ in và photocopy.”
- Hai câu thuộc hai dịch vụ khác nhau và không chia sẻ cùng ý định hỏi đáp.

Cosine similarity thường phù hợp hơn khoảng cách Euclid vì nó so sánh **hướng** của vector thay vì độ lớn tuyệt đối. Nhờ vậy, phép đo ít nhạy với độ dài hoặc cường độ vector và tập trung hơn vào phân bố đặc trưng ngữ nghĩa.

### 1.2. Bài toán chunking

Với `document_length=10.000`, `chunk_size=500`, `overlap=50`:

\[
N=\left\lceil\frac{10000-50}{500-50}\right\rceil
=\left\lceil\frac{9950}{450}\right\rceil
=\lceil22{,}111\ldots\rceil=23\text{ chunks}
\]

Khi tăng overlap lên 100:

\[
N=\left\lceil\frac{10000-100}{500-100}\right\rceil
=\left\lceil\frac{9900}{400}\right\rceil
=\lceil24{,}75\rceil=25\text{ chunks}
\]

Số chunk tăng từ 23 lên 25 vì bước trượt giảm từ 450 xuống 400 ký tự. Overlap lớn hơn có thể giữ ngữ cảnh nằm sát ranh giới chunk, nhưng làm tăng lưu trữ, thời gian embedding và nguy cơ trả về nội dung trùng lặp.

## 2. Hướng tiếp cận của tôi (My Approach) — 10 điểm

### Chunking

`SentenceChunker` dùng regex `(?<=[.!?])(?:[ \t]+|\r?\n+)` để tìm ranh giới sau dấu `.`, `!`, `?`, giữ dấu câu trong câu gốc rồi nhóm tối đa `max_sentences_per_chunk`. Chuỗi rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng; tham số số câu được chặn tối thiểu là 1.

`RecursiveChunker` thử lần lượt `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là tách cứng theo ký tự. Mỗi phần vừa giới hạn được gộp vào buffer; phần quá lớn được đệ quy với separator kế tiếp. Base case là đoạn đã ngắn hơn `chunk_size`; nếu hết separator, thuật toán cắt cố định để đảm bảo kết thúc.

Ngoài ba chiến lược bắt buộc, `HeadingSectionChunker` tách Markdown theo tiêu đề và giữ tiêu đề đi cùng nội dung. Section quá dài được chuyển cho `RecursiveChunker`, phù hợp với quy định đại học có cấu trúc mục rõ ràng.

### EmbeddingStore

`add_documents` tạo một record chuẩn hóa gồm ID nội bộ duy nhất, nội dung, bản sao metadata và vector embedding. Store luôn giữ mirror trong bộ nhớ để hành vi dot-product có tính xác định; nếu ChromaDB có sẵn, dữ liệu đồng thời được ghi vào collection cosine tạm thời.

`search` embedding câu hỏi một lần, tính dot product với từng record, sắp xếp giảm dần và lấy `top_k`. `search_with_filter` lọc metadata **trước** khi xếp hạng để tránh tài liệu sai đối tượng. `delete_document` tìm mọi chunk có cùng `metadata.doc_id`, xóa khỏi bộ nhớ và đồng bộ lệnh xóa sang Chroma nếu backend này hoạt động.

### KnowledgeBaseAgent

`answer` truy xuất top-k chunk, đánh số nguồn và đưa `source_url` cùng nội dung vào prompt. Prompt yêu cầu LLM chỉ dùng ngữ cảnh, nói rõ khi thiếu dữ liệu, không suy đoán và dẫn `[1]`, `[2]` khi có thể. Cách này làm căn cứ trả lời có thể truy vết.

## 3. Hoàn thiện code (Core Implementation) — 30 điểm

Lệnh chạy:

```bash
.venv/bin/python -m pytest tests/ -v
```

Kết quả tóm tắt:

```text
collected 42 items
tests/test_solution.py .......................................... [100%]
============================== 42 passed in 0.04s ==============================
```

**Số test vượt qua: 42/42.** Môi trường hiện tại chỉ cung cấp Python 3.14.5; mã nguồn chỉ dùng cú pháp từ Python 3.11 trở xuống và cần được chạy lại bằng Python 3.11 trong môi trường chấm chính thức như README quy định.

## 4. Dự đoán độ tương tự — 5 điểm

Các dự đoán được ghi trong `scripts/run_benchmark.py` trước khi gọi model. Điểm thực tế dùng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, không dùng mock.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---:|---|---|---|---:|:---:|
| 1 | Sinh viên được mượn tối đa 25 cuốn sách trong một tháng. | Hạn mức thư viện cho người học là 25 đầu sách trong 30 ngày. | Cao | 0,7707 | Có |
| 2 | Lớp có trạng thái Conflict khi bị trùng thời khóa biểu. | Xung đột lịch học khiến sinh viên không thể đăng ký lớp. | Cao | 0,5675 | Có |
| 3 | Ứng viên học bổng cần GPA tích lũy tối thiểu 3,4. | Thư viện cung cấp dịch vụ in và photocopy. | Thấp | 0,1575 | Có |
| 4 | Sinh viên có thể thanh toán học phí bằng chuyển khoản. | Cựu sinh viên chịu chi phí gửi trả sách qua bưu điện. | Thấp | 0,6744 | **Không** |
| 5 | Học bổng 50% được phân bổ trước học bổng 25%. | Chính sách hỗ trợ học phí không được dùng đồng thời với chính sách khác. | Trung bình-thấp | 0,3250 | Có |

Cặp 4 bất ngờ nhất: dù khác nghiệp vụ, cả hai câu cùng nói về một đối tượng đại học thực hiện **thanh toán/chịu chi phí**, khiến embedding đặt chúng khá gần nhau. Điều này cho thấy embedding nắm được mẫu quan hệ và từ vựng chung, nhưng độ gần vector không bảo đảm hai câu cùng trả lời một câu hỏi nghiệp vụ. Metadata và đánh giá top-k vẫn cần thiết.

## 5. Kết quả truy xuất của tôi — 10 điểm

Chiến lược cá nhân: `HeadingSectionChunker(chunk_size=300)`. Embedder: mô hình đa ngữ cục bộ nêu trên. Q1 dùng `metadata_filter={"audience": "student"}`; các câu còn lại không lọc.

| # | Câu hỏi | Top-1 chunk truy xuất | Score | Liên quan? | Câu trả lời Agent (tóm tắt, có căn cứ top-1) |
|---:|---|---|---:|:---:|---|
| 1 | Người dùng thư viện RMIT được mượn tối đa bao nhiêu tài liệu và trong bao lâu? | `rmit-student-library-2026` — mục “Mượn tài liệu” | 0,7994 | Có | Sinh viên được mượn tối đa 25 cuốn trong một tháng. |
| 2 | Điều kiện tín chỉ và GPA của học bổng thành tích RMIT năm 2026 là gì? | `rmit-current-student-scholarship-2026` — mục “Điều kiện” | 0,8089 | Có | Đã hoàn thành ít nhất 96 tín chỉ và GPA tích lũy từ 3,4/4,0. |
| 3 | Trạng thái Conflict khi đăng ký học phần VinUni có nghĩa là gì? | `vinuni-course-registration-2026` — mục “Trạng thái và điều kiện lớp” | 0,5998 | Có | Lớp bị trùng giờ với một lớp sinh viên đã đăng ký. |
| 4 | Nếu sinh viên RMIT không trả học phí đúng hạn thì điều gì có thể xảy ra? | `rmit-fees-and-finance` — mục “Không thanh toán đúng hạn” | 0,7046 | Có | Có thể bị rút khỏi các học phần và chuyển sang hủy hành chính; phí ký túc xá, thư viện và phí khác đã phát sinh không được đảo lại. |
| 5 | Mức hỗ trợ học phí cho người thân của sinh viên/cựu sinh viên RMIT bắt đầu học năm 2026 là bao nhiêu? | `rmit-tuition-fee-assistance-2026` — mục “Người thân và cựu sinh viên” | 0,7871 | Có | Người thân đủ điều kiện có thể được hỗ trợ 5% học phí. |

**Số câu có chunk liên quan trong top-3: 5/5.** Cả năm chunk đúng đều ở top-1 với chiến lược cá nhân.

Điểm học được quan trọng nhất từ so sánh cấu hình là không có một chunker thắng tuyệt đối về score: Recursive tốt nhất ở Q1–Q2, Sentence ở Q3, Fixed-size ở Q4 và Heading ở Q5. Heading vẫn phù hợp cho báo cáo cá nhân vì nó giữ tên mục với điều khoản, giúp đọc và truy vết nguồn dễ hơn trong khi vẫn đạt 5/5.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5/5 |
| Hướng tiếp cận | 10/10 |
| Hoàn thiện code | 30/30 |
| Dự đoán độ tương tự | 5/5 |
| Kết quả truy xuất | 10/10 |
| **Tổng phần cá nhân** | **60/60** |
