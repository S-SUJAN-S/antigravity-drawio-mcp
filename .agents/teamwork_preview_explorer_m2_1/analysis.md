# Analysis Report: Milestone 2 - R3 Mermaid Node Shapes & Multi-Hop Parsing

**Target File**: `src/antigravity_drawio_mcp/mermaid_converter.py`  
**Author**: teamwork_preview_explorer_m2_1  
**Date**: 2026-07-25  
**Mode**: Read-Only Technical Investigation  

---

## 1. Executive Summary

An in-depth read-only audit of `src/antigravity_drawio_mcp/mermaid_converter.py` was conducted to evaluate the implementation requirements for **Milestone 2 - R3**:
1. **Node shape syntax support**:
   - `{label}` -> rhombus/decision style (`rhombus;whiteSpace=wrap;html=1;`)
   - `(label)` -> rounded style (`rounded=1;whiteSpace=wrap;html=1;`)
   - `[label]` -> rectangular style (`rounded=0;whiteSpace=wrap;html=1;`)
2. **Multi-hop arrow chain parsing on a single line**:
   - Extract nodes `A`, `B`, `C` and create edges `A->B` and `B->C` for syntax like `A --> B --> C` or `A -- text --> B --> C`.

### Primary Audit Discoveries:
1. **Node Shape Style Defect**: In lines 58–62 of `mermaid_converter.py`, rectangular syntax `[label]` currently assigns `rounded=1;` instead of `rounded=0;` as required by the specification. In addition, line 17 defines `node_pattern` which is unused dead code.
2. **Multi-Hop Parsing Failure**: Line 68 uses `edge_pattern = re.compile(r'([\w\-]+)\s*(-->|---|==>|-\.->)\s*(?:\|([^\|]+)\|)?\s*([\w\-]+)')` with `finditer`. When given `A --> B --> C`, the first match consumes `A --> B`. Scanning resumes after `B` at ` --> C`, which lacks a starting node identifier `[\w\-]+`. As a result, `finditer` fails to match `B --> C` and silently drops all subsequent hops.
3. **Inline Edge Text Syntax Unsupported**: Syntax such as `A -- text --> B` is not matched by the existing regex, which only handles pipe labels (`-->|text|`).
4. **Shape Suffix Interference**: If shape annotations are placed on edge lines (e.g. `A[Start] --> B{Choice}`), the existing regex fails because `[Start]` sits between the node ID `A` and arrow `-->`.

---

## 2. Evidence Chain & Detailed Observations

### Observation 1: Node Shape Style Mapping & Unused Regex
- **Location**: `src/antigravity_drawio_mcp/mermaid_converter.py`, lines 17, 58–63, 114
- **Code Quote**:
  ```python
  17: node_pattern = re.compile(r'([\w\-]+)(?:(\["?.*?"?\])|\({"?.*?"?\}\)|\(("?.*?"?\)))')
  ...
  58: for match in re.finditer(r'([\w\-]+)\["?(.*?)"?\]', line):
  59:     nid, nval = match.groups()
  60:     if nid not in node_styles:
  61:         node_labels[nid] = nval
  62:         node_styles[nid] = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
  ```
- **Analysis**:
  - Line 62 sets `node_styles[nid]` to `"rounded=1;..."` for rectangular `[label]` nodes. The project requirement explicitly specifies `[label]` -> rectangular style (`rounded=0;whiteSpace=wrap;html=1;`).
  - Line 114 uses `"rounded=1;..."` as the default style for unshaped nodes. Standard rectangle nodes should default to `rounded=0;`.
  - Line 17 defines `node_pattern`, which is never used anywhere in the class.

### Observation 2: Multi-Hop Parsing Bug in `edge_pattern.finditer(line)`
- **Location**: `src/antigravity_drawio_mcp/mermaid_converter.py`, lines 68–79
- **Code Quote**:
  ```python
  68: edge_pattern = re.compile(r'([\w\-]+)\s*(-->|---|==>|-\.->)\s*(?:\|([^\|]+)\|)?\s*([\w\-]+)')
  69: for match in edge_pattern.finditer(line):
  70:     src, arrow, label, tgt = match.groups()
  71:     raw_edges.append((src, tgt, label or ""))
  ```
- **Analysis**:
  - `re.finditer` tracks non-overlapping match spans.
  - Input: `A --> B --> C`
  - First match: `src="A"`, `arrow="-->"`, `tgt="B"` spanning indices `0..7` (`"A --> B"`).
  - Next search index is `7` (immediately after `B`). Remaining substring: `" --> C"`.
  - Because `edge_pattern` begins with `([\w\-]+)` (node ID requirement), `" --> C"` does not match because it starts with whitespace and an arrow. `B` was consumed by Match 1 and cannot be reused by `finditer` as `src` for Match 2.
  - Result: Only edge `A -> B` is recorded. Edge `B -> C` is completely lost.

### Observation 3: Missing Support for Inline Arrow Labels (`-- text -->`)
- **Location**: `src/antigravity_drawio_mcp/mermaid_converter.py`, line 68
- **Analysis**:
  - Mermaid allows edge labels using inline notation: `A -- text --> B`, `A == text ==> B`, `A -. text .-> B`.
  - Line 68 only matches pipe syntax `(?:\|([^\|]+)\|)?` after standard arrows (`-->|text|`). Inline text notation `A -- text --> B` fails to parse edge labels.

### Observation 4: Shape Annotation Suffixes Block Edge Match
- **Location**: `src/antigravity_drawio_mcp/mermaid_converter.py`, lines 40–79
- **Analysis**:
  - If a line specifies node shapes on an edge statement, e.g. `A[Client] --> B{Decision}`, line 68 expects `([\w\-]+)` immediately followed by `\s*` and an arrow.
  - The string `[Client]` between `A` and `-->` prevents `([\w\-]+)\s*(-->` from matching.

