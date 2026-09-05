import math
from collections import defaultdict, deque

class HierarchicalLayout:
    """
    Sugiyama-style layered directed graph layout algorithm.
    Computes aesthetic, collision-free (x, y) coordinates for nodes and containers.
    Supports layout directions: 'TB' (top-to-bottom), 'LR' (left-to-right), 'BT', 'RL'.
    Includes container-awareness to ensure adequate breathing room between external
    nodes and container boundaries.
    """
    def __init__(self, direction="TB", rank_sep=140.0, node_sep=80.0, margin_x=80.0, margin_y=80.0):
        self.direction = direction.upper()
        self.rank_sep = float(rank_sep)
        self.node_sep = float(node_sep)
        self.margin_x = float(margin_x)
        self.margin_y = float(margin_y)

    def layout(self, nodes, edges):
        """
        Takes a list of node dicts [{'id': 'n1', 'width': 140, 'height': 60, ...}]
        and edge dicts [{'source': 'n1', 'target': 'n2', ...}].
        Returns a dict: {node_id: {'x': float, 'y': float, 'width': float, 'height': float}}
        """
        if not nodes:
            return {}

        node_dict = {n["id"]: {
            "id": n["id"],
            "width": float(n.get("width", 150.0)),
            "height": float(n.get("height", 65.0)),
            "group": n.get("group")
        } for n in nodes}

        node_ids = set(node_dict.keys())
        valid_edges = [
            (e["source"], e["target"]) for e in edges
            if e.get("source") in node_ids and e.get("target") in node_ids and e.get("source") != e.get("target")
        ]

        # 1. Cycle breaking using DFS
        adj = defaultdict(list)
        for u, v in valid_edges:
            adj[u].append(v)

        visited = {}
        acyclic_edges = []
        for nid in sorted(node_ids):
            if nid not in visited:
                self._dfs_remove_cycles(nid, adj, visited, acyclic_edges)

        # 2. Layer Assignment (Longest Path Ranking)
        dag_adj = defaultdict(list)
        dag_in_degree = {nid: 0 for nid in node_ids}
        for u, v in acyclic_edges:
            dag_adj[u].append(v)
            dag_in_degree[v] += 1

        layers = {nid: 0 for nid in node_ids}
        queue = deque([nid for nid, deg in dag_in_degree.items() if deg == 0])

        while queue:
            curr = queue.popleft()
            for nxt in dag_adj[curr]:
                layers[nxt] = max(layers[nxt], layers[curr] + 1)
                dag_in_degree[nxt] -= 1
                if dag_in_degree[nxt] == 0:
                    queue.append(nxt)

        # Group nodes by layer
        layer_nodes = defaultdict(list)
        for nid, lyr in layers.items():
            layer_nodes[lyr].append(nid)

        # 3. Crossing Reduction (Barycenter Ordering)
        preds = defaultdict(list)
        for u, v in acyclic_edges:
            preds[v].append(u)

        max_layer = max(layer_nodes.keys()) if layer_nodes else 0
        for lyr in range(1, max_layer + 1):
            curr_nodes = layer_nodes[lyr]
            prev_positions = {nid: idx for idx, nid in enumerate(layer_nodes[lyr - 1])}

            def barycenter(n):
                pred_indices = [prev_positions[p] for p in preds[n] if p in prev_positions]
                if not pred_indices:
                    return 0.0
                return sum(pred_indices) / len(pred_indices)

            layer_nodes[lyr] = sorted(curr_nodes, key=barycenter)

        # 4. Coordinate Assignment with Predecessor Alignment, Symmetrical Centering & Container Clearance
        coords = {}

        layer_widths = {}
        for lyr, nids in layer_nodes.items():
            layer_widths[lyr] = sum(node_dict[nid]["width"] for nid in nids) + max(0, len(nids) - 1) * self.node_sep
        max_layer_width = max(layer_widths.values()) if layer_widths else 0.0

        if self.direction in ["TB", "BT"]:
            curr_y = self.margin_y
            layer_range = range(max_layer + 1) if self.direction == "TB" else range(max_layer, -1, -1)

            prev_had_group = False
            for lyr in layer_range:
                nodes_in_layer = layer_nodes[lyr]
                layer_height = max((node_dict[nid]["height"] for nid in nodes_in_layer), default=65.0)

                # Check if layer starts a container boundary - add extra vertical clearance
                current_has_group = any(node_dict[nid].get("group") for nid in nodes_in_layer)
                if current_has_group and not prev_had_group and lyr > 0:
                    curr_y += 40.0  # Container header clearance
                prev_had_group = current_has_group

                # Compute target X for each node in this layer based on placed predecessors
                target_xs = {}
                default_start_x = self.margin_x + (max_layer_width - layer_widths.get(lyr, 0.0)) / 2.0
                cur_def_x = default_start_x

                for nid in nodes_in_layer:
                    nw = node_dict[nid]["width"]
                    pred_placed = [coords[p] for p in preds[nid] if p in coords]
                    if pred_placed:
                        avg_pred_center = sum(p["x"] + p["width"] / 2.0 for p in pred_placed) / len(pred_placed)
                        target_xs[nid] = avg_pred_center - nw / 2.0
                    else:
                        target_xs[nid] = cur_def_x
                    cur_def_x += nw + self.node_sep

                # Resolve overlaps from left to right, maintaining at least node_sep spacing
                placed_xs = {}
                prev_right = None
                for nid in nodes_in_layer:
                    nw = node_dict[nid]["width"]
                    desired_x = target_xs[nid]
                    if prev_right is not None:
                        actual_x = max(desired_x, prev_right + self.node_sep)
                    else:
                        actual_x = desired_x
                    placed_xs[nid] = actual_x
                    prev_right = actual_x + nw

                for nid in nodes_in_layer:
                    nw = node_dict[nid]["width"]
                    nh = node_dict[nid]["height"]
                    y_offset = (layer_height - nh) / 2.0
                    coords[nid] = {
                        "x": round(placed_xs[nid], 1),
                        "y": round(curr_y + y_offset, 1),
                        "width": nw,
                        "height": nh
                    }

                curr_y += layer_height + self.rank_sep

        else:
            # LR: X is layer rank, Y is within-layer position
            layer_heights = {}
            for lyr, nids in layer_nodes.items():
                layer_heights[lyr] = sum(node_dict[nid]["height"] for nid in nids) + max(0, len(nids) - 1) * self.node_sep
            max_layer_height = max(layer_heights.values()) if layer_heights else 0.0

            curr_x = self.margin_x
            layer_range = range(max_layer + 1) if self.direction == "LR" else range(max_layer, -1, -1)

            prev_had_group = False
            for lyr in layer_range:
                nodes_in_layer = layer_nodes[lyr]
                layer_width = max((node_dict[nid]["width"] for nid in nodes_in_layer), default=150.0)

                current_has_group = any(node_dict[nid].get("group") for nid in nodes_in_layer)
                if current_has_group and not prev_had_group and lyr > 0:
                    curr_x += 40.0
                prev_had_group = current_has_group

                # Compute target Y for each node in this layer based on placed predecessors
                target_ys = {}
                default_start_y = self.margin_y + (max_layer_height - layer_heights.get(lyr, 0.0)) / 2.0
                cur_def_y = default_start_y

                for nid in nodes_in_layer:
                    nh = node_dict[nid]["height"]
                    pred_placed = [coords[p] for p in preds[nid] if p in coords]
                    if pred_placed:
                        avg_pred_center = sum(p["y"] + p["height"] / 2.0 for p in pred_placed) / len(pred_placed)
                        target_ys[nid] = avg_pred_center - nh / 2.0
                    else:
                        target_ys[nid] = cur_def_y
                    cur_def_y += nh + self.node_sep

                placed_ys = {}
                prev_bottom = None
                for nid in nodes_in_layer:
                    nh = node_dict[nid]["height"]
                    desired_y = target_ys[nid]
                    if prev_bottom is not None:
                        actual_y = max(desired_y, prev_bottom + self.node_sep)
                    else:
                        actual_y = desired_y
                    placed_ys[nid] = actual_y
                    prev_bottom = actual_y + nh

                for nid in nodes_in_layer:
                    nw = node_dict[nid]["width"]
                    nh = node_dict[nid]["height"]
                    x_offset = (layer_width - nw) / 2.0
                    coords[nid] = {
                        "x": round(curr_x + x_offset, 1),
                        "y": round(placed_ys[nid], 1),
                        "width": nw,
                        "height": nh
                    }

                curr_x += layer_width + self.rank_sep

        return coords

    def _dfs_remove_cycles(self, u, adj, visited, acyclic_edges):
        visited[u] = 1
        for v in adj[u]:
            if visited.get(v) == 1:
                continue
            elif v not in visited:
                acyclic_edges.append((u, v))
                self._dfs_remove_cycles(v, adj, visited, acyclic_edges)
            else:
                acyclic_edges.append((u, v))
        visited[u] = 2


