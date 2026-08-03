# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hoàng Tín  
**MSSV:** 2A202601603  
**Nhóm:** THT  
**Ngày:** 03/08/2026

## 1. Khởi động (Warm-up) — 5 điểm

### 1.1. Độ tương tự cosine

Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, vì vậy hai đoạn văn bản thường cùng chủ đề hoặc cùng ý định. Điểm gần 1 thể hiện mức tương đồng cao, điểm gần 0 thể hiện ít liên quan và điểm âm cho thấy hai hướng biểu diễn đối lập.

**Ví dụ tương tự cao**

- Câu A: “Sinh viên cần hoàn thành ít nhất 96 tín chỉ để ứng tuyển học bổng.”
- Câu B: “Điều kiện nộp học bổng là người học đã tích lũy tối thiểu 96 tín chỉ.”
- Hai câu diễn đạt cùng một điều kiện bằng từ ngữ khác nhau.

**Ví dụ tương tự thấp**

- Câu A: “Sinh viên có thể thanh toán học phí bằng chuyển khoản.”
- Câu B: “Thư viện mở khu vực tự học vào cuối tuần.”
- Hai câu thuộc hai nghiệp vụ khác nhau: tài chính và dịch vụ thư viện.

Cosine similarity ưu tiên hướng vector thay vì khoảng cách tuyệt đối nên ít bị ảnh hưởng bởi độ lớn của vector hoặc độ dài văn bản. Vì thế, phép đo thường phù hợp hơn Euclidean distance khi mục tiêu là so sánh ý nghĩa của text embeddings.

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

Số chunk tăng từ 23 lên 25 vì bước trượt giảm từ 450 xuống 400 ký tự. Overlap lớn hơn giữ được nhiều ngữ cảnh tại ranh giới chunk hơn, nhưng cũng tăng số embedding, dung lượng lưu trữ và lượng nội dung trùng lặp.

## 2. Hướng tiếp cận của tôi (My Approach) — 10 điểm

### Chunking

`SentenceChunker` dùng regex `(?<=[.!?])(?:[ \t]+|\r?\n+)` để tách sau dấu kết thúc câu và vẫn giữ dấu câu trong nội dung. Các câu được loại khoảng trắng thừa rồi nhóm tối đa theo `max_sentences_per_chunk`; chuỗi rỗng trả về danh sách rỗng.

`RecursiveChunker` ưu tiên tách theo đoạn, dòng, câu, từ và cuối cùng là ký tự. Các phần vừa giới hạn được gộp bằng buffer; phần quá dài được chuyển sang separator tiếp theo. Base case là đoạn không vượt quá `chunk_size`; nếu hết separator, thuật toán cắt cứng theo ký tự để luôn kết thúc.

Chiến lược cá nhân được chọn cho benchmark là `FixedSizeChunker(chunk_size=300, overlap=50)`. Cấu hình này đơn giản, tạo 25 chunk trên toàn corpus và dùng overlap để hạn chế mất ngữ cảnh ở ranh giới. Đổi lại, nó có thể cắt giữa câu và lưu trữ một phần nội dung lặp.

### EmbeddingStore

`add_documents` chuẩn hóa mỗi tài liệu thành record gồm ID nội bộ, nội dung, metadata, `doc_id` và embedding. Store luôn giữ dữ liệu trong bộ nhớ để tìm kiếm dot-product có kết quả xác định; ChromaDB được dùng như backend phụ nếu khả dụng.

`search` embedding truy vấn một lần, tính dot product với từng record, sắp xếp score giảm dần và lấy `top_k`. `search_with_filter` lọc metadata trước khi xếp hạng để tránh đưa tài liệu sai đối tượng vào context. `delete_document` xóa toàn bộ chunk có cùng `metadata.doc_id` và trả về trạng thái có xóa được dữ liệu hay không.

### KnowledgeBaseAgent

`answer` truy xuất các chunk liên quan, đánh số nguồn và đưa `source_url` cùng nội dung vào prompt. Prompt yêu cầu LLM chỉ sử dụng ngữ cảnh được cung cấp, không suy đoán, nói rõ khi thiếu dữ liệu và dẫn số nguồn khi có thể.

## 3. Hoàn thiện code (Core Implementation) — 30 điểm

Ba file được kiểm tra trực tiếp từ thư mục `NguyenHoangTin_2A202601603` bằng Python 3.11.9 và pytest 9.1.1.

```text
..........................................                               [100%]
42 passed in 0.18s
```

**Số test vượt qua: 42/42.**

## 4. Dự đoán độ tương tự — 5 điểm