---

## 3. Formulated Strategy & Technical Design

To resolve all observed issues cleanly and robustly without breaking existing functionality, we formulate a 3-step pipeline per line:

### Step 1: Precise Node Shape & Label Extraction
We update the regex patterns for `{label}`, `(label)`, and `[label]`, ensuring label quotes are stripped and exact Draw.io styles are applied:
1. **Rhombus `{label}`**:
   - Regex: `r'([\w\-]+)\s*\{"?(.*?)"?\}'`
   - Style: `"rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"`
2. **Rounded `(label)`**:
   - Regex: `r'([\w\-]+)\s*\("?(.*?)"?\)'`
   - Style: `"rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"`
3. **Rectangle `[label]`**:
   - Regex: `r'([\w\-]+)\s*\["?(.*?)"?\]'`
   - Style: `"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"`
4. **Default fallback style** (nodes without explicit shape):
   - Style: `"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"`

### Step 2: Line Cleaning (Shape Annotation Suffix Stripping)
Before parsing edges, strip shape annotations from `line` to leave clean node IDs and arrow connectors:
```python
cleaned_line = re.sub(r'([\w\-]+)\s*(?:\[[^\]]*\]|\{[^\}]*\}|\([^\)]*\))', r'\1', line)
```
*Example Transformation*:
`A[Client] -->|HTTP| B{Decision} -- Yes --> C(Process)`  
$\rightarrow$ `A -->|HTTP| B -- Yes --> C`

### Step 3: Unified Arrow Connector Regex & Chain Tokenization
We construct a unified `ARROW_CONNECTOR_PATTERN` that matches all arrow syntax variations (pipe labels, inline labels, plain arrows):
```python
ARROW_CONNECTOR_PATTERN = re.compile(
    r'\s*(?:(--|==|-\.)\s+([^-\s][^|]*?)\s+(-->|---|==>|\.->|->)|'
    r'(-->|---|==>|-\.->)\s*\|([^\|]+)\|'
    r'|(-->|---|==>|-\.->))\s*'
)
```

Using `finditer(cleaned_line)`, we scan all arrow connector matches on the line:
1. Extract node token strings before the first match, between adjacent matches, and after the final match.
2. Extract edge label strings from Group 2 (inline text) or Group 5 (pipe label).
3. Construct sequential edges `(node_tokens[i], node_tokens[i+1], labels[i])` for `i = 0..len(node_tokens)-2`.
4. Register all node IDs in `all_node_ids` and current subgraph.

---

## 4. Proposed Code Replacement for `mermaid_converter.py`

Below is the proposed exact implementation to be applied by the implementer agent:

```python
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

        # Unified Arrow connector regex matching all inline and pipe label variants
        ARROW_CONNECTOR_PATTERN = re.compile(
            r'\s*(?:(--|==|-\.)\s+([^-\s][^|]*?)\s+(-->|---|==>|\.->|->)|'
            r'(-->|---|==>|-\.->)\s*\|([^\|]+)\|'
            r'|(-->|---|==>|-\.->))\s*'
        )
        
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
            for match in re.finditer(r'([\w\-]+)\s*\{"?(.*?)"?\}', line):
                nid, nval = match.group(1), match.group(2).strip('"\'')
                node_labels[nid] = nval
                node_styles[nid] = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if current_subgraph and nid not in current_subgraph["nodes"]:
                    current_subgraph["nodes"].append(nid)

            # 2. Rounded (Label)
            for match in re.finditer(r'([\w\-]+)\s*\("?(.*?)"?\)', line):
                nid, nval = match.group(1), match.group(2).strip('"\'')
                node_labels[nid] = nval
                node_styles[nid] = "rounded=1;whiteSpace=wrap;html=1;arcSize=30;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if current_subgraph and nid not in current_subgraph["nodes"]:
                    current_subgraph["nodes"].append(nid)

            # 3. Rectangle [Label]
            for match in re.finditer(r'([\w\-]+)\s*\["?(.*?)"?\]', line):
                nid, nval = match.group(1), match.group(2).strip('"\'')
                node_labels[nid] = nval
                node_styles[nid] = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
                all_node_ids.add(nid)
                if current_subgraph and nid not in current_subgraph["nodes"]:
                    current_subgraph["nodes"].append(nid)

            # Clean line of shape bracket annotations for edge parsing
            cleaned_line = re.sub(r'([\w\-]+)\s*(?:\[[^\]]*\]|\{[^\}]*\}|\([^\)]*\))', r'\1', line)

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
                style = node_styles.get(nid, "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;")
                builder.add_node(nid, label, x_pos, y_pos, style=style)
                node_coords[nid] = (x_pos, y_pos)

        # Add edges
        edge_count = 0
        for src, tgt, label in raw_edges:
            edge_count += 1
            builder.add_edge(f"e_{src}_{tgt}_{edge_count}", src, tgt, label=label)

        return builder.to_xml()
```

---

## 5. Verification Plan & Target Unit Tests

To verify the proposed fix, add test methods in `tests/test_mcp_server.py`:
1. `test_13_mermaid_shapes_exact_style()`: Verify `{label}` produces `rhombus`, `(label)` produces `rounded=1`, `[label]` produces `rounded=0`.
2. `test_14_mermaid_multi_hop_chain()`: Verify `A --> B --> C` produces 3 nodes and 2 edges (`A->B` and `B->C`).
3. `test_15_mermaid_inline_label_multi_hop()`: Verify `A -- HTTP --> B -- Yes --> C` extracts both labels (`HTTP` and `Yes`) and creates edges `A->B` and `B->C`.
