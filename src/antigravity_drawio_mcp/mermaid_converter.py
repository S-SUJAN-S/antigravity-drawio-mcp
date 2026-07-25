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
        
        # Subgraph parsing regexes
        SUBGRAPH_BRACKET_RE = re.compile(
            r'^\s*subgraph\s+([\w\-]+)\s*\[\s*["\']?(.*?)["\']?\s*\]\s*$',
            re.IGNORECASE
        )
        SUBGRAPH_SIMPLE_RE = re.compile(
            r'^\s*subgraph\s+["\']?(.*?)["\']?\s*$',
            re.IGNORECASE
        )

        subgraph_stack = []
        all_subgraphs = []

        # Unified Arrow connector regex matching inline and pipe label variants
        ARROW_CONNECTOR_PATTERN = re.compile(
            r'\s*(?:(--|==|-\.)\s+([^-\s][^|]*?)\s+(-->|---|==>|\.->|->)|'
            r'(-->|---|==>|-\.->)\s*\|([^\|]+)\|'
            r'|(-->|---|==>|-\.->|->))\s*'
        )

        raw_edges = []
        all_node_ids = set()

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            if line_clean.startswith("graph") or line_clean.startswith("flowchart"):
                continue

            # Subgraph end block
            if line_clean.lower() == "end":
                if subgraph_stack:
                    subgraph_stack.pop()
                continue

            # Subgraph start block (bracket syntax: subgraph id [title])
            m_bracket = SUBGRAPH_BRACKET_RE.match(line_clean)
            if m_bracket:
                sub_id = m_bracket.group(1).strip()
                sub_title = m_bracket.group(2).strip() or sub_id
                parent_id = subgraph_stack[-1]["id"] if subgraph_stack else None
                sub_data = {
                    "id": sub_id,
                    "title": sub_title,
                    "nodes": [],
                    "parent_id": parent_id
                }
                subgraph_stack.append(sub_data)
                all_subgraphs.append(sub_data)
                continue

            # Subgraph start block (simple syntax: subgraph title or subgraph id)
            m_simple = SUBGRAPH_SIMPLE_RE.match(line_clean)
            if m_simple and not line_clean.lower().startswith(("graph", "flowchart", "direction")):
                raw_val = m_simple.group(1).strip()
                if raw_val:
                    sub_title = raw_val
                    if re.match(r'^[\w\-]+$', raw_val):
                        sub_id = raw_val
                    else:
                        sub_id = f"sub_{re.sub(r'\\W+', '_', raw_val)}"
                    parent_id = subgraph_stack[-1]["id"] if subgraph_stack else None
                    sub_data = {
                        "id": sub_id,
                        "title": sub_title,
                        "nodes": [],
                        "parent_id": parent_id
                    }
                    subgraph_stack.append(sub_data)
                    all_subgraphs.append(sub_data)
                    continue

            # Extract node shapes & labels
            # 1. Rhombus {Decision} -> rhombus;whiteSpace=wrap;html=1;
            for match in re.finditer(r'([\w\-]+)\s*\{"?(.*?)"?\}', line_clean):
                nid, nval = match.group(1), match.group(2).strip('"\'')
                node_labels[nid] = nval
                node_styles[nid] = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if subgraph_stack:
                    for active_sub in subgraph_stack:
                        if nid not in active_sub["nodes"]:
                            active_sub["nodes"].append(nid)

            # 2. Rounded (Label) -> rounded=1;whiteSpace=wrap;html=1;arcSize=30;
            for match in re.finditer(r'([\w\-]+)\s*\("?(.*?)"?\)', line_clean):
                nid, nval = match.group(1), match.group(2).strip('"\'')
                node_labels[nid] = nval
                node_styles[nid] = "rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if subgraph_stack:
                    for active_sub in subgraph_stack:
                        if nid not in active_sub["nodes"]:
                            active_sub["nodes"].append(nid)

            # 3. Rectangle [Label] -> rounded=0;whiteSpace=wrap;html=1;
            for match in re.finditer(r'([\w\-]+)\s*\["?(.*?)"?\]', line_clean):
                nid, nval = match.group(1), match.group(2).strip('"\'')
                node_labels[nid] = nval
                node_styles[nid] = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if subgraph_stack:
                    for active_sub in subgraph_stack:
                        if nid not in active_sub["nodes"]:
                            active_sub["nodes"].append(nid)

            # Strip node shape bracket annotations for clean edge parsing
            cleaned_line = re.sub(r'([\w\-]+)\s*(?:\[[^\]]*\]|\{[^\}]*\}|\([^\)]*\))', r'\1', line_clean)

            # Multi-hop arrow chain parsing on line
            matches = list(ARROW_CONNECTOR_PATTERN.finditer(cleaned_line))
            if matches:
                node_tokens = []
                last_end = 0
                labels = []

                for match in matches:
                    start, end = match.span()
                    token = cleaned_line[last_end:start].strip()
                    if token:
                        node_tokens.append(token)

                    if match.group(2):
                        lbl = match.group(2).strip()
                    elif match.group(5):
                        lbl = match.group(5).strip()
                    else:
                        lbl = ""
                    labels.append(lbl)

                    last_end = end

                final_token = cleaned_line[last_end:].strip()
                if final_token:
                    node_tokens.append(final_token)

                for i in range(len(node_tokens) - 1):
                    src = node_tokens[i]
                    tgt = node_tokens[i + 1]
                    lbl = labels[i] if i < len(labels) else ""

                    if re.match(r'^[\w\-]+$', src) and re.match(r'^[\w\-]+$', tgt):
                        raw_edges.append((src, tgt, lbl))
                        all_node_ids.add(src)
                        all_node_ids.add(tgt)
                        if subgraph_stack:
                            for active_sub in subgraph_stack:
                                if src not in active_sub["nodes"]:
                                    active_sub["nodes"].append(src)
                                if tgt not in active_sub["nodes"]:
                                    active_sub["nodes"].append(tgt)

        # Topological depth calculation for multi-column layout with cycle tolerance
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        preds = defaultdict(list)

        for nid in all_node_ids:
            in_degree[nid] = 0

        for src, tgt, _ in raw_edges:
            adj[src].append(tgt)
            preds[tgt].append(src)
            in_degree[tgt] += 1

        depths = {nid: 0 for nid in all_node_ids}
        visited = set()

        # Primary Kahn's BFS (Root nodes with in_degree == 0)
        queue = deque([nid for nid in sorted(all_node_ids) if in_degree[nid] == 0])
        for nid in queue:
            visited.add(nid)

        while queue:
            curr = queue.popleft()
            for nxt in adj[curr]:
                depths[nxt] = max(depths[nxt], depths[curr] + 1)
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0 and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        # Secondary Pass for Cyclic / Unvisited Nodes
        while len(visited) < len(all_node_ids):
            unvisited = [n for n in sorted(all_node_ids) if n not in visited]

            best_cand = None
            best_pred_depth = -1

            for u in unvisited:
                visited_preds = [p for p in preds[u] if p in visited]
                if visited_preds:
                    max_d = max(depths[p] for p in visited_preds)
                    if max_d > best_pred_depth:
                        best_pred_depth = max_d
                        best_cand = u

            if best_cand is None:
                best_cand = unvisited[0]
                depths[best_cand] = 0
            else:
                depths[best_cand] = best_pred_depth + 1

            visited.add(best_cand)
            sub_queue = deque([best_cand])

            while sub_queue:
                curr = sub_queue.popleft()
                for nxt in adj[curr]:
                    if nxt not in visited:
                        depths[nxt] = max(depths[nxt], depths[curr] + 1)
                        in_degree[nxt] -= 1
                        if in_degree[nxt] <= 0:
                            visited.add(nxt)
                            sub_queue.append(nxt)

        # Group nodes by depth column
        depth_columns = defaultdict(list)
        for nid in sorted(all_node_ids):
            d = depths[nid]
            depth_columns[d].append(nid)

        # Assign coordinates: x = 80 + depth * 250, y = 80 + row * 110
        node_coords = {}
        for col_idx in sorted(depth_columns.keys()):
            col_nodes = depth_columns[col_idx]
            x_pos = 80 + col_idx * 250
            for row_idx, nid in enumerate(col_nodes):
                y_pos = 80 + row_idx * 110
                node_coords[nid] = (x_pos, y_pos)

        # Build hierarchy and calculate subgraph bounding boxes bottom-up
        sub_by_id = {sub["id"]: sub for sub in all_subgraphs}
        children_of = defaultdict(list)
        for sub in all_subgraphs:
            pid = sub.get("parent_id")
            if pid and pid in sub_by_id:
                children_of[pid].append(sub["id"])

        sub_depths = {}
        def get_depth(sub_id, visited_depth=None):
            if visited_depth is None:
                visited_depth = set()
            if sub_id in sub_depths:
                return sub_depths[sub_id]
            if sub_id in visited_depth:
                return 0
            visited_depth.add(sub_id)
            pid = sub_by_id[sub_id].get("parent_id")
            if not pid or pid not in sub_by_id:
                d = 0
            else:
                d = get_depth(pid, visited_depth) + 1
            sub_depths[sub_id] = d
            return d

        for sub in all_subgraphs:
            get_depth(sub["id"])

        memo_bounds = {}
        def get_subgraph_bounds(sub_id, visited_bounds=None):
            if visited_bounds is None:
                visited_bounds = set()
            if sub_id in memo_bounds:
                return memo_bounds[sub_id]
            if sub_id in visited_bounds:
                return None
            visited_bounds.add(sub_id)

            sub = sub_by_id[sub_id]
            
            # Points from direct/child nodes of this subgraph
            valid_nodes = [nid for nid in sub["nodes"] if nid in node_coords]
            
            x_mins = []
            y_mins = []
            x_maxs = []
            y_maxs = []

            for nid in valid_nodes:
                nx, ny = node_coords[nid]
                x_mins.append(nx)
                y_mins.append(ny)
                x_maxs.append(nx + 140)
                y_maxs.append(ny + 60)

            # Points from child subgraphs
            for cid in children_of[sub_id]:
                cbounds = get_subgraph_bounds(cid, visited_bounds.copy())
                if cbounds:
                    cx, cy, cw, ch = cbounds
                    x_mins.append(cx)
                    y_mins.append(cy)
                    x_maxs.append(cx + cw)
                    y_maxs.append(cy + ch)

            if not x_mins:
                return None

            content_x_min = min(x_mins)
            content_y_min = min(y_mins)
            content_x_max = max(x_maxs)
            content_y_max = max(y_maxs)

            sub_x = content_x_min - 20
            sub_y = content_y_min - 35
            sub_w = (content_x_max - content_x_min) + 40
            sub_h = (content_y_max - content_y_min) + 45

            bounds = (sub_x, sub_y, sub_w, sub_h)
            memo_bounds[sub_id] = bounds
            return bounds

        for sub in all_subgraphs:
            get_subgraph_bounds(sub["id"])

        # Add Subgraph Container Cells FIRST (sorted top-down: outer parents first, inner children second)
        sorted_subgraphs = sorted(all_subgraphs, key=lambda s: sub_depths.get(s["id"], 0))

        for sub in sorted_subgraphs:
            bounds = memo_bounds.get(sub["id"])
            if not bounds:
                continue

            sub_x, sub_y, sub_w, sub_h = bounds

            subgraph_style = (
                "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;"
                "fillColor=#F8F9FA;strokeColor=#6C757D;strokeWidth=1.5;"
                "fontStyle=1;fontSize=12;startSize=25;horizontal=1;"
            )

            builder.add_node(
                sub["id"],
                sub["title"],
                sub_x,
                sub_y,
                width=sub_w,
                height=sub_h,
                style=subgraph_style
            )

        # Add Child Nodes SECOND
        for col_idx in sorted(depth_columns.keys()):
            col_nodes = depth_columns[col_idx]
            for nid in col_nodes:
                x_pos, y_pos = node_coords[nid]
                label = node_labels.get(nid, nid)
                style = node_styles.get(
                    nid,
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                )
                builder.add_node(nid, label, x_pos, y_pos, style=style)

        # Add Edges THIRD
        edge_count = 0
        for src, tgt, label in raw_edges:
            edge_count += 1
            builder.add_edge(f"e_{src}_{tgt}_{edge_count}", src, tgt, label=label)

        return builder.to_xml()
