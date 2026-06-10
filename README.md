# primekg-vn-icd10-omop
PrimeKG-style knowledge graph for Vietnamese ICD-10 diseases.
# PRIME-KG VN: Đồ thị Tri thức Y khoa Lâm sàng (ICD-10 & OMOP CDM)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data: Clinical](https://img.shields.io/badge/Data-Clinical_Medicine-red.svg)]()

**PRIME-KG VN** là một hệ thống tự động thu thập, trích xuất và xây dựng đồ thị tri thức y khoa (Knowledge Graph) tập trung chuyên sâu vào khía cạnh lâm sàng. 

Lấy danh mục mã bệnh **ICD-10** của Bộ Y tế Việt Nam làm xương sống, dự án này kiến tạo một mạng lưới liên kết có cấu trúc giữa các bệnh lý và hàng chục ngàn thực thể y khoa khác (Triệu chứng, Thuốc, Biến chứng, v.v.). Dữ liệu được tổng hợp, khử nhiễu tự động từ các nguồn chính thống trong nước (Cổng thông tin chính phủ, Bệnh viện) và quốc tế (WHO, NCBI). Toàn bộ cấu trúc đồ thị được ánh xạ tương thích với tiêu chuẩn **OMOP CDM 5.3.1**.

---

## 📊 Báo cáo Thống kê Dữ liệu Chi tiết

Tiến độ thu thập hiện tại đang tập trung ở vùng mã **A00 đến G00.1** (Bao phủ **1,219** mã bệnh có dữ liệu web thực tế trên tổng số 15,844 mã ICD-10 gốc, tương đương **7.69%**).

### 1. Kích thước Tổng thể (Graph Size)
* **Tổng số Cạnh (Edges):** 76,415 (Lưu trữ các quan hệ có hướng)
* **Tổng số Đỉnh (Nodes):** 32,163 (Bao gồm hệ thống khung mã ICD-10 gốc)

### 2. Phân bố Số lượng Đỉnh (Node Distribution)
Đồ thị được phân chia rạch ròi thành 9 loại thực thể lâm sàng chính:

| Loại Thực thể (Node Type) | Khái niệm | Số lượng | Tỷ lệ (%) |
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

### 3. Phân tích Độ "Dày" & Toàn vẹn Đồ thị (Graph Density)
Với 1,219 bệnh sở hữu dữ liệu web lâm sàng thực tế, đồ thị đạt mật độ liên kết rất cao: **60.31 liên kết / 1 Bệnh**. Cụ thể, trung bình một mã bệnh sẽ được kết nối với:
* **11.0** Triệu chứng (`Symptom`)
* **8.6** Biến chứng (`Complication`)
* **8.6** Yếu tố nguy cơ (`RiskFactor`)
* **8.5** Can thiệp y tế (`Intervention`)
* **7.8** Đặc điểm nhân khẩu (`Demographic`)
* **6.1** Phương pháp xét nghiệm (`DiagnosticTest`)
* **4.9** Loại thuốc điều trị (`Drug`)
* **4.3** Tác nhân gây bệnh (`Pathogen`)

### 4. Đánh giá Độ tin cậy của Nguồn Tham khảo (Source Tiers)
Mỗi cạnh (quan hệ) trong đồ thị đều được gán minh bạch với câu trích xuất nguyên văn (`evidence`) và URL nguồn.
* **Tầng 1 (Chính thống VN - gov.vn, tạp chí y học):** 47.46% (36,269 links)
* **Tầng 2 (Bệnh viện/Nhà thuốc uy tín VN):** 34.12% (26,070 links)
* **Tầng 3 (Học thuật Quốc tế - NCBI, PubMed):** 1.76% (1,342 links)
* **Tầng 4 (Tổ chức Y tế Quốc tế - WHO, CDC):** 4.97% (3,795 links)
* **Tầng 5 (Nguồn mở rộng khác):** 11.70% (8,939 links)

---

## 🔗 Cấu trúc Quan hệ & Tương thích OMOP CDM

