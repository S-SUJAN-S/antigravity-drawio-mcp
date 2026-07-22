import re
from .builder import DrawIOBuilder

class MermaidToDrawIO:
    @staticmethod
    def convert(mermaid_code):
        builder = DrawIOBuilder(page_name="Mermaid Diagram")
        lines = [l.strip() for l in mermaid_code.strip().split("\n") if l.strip() and not l.strip().startswith("%%")]

        node_map = {}
        node_labels = {}
        y_cursor = 50
        x_cursor = 100

        # First pass: Extract explicit node labels like B[Load Balancer]
        for line in lines:
            for match in re.finditer(r'([\w\-]+)\["?(.*?)"?\]', line):
                nid, nval = match.groups()
                node_labels[nid] = nval

        # Second pass: Extract edge links
        for line in lines:
            if line.startswith("graph") or line.startswith("flowchart") or line.startswith("sequenceDiagram"):
                continue

            edge_match = re.search(r'([\w\-]+)(?:\[.*?\])?\s*(-->|---|==>|-\.->)\s*(?:\|([^\|]+)\|)?\s*([\w\-]+)(?:\[.*?\])?', line)
            if edge_match:
                src_id, arrow, label, tgt_id = edge_match.groups()

                if src_id not in node_map:
                    val = node_labels.get(src_id, src_id)
                    builder.add_node(src_id, val, x_cursor, y_cursor)
                    node_map[src_id] = (x_cursor, y_cursor)
                    y_cursor += 120

                if tgt_id not in node_map:
                    val = node_labels.get(tgt_id, tgt_id)
                    builder.add_node(tgt_id, val, x_cursor + 250, y_cursor - 120)
                    node_map[tgt_id] = (x_cursor + 250, y_cursor - 120)

                builder.add_edge(f"e_{src_id}_{tgt_id}", src_id, tgt_id, label=label or "")
            else:
                for nid, nval in node_labels.items():
                    if nid not in node_map:
                        builder.add_node(nid, nval, x_cursor, y_cursor)
                        node_map[nid] = (x_cursor, y_cursor)
                        y_cursor += 120

        return builder.to_xml()
