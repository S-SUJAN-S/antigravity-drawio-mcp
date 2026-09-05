"""
Topological Graph Analyzer for Antigravity Draw.io MCP v2.0.
Analyzes .drawio diagrams to extract architectural metrics, root entry points,
sink outputs, cycles, bottlenecks, and critical execution paths for AI reasoning.
"""

from collections import defaultdict, deque
from .parser import DrawIOParser

class DiagramAnalyzer:
    @classmethod
    def analyze(cls, drawio_path):
        parser = DrawIOParser(drawio_path)
        parsed = parser.parse()

        if not parsed["pages"]:
            return {"error": f"No pages found in {drawio_path}"}

        page = parsed["pages"][0]
        nodes = page["nodes"]
        edges = page["edges"]

        node_dict = {n["id"]: n for n in nodes}
        all_node_ids = set(node_dict.keys())

        # Build adjacency graph
        adj = defaultdict(list)
        rev_adj = defaultdict(list)
        in_degree = {nid: 0 for nid in all_node_ids}
        out_degree = {nid: 0 for nid in all_node_ids}

        for e in edges:
            src = e.get("source")
            tgt = e.get("target")
            if src in all_node_ids and tgt in all_node_ids:
                adj[src].append(tgt)
                rev_adj[tgt].append(src)
                out_degree[src] += 1
                in_degree[tgt] += 1

        # Entry points (roots) and terminal outputs (sinks)
        roots = [nid for nid in all_node_ids if in_degree[nid] == 0 and out_degree[nid] > 0]
        sinks = [nid for nid in all_node_ids if out_degree[nid] == 0 and in_degree[nid] > 0]
        isolated = [nid for nid in all_node_ids if in_degree[nid] == 0 and out_degree[nid] == 0]

        # Cycle detection using DFS
        visited = {}
        cycles = []

        def dfs_cycle(u, path):
            visited[u] = 1
            path.append(u)
            for v in adj[u]:
                if visited.get(v) == 1:
                    # Found cycle
                    cycle_idx = path.index(v)
                    cycles.append(list(path[cycle_idx:] + [v]))
                elif v not in visited:
                    dfs_cycle(v, path)
            path.pop()
            visited[u] = 2

        for nid in sorted(all_node_ids):
            if nid not in visited:
                dfs_cycle(nid, [])

        # Critical path (longest path across DAG)
        longest_path = []
        if not cycles:
            memo_dist = {}
            memo_next = {}

            def get_longest(u):
                if u in memo_dist:
                    return memo_dist[u]
                if not adj[u]:
                    memo_dist[u] = 1
                    memo_next[u] = None
                    return 1

                max_d = 0
                best_nxt = None
                for v in adj[u]:
                    d = 1 + get_longest(v)
                    if d > max_d:
                        max_d = d
                        best_nxt = v

                memo_dist[u] = max_d
                memo_next[u] = best_nxt
                return max_d

            max_len = 0
            best_start = None
            for r in roots:
                d = get_longest(r)
                if d > max_len:
                    max_len = d
                    best_start = r

            curr = best_start
            while curr is not None:
                longest_path.append(curr)
                curr = memo_next.get(curr)

        # Potential architectural bottlenecks (highest total degree)
        degree_ranking = sorted(
            [{"id": nid, "label": node_dict[nid]["value"], "degree": in_degree[nid] + out_degree[nid]} for nid in all_node_ids],
            key=lambda x: x["degree"],
            reverse=True
        )

        return {
            "node_count": len(all_node_ids),
            "edge_count": len(edges),
            "root_entry_points": [{"id": r, "label": node_dict[r]["value"]} for r in roots],
            "terminal_sinks": [{"id": s, "label": node_dict[s]["value"]} for s in sinks],
            "isolated_components": [{"id": iso, "label": node_dict[iso]["value"]} for iso in isolated],
            "has_cycles": len(cycles) > 0,
            "detected_cycles": cycles[:5],
            "critical_longest_path": [{"id": p, "label": node_dict[p]["value"]} for p in longest_path],
            "top_bottlenecks": degree_ranking[:5]
        }