Các dự đoán được đưa ra trước khi chạy model. Điểm thực tế sử dụng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, không dùng mock embedding.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---:|---|---|---|---:|:---:|
| 1 | Sinh viên được mượn tối đa 25 cuốn sách trong một tháng. | Hạn mức thư viện cho người học là 25 đầu sách trong 30 ngày. | Cao | 0,7707 | Có |
| 2 | Lớp có trạng thái Conflict khi bị trùng thời khóa biểu. | Xung đột lịch học khiến sinh viên không thể đăng ký lớp. | Cao | 0,5675 | Có |
| 3 | Ứng viên học bổng cần GPA tích lũy tối thiểu 3,4. | Thư viện cung cấp dịch vụ in và photocopy. | Thấp | 0,1575 | Có |
| 4 | Sinh viên có thể thanh toán học phí bằng chuyển khoản. | Cựu sinh viên chịu chi phí gửi trả sách qua bưu điện. | Thấp | 0,6744 | Không |
| 5 | Học bổng 50% được phân bổ trước học bổng 25%. | Chính sách hỗ trợ học phí không được dùng đồng thời với chính sách khác. | Trung bình-thấp | 0,3250 | Có |

Cặp 4 gây bất ngờ nhất vì hai câu khác nghiệp vụ nhưng cùng chứa quan hệ về chi trả và chi phí. Kết quả cho thấy embedding có thể đặt các câu có mẫu quan hệ chung ở gần nhau, dù chúng không thể thay thế nhau khi trả lời một câu hỏi cụ thể.

## 5. Kết quả truy xuất của tôi — 10 điểm

Chiến lược cá nhân: `FixedSizeChunker(chunk_size=300, overlap=50)`. Embedder: mô hình đa ngữ cục bộ nêu trên. Q1 sử dụng `metadata_filter={"audience": "student"}`; các câu còn lại không lọc.

| # | Câu hỏi | Top-1 chunk truy xuất | Score | Liên quan? | Câu trả lời Agent tóm tắt |
|---:|---|---|---:|:---:|---|
| 1 | Người dùng thư viện RMIT được mượn tối đa bao nhiêu tài liệu và trong bao lâu? | `rmit-student-library-2026` — nội dung quy định mượn tài liệu | 0,8149 | Có | Sinh viên được mượn tối đa 25 cuốn trong một tháng. |
| 2 | Điều kiện tín chỉ và GPA của học bổng thành tích RMIT năm 2026 là gì? | `rmit-current-student-scholarship-2026` — nội dung điều kiện ứng tuyển | 0,6937 | Có | Cần hoàn thành ít nhất 96 tín chỉ và có GPA tích lũy từ 3,4/4,0. |
| 3 | Trạng thái Conflict khi đăng ký học phần VinUni có nghĩa là gì? | `vinuni-course-registration-2026` — nội dung trạng thái lớp | 0,5939 | Có | Lớp bị trùng giờ với một lớp sinh viên đã đăng ký. |
| 4 | Nếu sinh viên RMIT không trả học phí đúng hạn thì điều gì có thể xảy ra? | `rmit-fees-and-finance` — nội dung không thanh toán đúng hạn | 0,7508 | Có | Sinh viên có thể bị rút khỏi học phần và chuyển sang hủy hành chính; một số phí đã phát sinh không được đảo lại. |
| 5 | Mức hỗ trợ học phí cho người thân của sinh viên/cựu sinh viên RMIT bắt đầu học năm 2026 là bao nhiêu? | `rmit-tuition-fee-assistance-2026` — nội dung hỗ trợ người thân | 0,7594 | Có | Người thân đủ điều kiện có thể được hỗ trợ 5% học phí. |

**Số câu có chunk liên quan trong top-3: 5/5.** Với cấu hình Fixed-size, cả năm tài liệu đúng đều xuất hiện ở top-1.

Điều quan trọng tôi học được từ việc so sánh các thành viên là không có một chunker dẫn đầu ở mọi truy vấn. Fixed-size đạt score cao nhất ở câu hỏi về chậm học phí, trong khi Recursive tốt hơn ở câu hỏi thư viện và học bổng; do đó cần chọn chiến lược dựa trên cấu trúc tài liệu và loại câu hỏi thay vì chỉ dựa vào số lượng chunk.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5/5 |
| Hướng tiếp cận | 10/10 |
| Hoàn thiện code | 30/30 |
| Dự đoán độ tương tự | 5/5 |
| Kết quả truy xuất | 10/10 |
| **Tổng phần cá nhân** | **60/60** |
