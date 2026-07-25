# Milestone 2 - R3 Subgraph Support Analysis & Implementation Strategy

## Executive Summary
This document provides a comprehensive technical analysis of `src/antigravity_drawio_mcp/mermaid_converter.py` for **Milestone 2 - R3 Subgraph Support**. It details the current parser limitations, formulates exact regular expressions and stack-based parsing logic for all Mermaid `subgraph` syntax variants (including nested subgraphs), and establishes a container layout & XML rendering strategy compatible with `DrawIOBuilder` and `DrawIOVerifier`.

---

## 1. Current Codebase Audit (`mermaid_converter.py`)

### 1.1 Existing Subgraph Handling Code (Lines 13-36 & 45-78)
In the current implementation of `mermaid_converter.py`:
```python
subgraphs = []
current_subgraph = None

# ...

subgraph_match = re.match(r'subgraph\s+["\']?(.*?)["\']?$', line, re.IGNORECASE)
if subgraph_match:
    title = subgraph_match.group(1) or "Group"
    current_subgraph = {"title": title, "nodes": []}
    subgraphs.append(current_subgraph)
    continue

if line.lower() == "end":
    current_subgraph = None
    continue
```

### 1.2 Identified Flaws & Limitations
1. **Incomplete Syntax Parsing**:
   - Does not parse `subgraph id [title]` or `subgraph id ["title"]` syntax. For `subgraph sub1 [Frontend App]`, regex captures `sub1 [Frontend App]` as the title string instead of extracting `id="sub1"` and `title="Frontend App"`.
2. **No Nesting Support**:
   - `current_subgraph` is stored as a single variable. Nested `subgraph` blocks overwrite `current_subgraph` and break upon encountering the first `end` statement.
3. **Container Output Omitted**:
   - `subgraphs` list is populated during parsing but **never rendered** into the output Draw.io XML! Subgraphs are completely lost when `builder.to_xml()` is called.
4. **Missing Container Coordinate & Boundary Logic**:
   - Child node positions are computed via topological depth layout, but container bounding boxes `(x, y, width, height)` are never calculated to enclose child nodes.

---

## 2. Parsing Strategy for `subgraph` Syntax Variants

### 2.1 Supported Mermaid Subgraph Syntax Forms
| Syntax Form | Example Line | Extracted ID | Extracted Title |
|-------------|--------------|--------------|-----------------|
| `subgraph id [title]` | `subgraph sub1 [Frontend App]` | `sub1` | `Frontend App` |
| `subgraph id ["title"]` | `subgraph sub1 ["React UI"]` | `sub1` | `React UI` |
| `subgraph title` | `subgraph Database Layer` | `sub_Database_Layer` | `Database Layer` |
| `subgraph "title"` | `subgraph "Backend Services"` | `sub_Backend_Services` | `Backend Services` |
| `subgraph id` | `subgraph sub1` | `sub1` | `sub1` |

### 2.2 Two-Stage Regex Parser
To reliably extract `id` and `title` without edge-case ambiguity:

```python
# Pattern 1: Explicit ID and Bracketed Title -> subgraph id [Title] or subgraph id ["Title"]
SUBGRAPH_BRACKET_RE = re.compile(
    r'^\s*subgraph\s+([\w\-]+)\s*\[\s*["\']?(.*?)["\']?\s*\]\s*$',
    re.IGNORECASE
)

# Pattern 2: Simple Title or ID -> subgraph Title or subgraph "Title" or subgraph id
SUBGRAPH_SIMPLE_RE = re.compile(
    r'^\s*subgraph\s+["\']?(.*?)["\']?\s*$',
    re.IGNORECASE
)
```

### 2.3 Stack-Based Parsing Algorithm (Nesting Support)
Using a stack (`subgraph_stack = []`), nested subgraphs can be tracked cleanly:

```python
subgraph_stack = []  # Stack of currently active subgraph dicts
all_subgraphs = []   # Flat list of all parsed subgraphs

for line in lines:
    line_clean = line.strip()
    if not line_clean or line_clean.startswith("%%"):
        continue

    # 1. Handle 'end'
    if line_clean.lower() == "end":
        if subgraph_stack:
            subgraph_stack.pop()
        continue

    # 2. Handle Subgraph Start (Bracket Syntax)
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

    # 3. Handle Subgraph Start (Simple Syntax)
    m_simple = SUBGRAPH_SIMPLE_RE.match(line_clean)
    if m_simple and not line_clean.lower().startswith(("graph", "flowchart", "direction")):
        raw_val = m_simple.group(1).strip()
        if raw_val:
            sub_title = raw_val
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

    # 4. Associate extracted node IDs with active subgraphs
    # Whenever a node `nid` is found in line:
    if subgraph_stack:
        for active_sub in subgraph_stack:
            if nid not in active_sub["nodes"]:
                active_sub["nodes"].append(nid)
```

---

## 3. Draw.io XML Container Representation & Positioning

### 3.1 Container Shape Style Selection
Draw.io uses `swimlane` (or `container=1`) shapes to represent subgraphs. The recommended style string for subgraph container cells is:

```python
CONTAINER_STYLE = (
    "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;"
    "fillColor=#F8F9FA;strokeColor=#6C757D;strokeWidth=1.5;"
    "fontStyle=1;fontSize=13;startSize=30;horizontal=1;"
)
```
- `swimlane`: Creates a standard container box with a dedicated header banner for the title.
- `startSize=30`: Reserve 30px height header for the title text.
- `fillColor=#F8F9FA;strokeColor=#6C757D`: Clean grayscale container styling matching Draw.io defaults.

