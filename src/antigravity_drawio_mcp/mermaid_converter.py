import re
from collections import defaultdict, deque
from .builder import DrawIOBuilder

class MermaidToDrawIO:
    @staticmethod
    def convert(mermaid_code):
        builder = DrawIOBuilder(page_name="Mermaid Diagram")
        lines = [l.strip() for l in mermaid_code.strip().split("\n") if l.strip() and not l.strip().startswith("%%")]

        node_labels = {}
        node_styles = {}
        subgraphs = []
        current_subgraph = None

        # Regex for node shapes: [label], {label}, (label)
        node_pattern = re.compile(r'([\w\-]+)(?:(\["?.*?"?\])|\({"?.*?"?\}\)|\(("?.*?"?\)))')
        
        # Parse lines for subgraphs, nodes, and edges
        raw_edges = []
        all_node_ids = set()

        for line in lines:
            if line.startswith("graph") or line.startswith("flowchart"):
                continue

            subgraph_match = re.match(r'subgraph\s+["\']?(.*?)["\']?$', line, re.IGNORECASE)
            if subgraph_match:
                title = subgraph_match.group(1) or "Group"
                current_subgraph = {"title": title, "nodes": []}
                subgraphs.append(current_subgraph)
                continue

            if line.lower() == "end":
                current_subgraph = None
                continue

            # Extract node shapes & labels
            # 1. Rhombus {Decision}
            for match in re.finditer(r'([\w\-]+)\{"?(.*?)"?\}', line):
                nid, nval = match.groups()
                node_labels[nid] = nval
                node_styles[nid] = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if current_subgraph:
                    current_subgraph["nodes"].append(nid)

            # 2. Rounded (Label)
            for match in re.finditer(r'([\w\-]+)\("?(.*?)"?\)', line):
                nid, nval = match.groups()
                node_labels[nid] = nval
                node_styles[nid] = "rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if current_subgraph:
                    current_subgraph["nodes"].append(nid)

            # 3. Rectangle [Label]
            for match in re.finditer(r'([\w\-]+)\["?(.*?)"?\]', line):
                nid, nval = match.groups()
                if nid not in node_styles:
                    node_labels[nid] = nval
                    node_styles[nid] = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if current_subgraph:
                    current_subgraph["nodes"].append(nid)

            # Extract all multi-hop edges on line (e.g. A --> B --> C)
            edge_pattern = re.compile(r'([\w\-]+)\s*(-->|---|==>|-\.->)\s*(?:\|([^\|]+)\|)?\s*([\w\-]+)')
            for match in edge_pattern.finditer(line):
                src, arrow, label, tgt = match.groups()
                raw_edges.append((src, tgt, label or ""))
                all_node_ids.add(src)
                all_node_ids.add(tgt)
                if current_subgraph:
                    if src not in current_subgraph["nodes"]:
                        current_subgraph["nodes"].append(src)
                    if tgt not in current_subgraph["nodes"]:
                        current_subgraph["nodes"].append(tgt)

        # Topological depth calculation for multi-column layout
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        for nid in all_node_ids:
            in_degree[nid] = 0

        for src, tgt, _ in raw_edges:
            adj[src].append(tgt)
            in_degree[tgt] += 1

        depths = {nid: 0 for nid in all_node_ids}
        queue = deque([nid for nid in all_node_ids if in_degree[nid] == 0])

        while queue:
            curr = queue.popleft()
            for nxt in adj[curr]:
                depths[nxt] = max(depths[nxt], depths[curr] + 1)
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        # Group nodes by depth column
        depth_columns = defaultdict(list)
        for nid, d in depths.items():
            depth_columns[d].append(nid)

        # Assign coordinates & add nodes to builder
        node_coords = {}
        for col_idx, col_nodes in depth_columns.items():
            x_pos = 100 + col_idx * 260
            y_start = 80
            for row_idx, nid in enumerate(col_nodes):
                y_pos = y_start + row_idx * 110
                label = node_labels.get(nid, nid)
                style = node_styles.get(nid, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;")
                builder.add_node(nid, label, x_pos, y_pos, style=style)
                node_coords[nid] = (x_pos, y_pos)

        # Add edges
        edge_count = 0
        for src, tgt, label in raw_edges:
            edge_count += 1
            builder.add_edge(f"e_{src}_{tgt}_{edge_count}", src, tgt, label=label)

        return builder.to_xml()