Hệ thống định nghĩa chặt chẽ 8 loại quan hệ có hướng giữa các tập đỉnh, ngăn chặn việc sinh ra các mối liên kết không có cơ sở y khoa. Đồ thị này có khả năng ánh xạ trực tiếp vào các bảng của **Mô hình Dữ liệu Chung OMOP (CDM v5.3.1)**:

| Loại Đỉnh Nguồn | Quan hệ (Relation) | Loại Đỉnh Đích | Ánh xạ Bảng OMOP CDM |
| :--- | :--- | :--- | :--- |
| **Drug** | `TREATS` (Điều trị) | **Disease** | `drug_exposure` |
| **Intervention** | `PART_OF_TREATMENT` (Là một phần điều trị) | **Disease** | `procedure_occurrence` |
| **RiskFactor** | `INCREASES_RISK_OF` (Làm tăng nguy cơ) | **Disease** | `observation` |
| **Pathogen** | `CAUSES` (Gây ra) | **Disease** | `specimen` / `observation` |
| **Demographic** | `AFFECTS_POPULATION` (Ảnh hưởng dân số) | **Disease** | `concept` |
| **Disease** | `HAS_SYMPTOM` (Có triệu chứng) | **Symptom** | `observation` |
| **Disease** | `DIAGNOSED_BY` (Được chẩn đoán bằng) | **DiagnosticTest** | `measurement` |
| **Disease** | `HAS_COMPLICATION` (Có biến chứng) | **Complication** | `condition_occurrence` |

*(Lưu ý: Đỉnh `Disease` được quản lý gốc tại bảng `condition_occurrence` với trường `condition_source_value` là mã ICD-10).*

---

## 🕸️ Trực quan hóa Đồ thị

Định dạng xuất ra của PRIME-KG VN (các tệp `nodes.csv` và `edges.csv`) được cấu trúc hóa để có thể dễ dàng đọc hiểu bởi các thư viện phân tích đồ thị (NetworkX, igraph) hoặc nạp vào các hệ quản trị cơ sở dữ liệu đồ thị như **Neo4j** để truy vấn trực quan.

Dưới đây là một ví dụ minh họa khi trực quan hóa mã bệnh **A00.0 (Bệnh tả do Vibrio cholerae 01, típ sinh học cholerae)** cùng mạng lưới các thực thể lâm sàng bao quanh nó trên nền tảng Neo4j:

![Trực quan hóa Đồ thị Neo4j - Bệnh Tả (A00.0)](visualisation (2).png)

Thông qua mạng lưới này, từ một node trung tâm (Bệnh), có thể dễ dàng truy xuất ngược - xuôi để tìm các tập hợp thuốc điều trị, triệu chứng lâm sàng đặc trưng hoặc chẩn đoán phân biệt với các bệnh có chung tập triệu chứng.

---

## 📂 Cấu trúc Thư mục

* `icd10_danh_muc.csv`: Tệp chứa danh mục gốc mã bệnh ICD-10 (Dữ liệu đầu vào).
* `kg_output/`: Thư mục chứa toàn bộ kết quả cấu trúc Đồ thị Tri thức.
    * `edges.csv`: Tệp chứa hơn 71 nghìn liên kết, mô tả quan hệ chi tiết kèm `evidence` và `source_url`.
    * `nodes_*.csv`: Các tệp chứa định danh, loại và tên chuẩn hóa của từng tập đỉnh.
* `emd.py`: Script Python để thống kê, phân tích mật độ và kiểm tra vùng phủ (Gaps) của Đồ thị.

---

## 👥 Nhóm Tác giả & Nghiên cứu

Dự án này là kết quả nghiên cứu của nhóm phát triển tại **Trường Đại học An Giang, Đại học Quốc gia Thành phố Hồ Chí Minh**.

* **Tôn Thiện Tâm**
* **PGS.TS Đoàn Thanh Nghị**
* Cùng các cộng sự: Nguyễn Duy Khánh, Phan Minh Trung, Võ Ngọc Tường Vi.

**Tài trợ:** Nghiên cứu này được tài trợ bởi Ủy ban Nhân dân tỉnh Cà Mau, Sở Khoa học và Công nghệ tỉnh Cà Mau.