class GridLayout:
    def __init__(self, columns=None, spacing_x=80.0, spacing_y=60.0, margin_x=80.0, margin_y=80.0):
        self.columns = columns
        self.spacing_x = float(spacing_x)
        self.spacing_y = float(spacing_y)
        self.margin_x = float(margin_x)
        self.margin_y = float(margin_y)

    def layout(self, nodes):
        if not nodes:
            return {}

        n_count = len(nodes)
        cols = self.columns or max(1, math.ceil(math.sqrt(n_count)))
        coords = {}

        for idx, n in enumerate(nodes):
            nid = n["id"]
            nw = float(n.get("width", 150.0))
            nh = float(n.get("height", 65.0))

            row = idx // cols
            col = idx % cols

            x = self.margin_x + col * (nw + self.spacing_x)
            y = self.margin_y + row * (nh + self.spacing_y)

            coords[nid] = {
                "x": round(x, 1),
                "y": round(y, 1),
                "width": nw,
                "height": nh
            }

        return coords


class ContainerBoundaryCalculator:
    """
    Computes generous enclosing bounding box for grouping containers/swimlanes
    based on child node coordinates with header bar and padding.
    """
    @staticmethod
    def compute_bounds(child_coords, padding=40.0, header_height=32.0, min_width=320.0):
        if not child_coords:
            return None

        x_min = min(c["x"] for c in child_coords)
        y_min = min(c["y"] for c in child_coords)
        x_max = max(c["x"] + c["width"] for c in child_coords)
        y_max = max(c["y"] + c["height"] for c in child_coords)

        w_content = x_max - x_min
        center_x = (x_min + x_max) / 2.0
        target_w = max(w_content + 2 * padding, float(min_width))
        start_x = center_x - target_w / 2.0

        return {
            "x": round(start_x, 1),
            "y": round(y_min - padding - header_height, 1),
            "width": round(target_w, 1),
            "height": round((y_max - y_min) + 2 * padding + header_height, 1)
        }
