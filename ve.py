#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import networkx as nx
from pyvis.network import Network

# Cấu hình màu sắc cho từng phân nhóm lâm sàng để dễ phân biệt
NODE_COLORS = {
    "Disease": "#E74C3C",        # Đỏ
    "Drug": "#3498DB",          # Xanh dương
    "Symptom": "#F1C40F",       # Vàng
    "DiagnosticTest": "#9B59B6", # Tím
    "Complication": "#E67E22",   # Cam
    "RiskFactor": "#34495E",    # Xám đậm
    "Demographic": "#1ABC9C",   # Xanh ngọc
    "Intervention": "#2ECC71",  # Xanh lá
    "Pathogen": "#7F8C8D"       # Xám nhạt
}

def build_interactive_graph(edges_file: str, output_html: str):
    print(f"[*] Đang đọc dữ liệu từ: {edges_file}")
    if not os.path.exists(edges_file):
        print("[!] Không tìm thấy file edges.csv. Vui lòng kiểm tra lại đường dẫn.")
        return

    # Đọc file cạnh
    df_edges = pd.read_csv(edges_file)
    
    # Giới hạn số lượng cạnh để tránh treo trình duyệt nếu đồ thị quá lớn (tuỳ chỉnh theo nhu cầu)
    MAX_EDGES = 2000 
    if len(df_edges) > MAX_EDGES:
        print(f"[*] Đồ thị có {len(df_edges)} cạnh. Giới hạn hiển thị {MAX_EDGES} cạnh ngẫu nhiên để tối ưu.")
        df_edges = df_edges.sample(MAX_EDGES, random_state=42)

    # Khởi tạo đồ thị có hướng bằng NetworkX
    G = nx.DiGraph()

    print("[*] Đang xây dựng cấu trúc node và edge...")
    for _, row in df_edges.iterrows():
        # Lấy thông tin Node X (Source)
        x_id = str(row.get('x_id', ''))
        x_name = str(row.get('x_name', x_id))
        x_type = str(row.get('x_type', 'Unknown'))
        
        # Lấy thông tin Node Y (Target)
        y_id = str(row.get('y_id', ''))
        y_name = str(row.get('y_name', y_id))
        y_type = str(row.get('y_type', 'Unknown'))
        
        # Quan hệ
        relation = str(row.get('relation', 'RELATED_TO'))
        display_rel = str(row.get('display_relation', relation))

        # Thêm Node X vào đồ thị
        if not G.has_node(x_id):
            G.add_node(x_id, 
                       label=x_name, 
                       title=f"Type: {x_type}\nID: {x_id}", 
                       color=NODE_COLORS.get(x_type, "#BDC3C7"),
                       group=x_type)

        # Thêm Node Y vào đồ thị
        if not G.has_node(y_id):
            G.add_node(y_id, 
                       label=y_name, 
                       title=f"Type: {y_type}\nID: {y_id}", 
                       color=NODE_COLORS.get(y_type, "#BDC3C7"),
                       group=y_type)

        # Thêm Cạnh vào đồ thị
        G.add_edge(x_id, y_id, title=display_rel, label=relation)

    print(f"[*] Đã tải xong: {G.number_of_nodes()} nodes và {G.number_of_edges()} edges.")

    # Sử dụng PyVis để render đồ thị NetworkX
    print("[*] Đang khởi tạo bản đồ HTML tương tác...")
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    
    # Cấu hình physics để các node đẩy nhau ra, giảm thiểu đè chéo
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150)
    
    # Tích hợp dữ liệu từ NetworkX sang PyVis
    net.from_nx(G)

    # Tạo menu filter động (Cho phép người dùng chọn lọc node theo type)
    net.show_buttons(filter_=['physics'])

    # Lưu ra HTML
    net.save_graph(output_html)
    print(f"[+] Đã xuất file thành công: {output_html}")
    print("    -> Bạn có thể mở file này bằng trình duyệt (Chrome/Firefox/Edge) để xem tương tác.")

if __name__ == "__main__":
    # Nguồn cấp vào là edges.csv hoặc kg.csv (chứa toàn bộ map quan hệ)
    INPUT_EDGES_CSV = "edges.csv"  
    OUTPUT_HTML = "medical_kg_visualization.html"
    
    build_interactive_graph(INPUT_EDGES_CSV, OUTPUT_HTML)
