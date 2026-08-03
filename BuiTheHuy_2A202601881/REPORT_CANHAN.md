# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Bùi Thế Huy  
**Mã sinh viên:** 2A202601881  
**Nhóm:** THT (E403)  
**Ngày:** 03/08/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiệm cận 1.0) nghĩa là hai vectơ nhúng (embedding vectors) có góc giữa chúng rất nhỏ trong không gian đa chiều, cho thấy hai đoạn văn bản tương ứng có mức độ tương đồng cao về mặt ý nghĩa/ngữ cảnh (semantic similarity), bất kể độ dài ngắn của hai đoạn văn bản đó.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** Sinh viên cần đăng ký học phần trước ngày 15 hàng tháng.
- **Câu B:** Hạn chót để người học đăng ký các môn học là ngày 15 mỗi tháng.
- **Tại sao tương đồng:** Cả hai câu đều truyền tải cùng một nội dung thông tin (thời hạn đăng ký học phần/môn học là ngày 15), dù sử dụng từ ngữ ("sinh viên" / "người học", "học phần" / "môn học") và cấu trúc ngữ pháp khác nhau nhưng mang ý nghĩa ngữ nghĩa hoàn toàn trùng khớp.

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** Sinh viên cần đăng ký học phần trước ngày 15 hàng tháng.
- **Câu B:** Thời tiết hôm nay trời mưa to và có bão lớn ở miền Trung.
- **Tại sao khác:** Hai câu đề cập đến hai chủ đề hoàn toàn độc lập và không liên quan đến nhau (thủ tục đăng ký học tập vs hiện tượng thời tiết/thiên tai), dẫn đến các vectơ nhúng hướng về các góc khác nhau trong không gian đa chiều.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid đo khoảng cách tuyệt đối giữa hai điểm cuối của vectơ, do đó dễ bị ảnh hưởng bởi độ dài của văn bản (văn bản dài hơn tạo ra vectơ có chuẩn lớn hơn, làm khoảng cách Euclid tăng lên dù ý nghĩa tương đồng). Ngược lại, độ tương tự cosine chỉ đo hướng (góc) giữa hai vectơ ($\cos \theta = \frac{A \cdot B}{\|A\| \|B\|}$), loại bỏ hoàn toàn yếu tố độ dài văn bản và phản ánh chính xác độ tương đồng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> **Trình bày phép tính:**  
> - Độ dài tài liệu ($L$) = $10,000$ ký tự  
> - Kích thước chunk ($chunk\_size$) = $500$ ký tự  
> - Độ chồng chéo ($overlap$) = $50$ ký tự  
> - Bước dịch chuyển giữa các chunk ($stride = chunk\_size - overlap$) = $500 - 50 = 450$ ký tự  
> - Áp dụng công thức:  
>   $số\_lượng\_chunk = \left\lceil \frac{\text{độ\_dài\_tài\_liệu} - \text{độ\_chồng\_chéo}}{\text{kích\_thước\_chunk} - \text{độ\_chồng\_chéo}} \right\rceil = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \lceil 22.111... \rceil = 23$  
> **Đáp án:** **23** chunks (bao gồm 22 chunks kích thước đầy đủ 500 ký tự và 1 chunk cuối cùng chứa phần dư).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> **Phép tính khi overlap = 100:**  
> Bước dịch chuyển $stride = 500 - 100 = 400$ ký tự.  
> $số\_lượng\_chunk = \left\lceil \frac{10000 - 100}{400} \right\rceil = \left\lceil \frac{9900}{400} \right\rceil = \lceil 24.75 \rceil = 25$ chunks.  
> **Thay đổi:** Số lượng chunk **tăng từ 23 lên 25 chunks** (tăng thêm 2 chunks).  
> **Lý do muốn độ chồng chéo (overlap) nhiều hơn:**  
> Việc tăng độ chồng chéo giúp duy trì tính liên tục ngữ cảnh giữa các ranh giới phân chia, tránh tình trạng thông tin quan trọng hoặc một câu hoàn chỉnh bị cắt ngang ở điểm phân đoạn làm thất thoát ý nghĩa khi thực hiện truy xuất (retrieval).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `BuiTheHuy_2A202601881`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy (regex) `re.split(r'(?<=[.!?])\s+', text.strip())` để tách văn bản thành danh sách câu dựa trên các dấu kết thúc câu (`.`, `!`, `?` theo sau bởi khoảng trắng hoặc ký tự xuống dòng). Sau đó, nhóm các câu lại theo số lượng tối đa `max_sentences_per_chunk` nối bằng khoảng trắng để tạo thành từng chunk. Xử lý trường hợp ngoại lệ văn bản rỗng/khoảng trắng bằng cách trả về danh sách rỗng `[]`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thực hiện chia nhỏ đệ quy văn bản sử dụng danh sách phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Trong hàm `_split`, nếu đoạn văn bản dài hơn `chunk_size`, thuật toán thử tách theo phân cách hiện tại và gom các đoạn nhỏ lại sao cho tổng độ dài $\le$ `chunk_size`; nếu một đoạn lẻ vẫn quá lớn, hàm sẽ đệ quy tiếp với danh sách phân cách còn lại. Trường hợp cơ sở (base case) là khi văn bản có độ dài $\le$ `chunk_size` hoặc danh sách dấu phân cách cạn kiệt (trường hợp rỗng/chính xác đến từng ký tự), hệ thống sẽ trả về chunk trực tiếp hoặc dùng `FixedSizeChunker`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Khi gọi `add_documents`, hệ thống duyệt từng `Document`, nhúng nội dung thông qua `_embedding_fn` và lưu dưới dạng bản ghi dictionary (chứa `id`, `content`, `metadata`, `embedding`) vào danh sách `self._store`. Hàm `search` thực hiện nhúng `query` và tính tích vô hướng (dot product `_dot`) giữa vectơ truy vấn với vectơ nhúng của từng chunk lưu giữ để xếp hạng điểm tương đồng ngữ nghĩa, sau đó trả về top-k chunk có điểm cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Hàm `search_with_filter` thực hiện pre-filtering (lọc trước): duyệt qua `self._store` để chỉ giữ lại các chunk có `metadata` khớp hoàn toàn với tất cả cặp key-value trong `metadata_filter`, rồi mới gọi hàm tìm kiếm tương đồng trên tập đã lọc. Hàm `delete_document` xóa tất cả các chunk mà `id` hoặc `metadata['doc_id']` trùng với `doc_id` truyền vào bằng cách lọc danh sách `self._store`, trả về `True` nếu có chunk bị loại bỏ và `False` nếu không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` triển khai mô hình RAG (Retrieval-Augmented Generation): gọi `self.store.search(question, top_k)` để truy xuất top-k chunk có điểm số cao nhất từ kho tri thức, sau đó ghép các nội dung này lại thành chuỗi context. Cấu trúc prompt được thiết lập dưới dạng: `Context:\n{context}\n\nQuestion: {question}\nAnswer:` và được truyền vào hàm callback `llm_fn` để mô hình sinh câu trả lời chính xác dựa trên ngữ cảnh đã cung cấp.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Hạn chót đóng học phí học phần Hè là ngày 15 hàng tháng. | Sinh viên cần thanh toán tiền học trước ngày 15 mỗi tháng. | cao | 0.8500 | Có |
| 2 | Học viên có thể mượn tối đa 25 cuốn sách từ thư viện. | Thư viện cho phép sinh viên rút mượn nhiều nhất 25 tài liệu. | cao | 0.8200 | Có |
| 3 | Sinh viên được phép nộp muộn học phí nếu có đơn xin gia hạn. | Sinh viên tuyệt đối không được nộp muộn học phí trong bất kỳ trường hợp nào. | thấp | 0.7800 | Không |
| 4 | Sinh viên phải trả sách thư viện đúng hạn. | Sinh viên phải đóng tiền học phí đúng hạn. | thấp | 0.6500 | Không |
| 5 | Quy định đăng ký học phần hè cho sinh viên VinUni. | Thời tiết Hà Nội hôm nay trời nắng nhẹ và có gió mát. | thấp | 0.1200 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất xảy ra ở Cặp 3 (ý nghĩa phủ định) và Cặp 4 (khác nghiệp vụ thư viện vs học phí), hai câu vẫn nhận điểm tương đồng cao (0.65 - 0.78). Điều này chứng minh text embeddings hiện tại chủ yếu tập trung vào các từ khóa quan trọng và cấu trúc ngữ pháp chung thay vì thấu hiểu sâu sắc logic phủ định hay phạm vi nghiệp vụ hẹp. Do đó, việc kết hợp metadata filter (`audience`, `category`) là giải pháp bắt buộc để duy trì độ chính xác cao.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `BuiTheHuy_2A202601881`. **5 câu hỏi này trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Người dùng thư viện RMIT được mượn tối đa bao nhiêu tài liệu và trong bao lâu? | Với đối tượng sinh viên: mượn tối đa 25 cuốn trong một tháng (`rmit-student-library-2026`) | 0.8235 | Có | Sinh viên RMIT được phép mượn tối đa 25 tài liệu trong thời gian 1 tháng. |
| 2 | Điều kiện tín chỉ và GPA của học bổng thành tích RMIT năm 2026 là gì? | Hoàn thành ít nhất 96 tín chỉ và GPA tích lũy tối thiểu 3.4/4.0 (`rmit-current-student-scholarship-2026`) | 0.8105 | Có | Điều kiện cần đạt là tối thiểu 96 tín chỉ tích lũy cùng điểm GPA từ 3.4/4.0 trở lên. |
| 3 | Trạng thái Conflict khi đăng ký học phần VinUni có nghĩa là gì? | Lớp học bị trùng thời khóa biểu với một lớp đã đăng ký (`vinuni-course-registration-2026`) | 0.6033 | Có | Conflict chỉ tình trạng môn học đăng ký bị trùng giờ với một môn học khác đã chọn trước đó. |
| 4 | Nếu sinh viên RMIT không trả học phí đúng hạn thì điều gì có thể xảy ra? | Có thể bị rút khỏi toàn bộ học phần, chuyển sang hủy hành chính (`rmit-fees-and-finance`) | 0.7508 | Có | Sinh viên có nguy cơ bị rút tên khỏi tất cả học phần và chuyển sang diện hủy hành chính. |
| 5 | Mức hỗ trợ học phí cho người thân của sinh viên/cựu sinh viên RMIT bắt đầu học năm 2026 là bao nhiêu? | Mức hỗ trợ 5% học phí cho người thân đủ điều kiện (`rmit-tuition-fee-assistance-2026`) | 0.7871 | Có | Người thân đủ điều kiện của sinh viên/cựu sinh viên được giảm 5% học phí khi nhập học. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Kỹ thuật pre-filtering bằng Metadata đóng vai trò cực kỳ quan trọng để ngăn ngừa nhiễu truy xuất từ các đối tượng không liên quan (ví dụ: phân biệt đối tượng `student` và `alumni`). Ngoài ra, giữ lại cấu trúc tiêu đề (Heading) khi phân chia văn bản giúp tăng mức độ grounded của câu trả lời extractive trong quy trình RAG.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
