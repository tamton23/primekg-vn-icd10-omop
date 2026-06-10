# PRIME-KG VN: Đồ thị Tri thức Y khoa Lâm sàng (ICD-10 & OMOP CDM)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data: Clinical](https://img.shields.io/badge/Data-Clinical_Medicine-red.svg)]()

**PRIME-KG VN (Scientific Edition)** là một hệ thống tự động thu thập, trích xuất và xây dựng đồ thị tri thức y khoa (Knowledge Graph) tập trung chuyên sâu vào khía cạnh lâm sàng. 

Lấy danh mục mã bệnh **ICD-10** của Bộ Y tế Việt Nam làm xương sống, dự án này kiến tạo một mạng lưới liên kết có cấu trúc giữa các bệnh lý và hàng chục ngàn thực thể y khoa khác (Triệu chứng, Thuốc, Biến chứng, v.v.). Dữ liệu được tổng hợp, khử nhiễu tự động từ các nguồn chính thống trong nước và quốc tế. Toàn bộ cấu trúc đồ thị được ánh xạ tương thích với tiêu chuẩn **OMOP CDM 5.3.1**.

---

## 💡 Đặc tính Kỹ thuật & Kiến trúc Hệ thống

Hệ thống được xây dựng với tư duy kỹ thuật bền bỉ (Fault-tolerant) và kiến trúc dữ liệu nghiêm ngặt:

* **Kiến trúc Cứng (Hard-Anchoring):** Khác với các hệ thống sinh đồ thị ngẫu nhiên, hệ thống này **KHÔNG** dùng LLM để tự bịa ra loại liên kết. Các cạnh được định nghĩa bằng toán học thông qua `RELATION_RULES` và liên kết nội bộ `EXCLUDES`/`INCLUDES` được bóc tách trực tiếp từ cột Hướng dẫn của WHO trong file ICD-10 gốc.
* **Knowledge Hub (Khử trùng lặp):** Gộp các Node giống nhau (cùng SHA-256 hash), tự động nối chuỗi (`|`) các mô tả và bằng chứng (`evidence`) từ nhiều bài báo khác nhau vào một Node duy nhất.
* **Tương thích igraph & Neo4j:** Sinh mã `node_index` liên tục tuyệt đối, đảm bảo mapping `x_id`/`y_id` chuẩn xác 100%, sẵn sàng nạp vào bất kỳ cơ sở dữ liệu đồ thị nào.
* **Cơ chế Chống sập (Anti-Crash):** Tích hợp tính năng *Kiểm toán chéo* để gỡ checkpoint các bệnh cào lỗi. Kết hợp hệ thống Auto-Save theo từng cụm và thuật toán xoay vòng SearXNG URL để chống rate-limit.

---

## 🌐 Phân luồng Dữ liệu "5 Tầng" & Đa Ngữ

Quá trình crawl dữ liệu (Web Scraping) được tối ưu hóa bằng `ThreadPoolExecutor` và chia làm 5 tầng uy tín từ cao xuống thấp. **Đặc biệt, hệ thống tự động dịch từ khóa sang Tiếng Anh** khi tìm kiếm ở các tầng quốc tế:

1.  **Tầng 1 (Chính thống VN):** `gov.vn`, `tapchiyhocduphong.vn`, `vjmed.org.vn`...
2.  **Tầng 2 (Bệnh viện lớn VN):** `vinmec.com`, `nhathuoclongchau.com.vn`, `medlatec.vn`...
3.  **Tầng 3 (Học thuật Quốc tế - Tự dịch Tiếng Anh):** `ncbi.nlm.nih.gov`, `thelancet.com`, `jamanetwork.com`...
4.  **Tầng 4 (Tổ chức Y tế - Tự dịch Tiếng Anh):** `who.int`, `cdc.gov`, `mayoclinic.org`...
5.  **Tầng 5 (Nguồn mở rộng):** Mở xích tìm kiếm tự do nếu 4 tầng trên không cung cấp đủ số bài quy định.

---

## 🤖 Luồng Xử lý AI Đa tác tử (Multi-Agent Pipeline)

Thay vì dùng 1 prompt nhồi nhét, hệ thống sử dụng Ollama (Qwen3-VL 8B) vận hành song song 3 Agent độc lập với chuẩn `format: json` ép buộc:

1.  **Agent Evaluator (Người gác cổng):** Phân tích 2000 ký tự đầu của bài báo. **Chặn đứng** các tài liệu Thú Y thuần túy (chữa bệnh cho heo, gà, chó, mèo), nhưng đủ thông minh để **Cho phép** các bài viết về bệnh truyền nhiễm từ động vật sang người (Zoonotic disease).
2.  **Agent Extractor (Máy trích xuất):** Đọc sâu tới 25.000 ký tự. Bóc tách triệt để 9 loại thực thể lâm sàng, ép buộc dịch mọi dữ liệu sang Tiếng Việt chuẩn và bắt buộc trích xuất câu nguyên văn làm `evidence`.
3.  **Agent Reviewer (Giám sát viên):** Kiểm tra lại tập hợp các thực thể vừa bóc tách, loại bỏ các kết quả bị ảo giác (hallucination) hoặc quá dài dòng vô nghĩa trước khi đưa vào đồ thị.

---

## 📊 Báo cáo Thống kê Dữ liệu Chi tiết

Tiến độ thu thập hiện tại đang tập trung ở vùng mã **A00 đến G00.1** (Bao phủ **1,219** mã bệnh có dữ liệu web thực tế trên tổng số 15,844 mã ICD-10 gốc, tương đương **7.69%**).

