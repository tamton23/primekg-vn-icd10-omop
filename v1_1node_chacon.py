#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Bảng màu chuẩn OMOP
NODE_COLORS = {
    "Disease": "#E74C3C", "Drug": "#3498DB", "Symptom": "#F1C40F",
    "DiagnosticTest": "#9B59B6", "Complication": "#E67E22",
    "RiskFactor": "#34495E", "Demographic": "#1ABC9C",
    "Intervention": "#2ECC71", "Pathogen": "#7F8C8D",
    "Unknown": "#BDC3C7"
}

def visualize_disease_family(edges_file: str, base_disease_id: str, output_html: str):
    if not os.path.exists(edges_file):
        print(f"[!] Lỗi: Không tìm thấy file {edges_file}")
        return

    # 1. Đọc dữ liệu và DỌN DẸP KHOẢNG TRẮNG TÀNG HÌNH (Quan trọng nhất)
    df = pd.read_csv(edges_file)
    df['x_id'] = df['x_id'].astype(str).str.strip()
    df['y_id'] = df['y_id'].astype(str).str.strip()

    # 2. Lọc theo cụm họ bệnh (Lấy trọn A00, A00.0, A00.1, A00.9...)
    is_target_x = df['x_id'].str.startswith(base_disease_id)
    is_target_y = df['y_id'].str.startswith(base_disease_id)
    filtered_edges = df[is_target_x | is_target_y].copy()

    if filtered_edges.empty:
        print(f"[-] Không tìm thấy dữ liệu nào cho họ bệnh: {base_disease_id}")
        return

    print(f"\n[*] Đã tìm thấy {len(filtered_edges)} liên kết cho họ bệnh {base_disease_id}. Đang vẽ đồ thị...")

    # 3. Xây dựng đồ thị bằng NetworkX (Để giữ layout đẹp như ảnh của bạn)
    G = nx.DiGraph()
    
    for _, row in filtered_edges.iterrows():
        x_id, x_name, x_type = str(row['x_id']), str(row['x_name']), str(row.get('x_type', 'Unknown'))
        y_id, y_name, y_type = str(row['y_id']), str(row['y_name']), str(row.get('y_type', 'Unknown'))
        rel = str(row.get('display_relation', 'RELATED_TO'))

        # Phân biệt node cha/con trong họ bệnh để làm nổi bật
        x_is_core = x_id.startswith(base_disease_id)
        y_is_core = y_id.startswith(base_disease_id)
        
        x_size = 40 if x_is_core else 20
        y_size = 40 if y_is_core else 20

        if not G.has_node(x_id):
            G.add_node(x_id, label=f"[{x_id}] {x_name}" if x_is_core else x_name, 
                       title=f"Type: {x_type}\nID: {x_id}", 
                       color=NODE_COLORS.get(x_type, NODE_COLORS["Unknown"]), 
                       size=x_size, font={"size": 16 if x_is_core else 12})
            
        if not G.has_node(y_id):
            G.add_node(y_id, label=f"[{y_id}] {y_name}" if y_is_core else y_name, 
                       title=f"Type: {y_type}\nID: {y_id}", 
                       color=NODE_COLORS.get(y_type, NODE_COLORS["Unknown"]), 
                       size=y_size, font={"size": 16 if y_is_core else 12})

        # Add cạnh với font align middle để hiện text trên đường mũi tên
        G.add_edge(x_id, y_id, title=rel, label=rel, font={"size": 10, "align": "middle"})

    # 4. Render bằng PyVis
    net = Network(height="95vh", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.from_nx(G)
    
    # Giữ nguyên cấu hình vật lý đẩy nhẹ nhàng
    net.barnes_hut(gravity=-3000, central_gravity=0.1, spring_length=200)
    net.show_buttons(filter_=['physics'])
    
    net.save_graph(output_html)
    print(f"[+] Đã xuất file HTML trực quan: {output_html}")
    print("[+] Mở file trên trình duyệt để kiểm tra nhé!")

if __name__ == "__main__":
    TARGET_FAMILY = "A00" 
    INPUT_EDGES = "edges.csv"
    OUTPUT_HTML = f"ego_graph_{TARGET_FAMILY}_family.html"
    
    visualize_disease_family(INPUT_EDGES, TARGET_FAMILY, OUTPUT_HTML)
