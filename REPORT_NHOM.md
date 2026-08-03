# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** THT

**Thành viên:** 

| STT | Họ và tên | Mã học viên | Vai trò trong nhóm |
|-----|-----------|-------------|--------------------|
| 1 | Nguyễn Duy Trọng | 2A202601333 | Thành viên |
| 2 | Nguyễn Hoàng Tín | 2A202601603 | Thành viên |
| 3 | Bùi Thế Huy | 2A202601881 | Thành viên |

**Ngày:** 03/08/2026

> Báo cáo đã có corpus, cấu hình và số liệu benchmark tái lập. Các ô nhận dạng cá nhân cần được nhóm điền trước khi nộp; các cấu hình A/B/C/D dưới đây không được trình bày như tên thành viên khi chưa có thông tin nhóm thực tế.

## 1. Lựa chọn tài liệu — 10 điểm

### Phạm vi

Nhóm tập trung vào dịch vụ và quy định có ảnh hưởng trực tiếp đến người học: đăng ký học phần, thư viện, học bổng, học phí và tài chính. Năm tài liệu thuộc RMIT Vietnam tạo trục so sánh nhất quán; một thông báo đăng ký học phần của VinUniversity bổ sung nghiệp vụ học vụ.

### Danh sách tài liệu

| # | Tài liệu | Nguồn công khai | Ngày lấy / phiên bản | Số ký tự nội dung | Metadata nổi bật |
|---:|---|---|---|---:|---|
| 1 | Chính sách mượn cho cựu sinh viên RMIT | [RMIT Vietnam](https://www.rmit.edu.vn/libraryvn/borrowing-and-resources/borrowing-and-returning/borrowing-for-alumni) | 03/08/2026 / `not-stated` | 778 | `audience=alumni`, `category=borrowing-policy` |
| 2 | Đăng ký học phần VinUni Hè 2026 | [VinUniversity Registrar](https://registrar.vinuni.edu.vn/2026/06/29/announcement-launch-of-the-new-student-portal-for-summer-2026-course-registration/) | 03/08/2026 / 29/06/2026 | 886 | `audience=student`, `category=course-registration` |
| 3 | Học bổng thành tích RMIT 2026 | [RMIT Vietnam](https://www.rmit.edu.vn/study-at-rmit/scholarships/current-student-scholarships) | 03/08/2026 / 2026 | 908 | `audience=student`, `category=scholarship` |
| 4 | Hỏi đáp phí và tài chính RMIT | [RMIT Vietnam](https://www.rmit.edu.vn/students/support/student-connect/ask-about-fees-and-finance) | 03/08/2026 / `not-stated` | 1.263 | `audience=student`, `category=fees-and-finance` |
| 5 | Dịch vụ thư viện RMIT cho sinh viên | [RMIT Vietnam](https://www.rmit.edu.vn/students/student-news-and-events/student-news/2026/newbie-101-unlock-library-power) | 03/08/2026 / 2026 | 846 | `audience=student`, `category=borrowing-and-study-support` |
| 6 | Hỗ trợ học phí RMIT 2026 | [RMIT Vietnam](https://www.rmit.edu.vn/study-at-rmit/tuition-fees/tuition-fee-assistance) | 03/08/2026 / 2026 | 1.187 | `audience=prospective-student`, `category=tuition-assistance` |

Các file là bản làm sạch và diễn đạt ngắn gọn từ trang nguồn; không chứa menu, quảng cáo, thông tin đăng nhập hoặc dữ liệu cá nhân. `data/k3_university/sources.csv` ánh xạ đúng một dòng cho mỗi tài liệu.

**Data governance**

- [x] Corpus có 6 tài liệu công khai, nằm trong giới hạn 5–10.
- [x] Không có dữ liệu cá nhân, hồ sơ nội bộ, thông tin đăng nhập hay nội dung sau đăng nhập.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` và căn cứ `public-page` trong `sources.csv`.
- [x] Mỗi tài liệu có `audience` cùng các trường hữu ích khác.

### Metadata schema

| Trường | Kiểu | Ví dụ | Giá trị đối với retrieval |
|---|---|---|---|
| `doc_id` | string | `rmit-student-library-2026` | Định danh ổn định, xóa toàn bộ chunk cùng tài liệu |
| `title` | string | `Dịch vụ thư viện RMIT dành cho sinh viên` | Hiển thị và truy vết nguồn |
| `source_url` | URL string | `https://www.rmit.edu.vn/...` | Kiểm chứng gold answer |
| `retrieved_at` | date string | `2026-08-03` | Đánh giá độ mới của snapshot |
| `document_version` | string | `2026` | Phân biệt phiên bản chính sách |
| `audience` | enum string | `student`, `alumni` | Loại tài liệu sai đối tượng trước khi xếp hạng |
| `institution` | string | `RMIT Vietnam` | Giới hạn kết quả theo trường |
| `department` | string | `library` | Định tuyến câu hỏi đến đơn vị phụ trách |
| `category` | string | `fees-and-finance` | Giảm nhiễu giữa các nghiệp vụ có từ vựng gần nhau |
| `language` | string | `vi` | Chọn ngôn ngữ trả lời/embedding phù hợp |

## 2. Thiết kế chiến lược — 15 điểm

### Thiết lập thí nghiệm

- Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Corpus và 5 query giống nhau cho mọi cấu hình.
- `chunk_size=300`; Fixed-size dùng `overlap=50`; Sentence dùng tối đa 3 câu; Recursive và Heading không overlap.
- Q1 lọc `audience=student`; các query khác không lọc.
- Script tái lập: `scripts/run_benchmark.py`.

### Baseline trên ba tài liệu

| Tài liệu | Chiến lược | Số chunk | Độ dài TB | Nhận xét mạch lạc |
|---|---|---:|---:|---|
| Alumni library | Fixed-size | 3 | 259,33 | Có thể cắt giữa câu/mục |
| Alumni library | Sentence | 3 | 258,00 | Giữ câu nhưng tiêu đề có thể dính câu sau |
| Alumni library | Recursive | 4 | 193,25 | Ưu tiên đoạn và dòng |
| Alumni library | Heading | 5 | 164,20 | Giữ tên mục với điều khoản |
| Course registration | Fixed-size | 3 | 295,33 | Ít chunk nhưng ranh giới cơ học |
| Course registration | Sentence | 4 | 220,25 | Giữ câu hoàn chỉnh |
| Course registration | Recursive | 5 | 175,80 | Tách tốt theo đoạn |
| Course registration | Heading | 5 | 179,20 | Mỗi quy tắc gắn với heading |
| Current scholarship | Fixed-size | 4 | 227,00 | Có overlap nhưng vẫn có thể cắt ý |
| Current scholarship | Sentence | 3 | 301,33 | Một chunk vượt 300 vì giới hạn theo số câu |
| Current scholarship | Recursive | 5 | 180,20 | Độ dài đều, ý khá trọn vẹn |
| Current scholarship | Heading | 5 | 183,00 | Dễ đọc và truy vết mục |

### Các cấu hình so sánh

**Cấu hình A — HeadingSectionChunker (chiến lược cá nhân của bản nộp này)**

Chiến lược phát hiện heading Markdown, giữ heading trong chunk và dùng recursive splitting nếu section quá dài. Cách này phù hợp quy định đại học vì các heading như “Điều kiện”, “Không thanh toán đúng hạn” cung cấp nhãn ngữ nghĩa trực tiếp.

```python
from src import HeadingSectionChunker

chunker = HeadingSectionChunker(chunk_size=300)
chunks = chunker.chunk(markdown_text)
```

**Cấu hình B — FixedSizeChunker**

`chunk_size=300, overlap=50` là baseline đơn giản, kiểm soát tốt kích thước và giữ một phần ngữ cảnh qua overlap. Điểm yếu là ranh giới không biết cấu trúc câu/mục và tạo nội dung lặp.

**Cấu hình C — SentenceChunker**

Nhóm tối đa 3 câu để bảo toàn câu hoàn chỉnh. Cấu hình ít chunk nhất nhưng không bảo đảm giới hạn ký tự; heading Markdown không kết thúc bằng dấu câu có thể dính với nội dung không mong muốn.

**Cấu hình D — RecursiveChunker**

Ưu tiên tách theo đoạn, dòng, câu rồi từ. Cấu hình cho chunk nhỏ, đều và đạt score tốt trên điều kiện học bổng, nhưng tạo nhiều chunk nhất.

> Khi có danh sách nhóm thật, phân công A/B/C/D cho từng thành viên và thay phần nhận dạng ở đầu báo cáo. Các kết quả dưới đây là kết quả chạy thực tế của bốn cấu hình, không phải tuyên bố về người chưa được cung cấp tên.

### So sánh kết quả

| Cấu hình | Chiến lược | Số chunk toàn corpus | Điểm truy xuất | Điểm mạnh | Điểm yếu |
|---|---|---:|---:|---|---|
| A | Heading | 34 | 10/10 | Truy vết theo mục; 5/5 đúng ở top-1 | Nhiều chunk; heading cấp cao có thể thành chunk ngắn |
| B | Fixed-size | 25 | 10/10 | Ít chunk; Q4 có score top-1 cao nhất 0,7508 | Có thể cắt giữa câu; overlap gây lặp |
| C | Sentence | 19 | 9/10 | Ít chunk nhất; giữ câu hoàn chỉnh | Q4 đúng chỉ ở rank 2; có chunk vượt 300 |
| D | Recursive | 35 | 10/10 | Score tốt nhất Q1 và Q2; kích thước đều | Nhiều chunk và mất nhãn heading ở một số đoạn |

Không có chiến lược thắng mọi query. Heading được chọn cho bản cá nhân vì cân bằng retrieval 5/5 với tính mạch lạc và khả năng truy vết điều khoản; Fixed-size vẫn tốt hơn về score ở Q4, còn Recursive nhỉnh hơn ở Q1–Q2. Kết luận vì vậy dựa trên cả chất lượng chunk lẫn điểm số, không chỉ lấy score trung bình.

## 3. Câu hỏi đánh giá và chất lượng truy xuất — 10 điểm

### Đúng 5 benchmark queries và gold answers

| # | Query | Gold answer kiểm chứng từ corpus | Chunk chứa thông tin |
|---:|---|---|---|
| 1 | Người dùng thư viện RMIT được mượn tối đa bao nhiêu tài liệu và trong bao lâu? | Với đối tượng **sinh viên**: tối đa 25 cuốn trong một tháng. Q1 bắt buộc lọc `audience=student`; tài liệu alumni có quy tắc 5 tài liệu/30 ngày. | `rmit-student-library-2026`, “Mượn tài liệu” |
| 2 | Điều kiện tín chỉ và GPA của học bổng thành tích RMIT năm 2026 là gì? | Hoàn thành ít nhất 96 tín chỉ và GPA tích lũy tối thiểu 3,4/4,0. | `rmit-current-student-scholarship-2026`, “Điều kiện” |
| 3 | Trạng thái Conflict khi đăng ký học phần VinUni có nghĩa là gì? | Lớp trùng giờ với một lớp đã đăng ký. | `vinuni-course-registration-2026`, “Trạng thái và điều kiện lớp” |
| 4 | Nếu sinh viên RMIT không trả học phí đúng hạn thì điều gì có thể xảy ra? | Có thể bị rút khỏi toàn bộ học phần và chuyển sang hủy hành chính; phí ký túc xá, thư viện và phí khác đã phát sinh không được đảo lại. | `rmit-fees-and-finance`, “Không thanh toán đúng hạn” |
| 5 | Mức hỗ trợ học phí cho người thân của sinh viên/cựu sinh viên RMIT bắt đầu học năm 2026 là bao nhiêu? | Người thân đủ điều kiện có thể được hỗ trợ 5% học phí. | `rmit-tuition-fee-assistance-2026`, “Người thân và cựu sinh viên” |

### Tổng hợp retrieval

| # | Cấu hình có top-1 score cao nhất | Score | Chunk đúng trong top-3? | Ghi chú |
|---:|---|---:|:---:|---|
| 1 | Recursive | 0,8235 | Có | Filter student loại tài liệu alumni khỏi candidates |
| 2 | Recursive | 0,8105 | Có | Heading sát nút ở 0,8089 |
| 3 | Sentence | 0,6033 | Có | Cả bốn cấu hình đều trả đúng ở top-1 |
| 4 | Fixed-size | 0,7508 | Có | Sentence thất bại ở top-1 nhưng đúng ở rank 2 |
| 5 | Heading | 0,7871 | Có | Heading “Người thân và cựu sinh viên” tăng grounding |

Tất cả bốn cấu hình đều có chunk liên quan trong top-3 cho 5/5 query. Với Heading, cả năm chunk đúng đứng top-1, nên câu trả lời extractive từ context khớp năm gold answer.

### Tác động của metadata filter

Q1 cố ý mơ hồ về loại người dùng. Khi không lọc với Heading, top-5 chứa hai chunk alumni ở rank 2 (0,6582) và rank 3 (0,6457), bên cạnh quy tắc sinh viên 25 cuốn. Sau `metadata_filter={"audience": "student"}`, cả hai chunk alumni bị loại; top-3 chỉ còn tài liệu cho sinh viên. Top-1 không đổi, nhưng precision và độ an toàn của context tăng rõ rệt, ngăn agent trộn hai hạn mức 25 và 5.

## 4. Demo, failure analysis và bài học — 5 điểm

### Failure case

Ở Q4, SentenceChunker xếp chunk alumni về trách nhiệm trả sách đúng hạn ở top-1 với score 0,6565, trong khi chunk phí và tài chính đúng chỉ đứng rank 2 với 0,5882. Câu hỏi chứa mẫu “không ... đúng hạn”, gần về ngữ nghĩa với “không trả tài liệu đúng hạn”; chunk theo câu thiếu nhãn section đủ mạnh nên model nhầm nghiệp vụ.

Đây là lỗi **top-1 precision**, dù top-3 recall vẫn thành công. Có ba cải thiện hợp lý: giữ heading trong chunk; lọc `audience=student` và/hoặc `category=fees-and-finance`; hoặc viết query cụ thể hơn với từ “học phí”. Kết quả Heading đưa đúng tài liệu phí lên top-1 (0,7046), cho thấy cấu trúc section giúp grounding.

### Insight dùng khi thuyết trình

1. Embedding ngữ nghĩa vẫn có thể nhầm hai hành động “trả đúng hạn” thuộc hai nghiệp vụ; metadata không phải phần trang trí mà là lớp kiểm soát precision.
2. Chiến lược ít chunk nhất không đồng nghĩa tốt nhất: Sentence chỉ tạo 19 chunk nhưng thất bại top-1 ở Q4; Heading tạo 34 chunk nhưng giữ điều khoản dễ kiểm chứng.
3. Cần đánh giá theo query: mỗi chiến lược dẫn đầu ít nhất một câu, vì vậy nên chọn theo cấu trúc dữ liệu và failure cost thay vì một con số tổng quát.

Nếu làm lại, nhóm sẽ thêm trường `effective_date`, chuẩn hóa taxonomy `audience`, và tạo query đối nghịch theo từng audience để stress-test filter. Nhóm cũng sẽ merge heading cấp cao quá ngắn với section con nhằm giảm số chunk mà vẫn giữ nhãn ngữ nghĩa.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Lựa chọn tài liệu | 10/10 |
| Thiết kế chiến lược | 15/15 |
| Chất lượng truy xuất | 10/10 |
| Nội dung chuẩn bị demo | 5/5 |
| **Tổng phần nhóm** | **40/40** |