### 3.2 Coordinate System Analysis: Absolute vs Relative `parent`
- **Approach A (Absolute Coordinates + Layer Root `parent="1"`)**:
  - Container box is created as an `mxCell` with `vertex="1"`, `parent="1"`, `(sub_x, sub_y, sub_w, sub_h)`.
  - Child nodes are created with `parent="1"` and absolute positions `(child_x, child_y)`.
  - Container cell MUST be added to `DrawIOBuilder` **BEFORE** child nodes so it renders underneath them.
  - **Compatibility**: 100% compatible with existing `DrawIOBuilder`, `DrawIOParser`, and `DrawIOVerifier.verify()`. `is_container_of(container, child)` evaluates `True` because `sub_x <= child_x` and `sub_y <= child_y` and `sub_x + sub_w >= child_x + width` and `sub_y + sub_h >= child_y + height`. Zero false collision flags.

- **Approach B (Relative Coordinates + Parent Cell `parent="sub_id"`)**:
  - Requires updating `DrawIOBuilder` to support `parent` field.
  - `DrawIOParser` currently extracts raw `x, y` without resolving parent offsets, causing `DrawIOVerifier` to fail container check (`is_container_of` returns `False`).

**Conclusion**: Approach A (Absolute coordinates with container added first) is superior, robust, and zero-breaking-change.

### 3.3 Container Boundary & Padding Calculation

Given child nodes inside subgraph $S$ with calculated diagram absolute coordinates $(x_i, y_i)$ and dimensions $(w_i, h_i)$:

$$ \text{min\_x} = \min_{i \in S} (x_i), \quad \text{max\_r} = \max_{i \in S} (x_i + w_i) $$
$$ \text{min\_y} = \min_{i \in S} (y_i), \quad \text{max\_b} = \max_{i \in S} (y_i + h_i) $$

Applying container padding:
- `padding_left = 30`
- `padding_right = 30`
- `padding_top = 50` (30px header + 20px margin)
- `padding_bottom = 30`

Container Geometry:
- `sub_x = min_x - padding_left`
- `sub_y = min_y - padding_top`
- `sub_w = (max_r - min_x) + padding_left + padding_right`
- `sub_h = (max_b - min_y) + padding_top + padding_bottom`

### 3.4 Multi-Subgraph Overlap Prevention
When multiple subgraphs exist in the diagram, their node Y-positions are adjusted per subgraph block:
1. Sort subgraphs by top Y-coordinate (`sub_y`).
2. If `sub_B` top coordinate `sub_B.y` is less than `sub_A.y + sub_A.h + vertical_gap`, shift all nodes in `sub_B` down by `shift_y = (sub_A.y + sub_A.h + vertical_gap) - sub_B.y`.
3. Recompute bounding box for `sub_B`.

---

## 4. Proposed Code Snippet for `mermaid_converter.py`

```python
# Calculate Subgraph Bounding Boxes
subgraph_cells = []
for sub in all_subgraphs:
    sub_nodes = sub["nodes"]
    if not sub_nodes:
        continue
    
    node_x_min = min(node_coords[nid][0] for nid in sub_nodes if nid in node_coords)
    node_y_min = min(node_coords[nid][1] for nid in sub_nodes if nid in node_coords)
    node_x_max = max(node_coords[nid][0] + 140 for nid in sub_nodes if nid in node_coords)
    node_y_max = max(node_coords[nid][1] + 60 for nid in sub_nodes if nid in node_coords)

    sub_x = node_x_min - 30
    sub_y = node_y_min - 50
    sub_w = (node_x_max - node_x_min) + 60
    sub_h = (node_y_max - node_y_min) + 80

    subgraph_cells.append({
        "id": sub["id"],
        "title": sub["title"],
        "x": sub_x, "y": sub_y,
        "w": sub_w, "h": sub_h
    })

# 1. Add Subgraph Container Cells FIRST
for sc in subgraph_cells:
    builder.add_node(
        sc["id"],
        sc["title"],
        sc["x"],
        sc["y"],
        width=sc["w"],
        height=sc["h"],
        style="swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;fillColor=#F8F9FA;strokeColor=#6C757D;strokeWidth=1.5;fontStyle=1;fontSize=13;startSize=30;"
    )

# 2. Add Child Nodes SECOND
for col_idx, col_nodes in depth_columns.items():
    # ... builder.add_node(...) for child nodes ...

# 3. Add Edges THIRD
# ... builder.add_edge(...) ...
```

---

## 5. Verification Matrix & Edge Case Coverage

| Test Case | Scenario | Expected Outcome | Verification Method |
|-----------|----------|------------------|---------------------|
| TC-01 | Single subgraph (`subgraph sub1 [Title]`) | Container box rendered around nodes | `DrawIOParser` returns container node and child nodes |
| TC-02 | Unquoted title (`subgraph Backend Services`) | Auto-generated ID `sub_Backend_Services` | Node exists in XML output |
| TC-03 | Nested subgraphs | Parent and child containers enclosing nodes | Outer container strictly encloses inner container and nodes |
| TC-04 | Empty subgraph (0 nodes) | Handled gracefully without crash | Diagram compiles cleanly |
| TC-05 | Auto-Collision Verification | `DrawIOVerifier.verify()` returns `is_clean: True` | `is_container_of()` returns `True`, 0 collision issues |
