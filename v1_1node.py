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

def visualize_specific_node(edges_file: str, target_node_id: str, output_html: str):
    if not os.path.exists(edges_file):
        print(f"[!] Lỗi: Không tìm thấy file {edges_file}")
        return

    # 1. Đọc dữ liệu
    df = pd.read_csv(edges_file)

    # 2. Lọc đúng các cạnh liên quan đến target_node_id (Lọc 1-hop)
    filtered_edges = df[(df['x_id'] == target_node_id) | (df['y_id'] == target_node_id)].copy()

    if filtered_edges.empty:
        print(f"[-] Không tìm thấy dữ liệu hoặc liên kết nào cho node: {target_node_id}")
        return

    # 3. LIỆT KÊ ĐẦY ĐỦ RA TERMINAL
    print(f"\n=== DANH SÁCH THỰC THỂ LIÊN KẾT VỚI [{target_node_id}] ===")
    
    # Gom nhóm để in ra cho dễ nhìn
    entities_by_type = {}
    for _, row in filtered_edges.iterrows():
        # Xác định đâu là node cha (target), đâu là node con (child)
        if row['x_id'] == target_node_id:
            child_id, child_name, child_type = row['y_id'], row['y_name'], row['y_type']
            rel = row['display_relation']
        else:
            child_id, child_name, child_type = row['x_id'], row['x_name'], row['x_type']
            rel = row['display_relation']
            
        if child_type not in entities_by_type:
            entities_by_type[child_type] = []
        entities_by_type[child_type].append(f" - {child_name} ({rel})")

    for e_type, e_list in entities_by_type.items():
        print(f"\n📌 {e_type.upper()}:")
        # Xóa trùng lặp khi in
        for item in sorted(list(set(e_list))):
            print(item)
    print("========================================================\n")

    # 4. Xây dựng đồ thị NetworkX
    G = nx.DiGraph()
    
    for _, row in filtered_edges.iterrows():
        x_id, x_name, x_type = str(row['x_id']), str(row['x_name']), str(row.get('x_type', 'Unknown'))
        y_id, y_name, y_type = str(row['y_id']), str(row['y_name']), str(row.get('y_type', 'Unknown'))
        rel = str(row.get('display_relation', 'RELATED_TO'))

        # Tăng kích thước (size) cho node cha (target) để nó nổi bật giữa bản đồ
        x_size = 40 if x_id == target_node_id else 20
        y_size = 40 if y_id == target_node_id else 20

        if not G.has_node(x_id):
            G.add_node(x_id, label=x_name, title=f"[{x_type}] {x_name}", 
                       color=NODE_COLORS.get(x_type, NODE_COLORS["Unknown"]), 
                       size=x_size, font={"size": 16 if x_id == target_node_id else 12})
            
        if not G.has_node(y_id):
            G.add_node(y_id, label=y_name, title=f"[{y_type}] {y_name}", 
                       color=NODE_COLORS.get(y_type, NODE_COLORS["Unknown"]), 
                       size=y_size, font={"size": 16 if y_id == target_node_id else 12})

        G.add_edge(x_id, y_id, title=rel, label=rel, font={"size": 10, "align": "middle"})

    # 5. Render bằng PyVis
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.from_nx(G)
    
    # Cấu hình vật lý đẩy nhẹ nhàng hơn vì số lượng node giờ đã ít
    net.barnes_hut(gravity=-3000, central_gravity=0.1, spring_length=200)
    
    # Bật control menu để bạn có thể tự chỉnh physics ngay trên web nếu muốn
    net.show_buttons(filter_=['physics'])
    
    net.save_graph(output_html)
    print(f"[+] Đã xuất file HTML trực quan: {output_html}")
    print(f"[+] Mở file trên trình duyệt để xem rõ các node.")

if __name__ == "__main__":
    TARGET_ID = "A00" # Có thể thay đổi thành mã bệnh khác (VD: A01, A09)
    INPUT_EDGES = "edges.csv"
    OUTPUT_HTML = f"ego_graph_{TARGET_ID}.html"
    
    visualize_specific_node(INPUT_EDGES, TARGET_ID, OUTPUT_HTML)