### 1. Phân bố Số lượng Đỉnh (Nodes)
Đồ thị được phân chia rạch ròi thành 9 loại thực thể lâm sàng chính (Tổng cộng **32,163 Nodes**):

| Loại Thực thể | Khái niệm | Số lượng | Tỷ lệ (%) |
| :--- | :--- | :--- | :--- |
| **RiskFactor** | Yếu tố nguy cơ | 4,974 | 15.46% |
| **Symptom** | Triệu chứng lâm sàng | 4,832 | 15.02% |
| **Intervention** | Can thiệp y tế | 4,618 | 14.36% |
| **Disease** | Bệnh lý (Mã ICD-10) | 4,232 | 13.16% |
| **Complication** | Biến chứng | 3,894 | 12.11% |
| **Demographic** | Đặc điểm nhân khẩu học | 3,474 | 10.80% |
| **DiagnosticTest**| Xét nghiệm / Chẩn đoán | 2,620 | 8.15% |
| **Pathogen** | Tác nhân gây bệnh | 1,861 | 5.79% |
| **Drug** | Thuốc điều trị | 1,658 | 5.15% |

### 2. Phân tích Độ "Dày" Đồ thị (Graph Density)
Tổng số cạnh đạt **76,415 Edges**. Với 1,219 bệnh sở hữu dữ liệu web thực tế, đồ thị đạt mật độ liên kết rất cao: **60.31 liên kết / 1 Bệnh**. Cụ thể, trung bình một mã bệnh sẽ được kết nối với:
`11.0 Triệu chứng` | `8.6 Biến chứng` | `8.6 Yếu tố nguy cơ` | `8.5 Can thiệp y tế` | `7.8 Đặc điểm nhân khẩu` | `6.1 Phương pháp xét nghiệm` | `4.9 Thuốc điều trị` | `4.3 Tác nhân gây bệnh`.

---

## 🔗 Cấu trúc Quan hệ & Tương thích OMOP CDM

Hệ thống định nghĩa chặt chẽ 8 loại quan hệ có hướng, ánh xạ trực tiếp vào các bảng của **Mô hình Dữ liệu Chung OMOP (CDM v5.3.1)**:

| Loại Đỉnh Nguồn | Quan hệ (Relation) | Loại Đỉnh Đích | Ánh xạ Bảng OMOP CDM |
| :--- | :--- | :--- | :--- |
| **Drug** | `TREATS` (Điều trị) | **Disease** | `drug_exposure` |
| **Intervention** | `PART_OF_TREATMENT` | **Disease** | `procedure_occurrence` |
| **RiskFactor** | `INCREASES_RISK_OF` | **Disease** | `observation` |
| **Pathogen** | `CAUSES` (Gây ra) | **Disease** | `specimen` / `observation` |
| **Demographic** | `AFFECTS_POPULATION` | **Disease** | `concept` |
| **Disease** | `HAS_SYMPTOM` | **Symptom** | `observation` |
| **Disease** | `DIAGNOSED_BY` | **DiagnosticTest** | `measurement` |
| **Disease** | `HAS_COMPLICATION` | **Complication** | `condition_occurrence` |

---

## 🕸️ Trực quan hóa Đồ thị (Neo4j)

### 1. Mạng lưới Tổng quan (Macroscopic View)
Khi mở rộng góc nhìn toàn cảnh, đồ thị thể hiện rõ sự liên thông phức tạp giữa các họ bệnh khác nhau. Các mã bệnh không tồn tại độc lập mà chia sẻ chung nhiều tập hợp thực thể (triệu chứng, thuốc), tạo thành các cụm tri thức hỗ trợ rất tốt cho chẩn đoán phân biệt.

![Tổng quan liên kết các họ bệnh trên Đồ thị Neo4j](image_d33bff.png)

### 2. Góc nhìn Chi tiết (Microscopic View)
Khi đi sâu vào một node cụ thể, ví dụ mã bệnh **A00.0 (Bệnh tả do Vibrio cholerae 01, típ sinh học cholerae)**, chúng ta có thể thấy rõ cấu trúc mạng lưới hình sao:

![Trực quan hóa chi tiết Đồ thị Neo4j - Bệnh Tả (A00.0)](visualisation_2.png)

Từ node Bệnh trung tâm, hệ thống truy xuất các triệu chứng (nôn, tiêu chảy, mất nước), thuốc điều trị, và mối quan hệ phân cấp `IS_SUBTYPE_OF` ngược lên bệnh gốc (Bệnh tả A00).

---

## 📂 Cấu trúc Thư mục & Cách chạy

* `run_crawl.py`: Script Core (Scientific Edition) điều khiển luồng cào dữ liệu, gọi Ollama và xây dựng đồ thị.
* `icd10_danh_muc.csv`: Tệp chứa danh mục gốc mã bệnh ICD-10.
* `emd.py`: Script thống kê, phân tích mật độ và kiểm tra vùng phủ (Gaps) của Đồ thị.
* `kg_output/`: Thư mục chứa kết quả (`edges.csv`, `nodes_*.csv` và log `raw_sources.jsonl`).

### 🚀 Lệnh khởi chạy Crawler
```bash
# Cào một bệnh cụ thể (VD: Bệnh tả), thu thập tối đa 15 bài báo/nguồn
python run_crawl.py --query "Bệnh tả" --max_urls 15

# Chạy cào toàn bộ danh mục tự động (Dựa trên checkpoint để tiếp tục nếu bị gián đoạn)
python run_crawl.py --crawl_all
