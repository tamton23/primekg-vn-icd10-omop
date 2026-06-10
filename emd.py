#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import pandas as pd
import csv

# ==================== CẤU HÌNH ĐƯỜNG DẪN ====================
OUTPUT_DIR = ""  # Để trống nếu chạy cùng thư mục với các file CSV
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.csv")
ICD10_CSV_PATH = "./icd10_danh_muc.csv"

# Các nhóm nguồn tham khảo trích xuất từ DOMAIN_TIERS
DOMAIN_TIERS = {
    "Tầng 1 (Chính thống VN)": ["gov.vn", "tapchiyhocduphong.vn", "vjmed.org.vn", "vjid.vn", "yhth.vn"],
    "Tầng 2 (Bệnh viện/Nhà thuốc VN)": ["nhathuoclongchau", "pharmacity", "vinmec", "medlatec", "tamanhhospital", "hongngochospital"],
    "Tầng 3 (Học thuật Quốc tế)": ["ncbi", "pubmed", "jamanetwork", "nejm", "thelancet"],
    "Tầng 4 (Tổ chức Y tế QT)": ["cdc.gov", "who.int", "nih.gov", "msdmanuals", "mayoclinic", "clevelandclinic", "hopkinsmedicine", "nhs.uk"]
}

def analyze_kg():
    print("="*70)
    print(" BÁO CÁO THỐNG KÊ TOÀN DIỆN MẠNG LƯỚI TRI THỨC Y KHOA (PRIME-KG)")
    print("="*70)

    if not os.path.exists(EDGES_FILE):
        print(f"[!] Không tìm thấy file {EDGES_FILE}. Hãy đảm bảo bạn đã chạy module cào dữ liệu thành công.")
        return

    # =========================================================================
    # 1. ĐỌC DỮ LIỆU ĐỒ THỊ (EDGES)
    # =========================================================================
    df_edges = pd.read_csv(EDGES_FILE, dtype=str)
    
    x_nodes = df_edges[['x_id', 'x_type']].rename(columns={'x_id': 'id', 'x_type': 'type'})
    y_nodes = df_edges[['y_id', 'y_type']].rename(columns={'y_id': 'id', 'y_type': 'type'})
    df_nodes = pd.concat([x_nodes, y_nodes]).dropna().drop_duplicates(subset=['id'])
    
    total_edges = len(df_edges)
    total_nodes = len(df_nodes)
    
    print("\n[1] KÍCH THƯỚC ĐỒ THỊ (GRAPH SIZE):")
    print(f"  - Tổng số Cạnh (Edges): {total_edges:,}")
    print(f"  - Tổng số Đỉnh (Nodes): {total_nodes:,}")

    # =========================================================================
    # 2. PHÂN BỐ NODE
    # =========================================================================
    print("\n[2] PHÂN BỐ SỐ NODE & TỶ LỆ (%):")
    node_counts = df_nodes['type'].value_counts()
    for ntype, count in node_counts.items():
        pct = (count / total_nodes) * 100
        print(f"  - {ntype:15}: {count:<6,} nodes ({pct:5.2f}%)")
    
    scanned_disease_nodes = df_nodes[df_nodes['type'] == 'Disease']['id'].dropna().astype(str)
    scanned_disease_ids = set(scanned_disease_nodes.apply(lambda x: x.strip().upper()))
    total_diseases = len(scanned_disease_ids)

    # =========================================================================
    # 3. THỐNG KÊ NGUỒN THAM KHẢO
    # =========================================================================
    print("\n[3] THỐNG KÊ NGUỒN THAM KHẢO THEO TẦNG (%):")
    if 'source_url' in df_edges.columns:
        urls = df_edges['source_url'].dropna()
        
        def categorize_domain(url):
            url_str = str(url).lower()
            for tier_name, domains in DOMAIN_TIERS.items():
                if any(d in url_str for d in domains):
                    return tier_name
            return "Tầng 5 (Nguồn tự do/Khác)"
            
        tier_counts = urls.apply(categorize_domain).value_counts()
        total_urls = len(urls)
        
        for tier, count in tier_counts.items():
            pct = (count / total_urls) * 100
            print(f"  - {tier:30}: {count:<6,} links ({pct:5.2f}%)")
    else:
        print("  [!] Không tìm thấy cột 'source_url'.")

    # =========================================================================
    # 4. ĐỘ TOÀN VẸN & MẬT ĐỘ (DENSITY)
    # =========================================================================
    print("\n[4] ĐỘ TOÀN VẸN CỦA ĐỒ THỊ (GRAPH DENSITY):")
    if total_diseases > 0:
        avg_degree = total_edges / total_diseases
        print(f"  - Mật độ cạnh trung bình: {avg_degree:.2f} liên kết / 1 Bệnh")
        print("  - Phân tích độ \"dày\" trung bình cho 1 Bệnh:")
        
        for ntype in ['Drug', 'Symptom', 'Complication', 'DiagnosticTest', 'RiskFactor', 'Demographic', 'Intervention', 'Pathogen']:
            type_edges = df_edges[(df_edges['x_type'] == ntype) | (df_edges['y_type'] == ntype)]
            avg_per_disease = len(type_edges) / total_diseases
            print(f"      + Có {avg_per_disease:4.1f} {ntype} / 1 Bệnh")
    else:
        print("  [!] Chưa có node Disease nào để đo mật độ.")

    # =========================================================================
    # 5. TỶ LỆ PHỦ SÓNG & LẤY DANH SÁCH GỐC (DỰA VÀO QUÉT THỰC TẾ)
    # =========================================================================
    valid_codes_list = []
    
    print("\n[5] TỶ LỆ PHỦ SÓNG ICD-10 (COVERAGE):")
    if os.path.exists(ICD10_CSV_PATH):
        try:
            with open(ICD10_CSV_PATH, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            # Đọc trực tiếp từ dòng số 4 trở đi (Bỏ qua 4 dòng header của file Excel)
            for i in range(4, len(rows)):
                if len(rows[i]) > 17:
                    c = str(rows[i][17]).strip().upper() # Cột 17 là cột chứa Mã Bệnh
                    if c != "":
                        # Quét và làm sạch mã: CHỈ GIỮ LẠI Chữ, Số, Dấu chấm (.), Dấu sao (*), Dấu cộng (+)
                        clean_code = re.sub(r'[^\w\.\*\+]', '', c)
                        
                        # Xử lý mã dính đúp (VD: A23.0*A23.0* -> A23.0*)
                        clean_code = re.sub(r'^([A-Z]\d{2}(?:\.\d+)?[\*\+]?)\1$', r'\1', clean_code)
                        
                        # Nếu đúng chuẩn mã bệnh (Cho phép chứa đuôi * hoặc +) thì nạp vào danh sách
                        if re.match(r'^[A-Z]\d{2}(?:\.\d+)?[\*\+]?$', clean_code):
                            valid_codes_list.append(clean_code)
            
            # Khử trùng lặp và đếm số lượng thực tế lấy được từ file
            valid_codes_list = sorted(list(set(valid_codes_list)))
            total_danh_muc_goc = len(valid_codes_list)
            
            coverage_pct = (total_diseases / total_danh_muc_goc) * 100 if total_danh_muc_goc > 0 else 0
            print(f"  - Tổng số Bệnh ĐÃ CÀO VÀ NỐI LƯỚI   : {total_diseases:,}")
            print(f"  - Tổng số Bệnh TRONG DANH MỤC GỐC  : {total_danh_muc_goc:,}")
            print(f"  => Tiến độ bao phủ hệ thống        : {coverage_pct:.2f}%")
            
        except Exception as e:
            print(f"  [!] Lỗi khi phân tích ICD-10: {e}")
    else:
        print(f"  [!] Không tìm thấy file {ICD10_CSV_PATH} để đối chiếu độ phủ.")
        
    # =========================================================================
    # 6. PHÂN TÍCH VÙNG QUÉT VÀ CÁC ĐIỂM TRỐNG (GAPS) - LỌC THEO SOURCE URL
    # =========================================================================
    print("\n[6] PHÂN TÍCH VÙNG QUÉT & CÁC ĐIỂM TRỐNG (GAPS):")
    if not valid_codes_list:
        print("  [!] Không có danh mục gốc hợp lệ để đối chiếu điểm trống.")
    else:
        valid_codes_set = set(valid_codes_list)
        
        # --- LỌC NHIỄU: CHỈ LẤY CÁC BỆNH CÓ NGUỒN LÀ LINK WEBSITE (HTTP) ---
        # Tìm các mã bệnh ở cột x có x_source là link (bỏ qua 'ICD-10 Guidelines')
        real_x = df_edges[
            (df_edges['x_type'] == 'Disease') & 
            (df_edges['x_source'].astype(str).str.strip().str.startswith('http', na=False))
        ]['x_id']
        
        # Tìm các mã bệnh ở cột y có y_source là link
        real_y = df_edges[
            (df_edges['y_type'] == 'Disease') & 
            (df_edges['y_source'].astype(str).str.strip().str.startswith('http', na=False))
        ]['y_id']
        
        # Gộp tất cả các bệnh thực tế cào được từ web
        real_scanned_diseases = set(real_x).union(set(real_y))
        
        # Đối chiếu với danh mục gốc để ra danh sách ID sạch
        clean_scanned_ids = [str(c).strip().upper() for c in real_scanned_diseases if str(c).strip().upper() in valid_codes_set]
        
        if not clean_scanned_ids:
            print("  [!] Không tìm thấy mã bệnh nào thực sự được cào từ website (nguồn http).")
            return

        # Xác định điểm đầu - cuối dựa trên danh sách đã lọc sạch
        sorted_scanned = sorted(clean_scanned_ids)
        first_scanned = sorted_scanned[0]
        last_scanned = sorted_scanned[-1]
        
        print(f"  - Phạm vi đang quét (Đã lọc nguồn URL thực tế): Từ mã {first_scanned} đến mã {last_scanned}")
        
        # Lọc ra các mã MONG ĐỢI nằm trong vùng quét
        expected_in_range = [code for code in valid_codes_list if first_scanned <= code <= last_scanned]
        
        # Tìm các mã bị "trống" (có trong danh mục nhưng tool chưa cào được web nào)
        missing_codes = [code for code in expected_in_range if code not in clean_scanned_ids]
        
        total_expected = len(expected_in_range)
        total_missing = len(missing_codes)
        total_scanned_in_range = total_expected - total_missing
        
        print(f"  - Tổng số mã ICD-10 lâm sàng nằm trong vùng này     : {total_expected:,}")
        print(f"  - Số mã đã cào web thành công                       : {total_scanned_in_range:,}")
        print(f"  - Số mã bị TRỐNG (chưa cào được bài viết nào)       : {total_missing:,}")
        
        if total_missing > 0:
            error_rate = (total_missing / total_expected) * 100
            print(f"  => Tỷ lệ sót/lỗi trong vùng đang quét               : {error_rate:.2f}%")
            
            sample_missing = ", ".join(missing_codes[:20])
            if total_missing > 20:
                sample_missing += " ..."
            print(f"  - Danh sách điểm trống minh họa: {sample_missing}")
        else:
            print("  => Tuyệt vời! Bạn đã cào phủ kín 100% các mã trong phạm vi này.")
    print("="*70)

if __name__ == "__main__":
    analyze_kg()
