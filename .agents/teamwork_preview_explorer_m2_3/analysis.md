# Technical Analysis & Implementation Plan: Milestone 2 - R3 Topological Depth Layout Engine

## Executive Summary
This document provides a comprehensive code audit of `src/antigravity_drawio_mcp/mermaid_converter.py` for Milestone 2 - R3 (Topological Depth Layout Engine). It details the architectural flaws in the current layout generator, outlines the required coordinate mapping transformations, and presents a robust multi-pass topological depth algorithm with directed cycle recovery.

---

## 1. Problem Statement & Scope Audit

### 1.1 Objective
Transform the layout algorithm in `MermaidToDrawIO.convert()` from a static column placement model to an automated, dynamic topological depth engine satisfying:
1. **Horizontal Coordinate Calculation**: `x = depth * 250` (or `40 + depth * 250` / `100 + depth * 250` offset).
2. **Topological Depth Algorithm with Cycle Recovery**: Multi-pass BFS traversal from root nodes (`in-degree == 0`), extended with cycle detection and depth fallback for graph cycles or isolated cyclic components.
3. **Vertical Stacking (`y` calculation)**: Collision-free vertical stacking (`y_pos = 80 + row_idx * 110`) per depth level to prevent overlapping bounding boxes.

---

## 2. Deep Dive Code Audit of `mermaid_converter.py`

### 2.1 Current Implementation (Lines 80–117)

```python
80:         # Topological depth calculation for multi-column layout
81:         adj = defaultdict(list)
82:         in_degree = defaultdict(int)
83:         for nid in all_node_ids:
84:             in_degree[nid] = 0
85: 
86:         for src, tgt, _ in raw_edges:
87:             adj[src].append(tgt)
88:             in_degree[tgt] += 1
89: 
90:         depths = {nid: 0 for nid in all_node_ids}
91:         queue = deque([nid for nid in all_node_ids if in_degree[nid] == 0])
92: 
93:         while queue:
94:             curr = queue.popleft()
95:             for nxt in adj[curr]:
96:                 depths[nxt] = max(depths[nxt], depths[curr] + 1)
97:                 in_degree[nxt] -= 1
98:                 if in_degree[nxt] == 0:
99:                     queue.append(nxt)
100: 
101:         # Group nodes by depth column
102:         depth_columns = defaultdict(list)
103:         for nid, d in depths.items():
104:             depth_columns[d].append(nid)
105: 
106:         # Assign coordinates & add nodes to builder
107:         node_coords = {}
108:         for col_idx, col_nodes in depth_columns.items():
109:             x_pos = 100 + col_idx * 260
110:             y_start = 80
111:             for row_idx, nid in enumerate(col_nodes):
112:                 y_pos = y_start + row_idx * 110
113:                 label = node_labels.get(nid, nid)
114:                 style = node_styles.get(nid, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;")
115:                 builder.add_node(nid, label, x_pos, y_pos, style=style)
116:                 node_coords[nid] = (x_pos, y_pos)
```

---

### 2.2 Flaws Identified in Existing Code

#### Flaw 1: Failure on Cyclic Graphs (Kahn's Algorithm Stalls)
- **Mechanism**: Standard Kahn's algorithm initializes `queue` only with nodes having `in_degree == 0`.
- **Failure Scenario 1 (Pure Cycle `A -> B -> C -> A`)**:
  - `in_degree['A'] = 1`, `in_degree['B'] = 1`, `in_degree['C'] = 1`.
  - `queue` is initially empty `[]`.
  - `while queue:` block is skipped entirely.
  - All nodes remain at `depths[nid] = 0`.
  - Nodes `A`, `B`, and `C` are all placed into column 0 at `x = 100`, stacked vertically instead of flowing horizontally.
- **Failure Scenario 2 (Partial Cycle `A -> B -> C -> B`)**:
  - `A` has in-degree 0; `B` has in-degree 2; `C` has in-degree 1.
  - `A` is popped from queue. `in_degree[B]` decrements from 2 to 1 (not 0).
  - Queue becomes empty. `B` and `C` are never processed and remain at depth 0.

#### Flaw 2: Non-Standard Horizontal Pitch Constant
- Line 109 uses `x_pos = 100 + col_idx * 260`.
- The requirement explicitly specifies horizontal coordinate positioning `x = depth * 250` (or `40 + depth * 250` / `x_start + depth * 250`).
- Standardizing to step size `250` ensures consistency across unit test assertions and export rendering.

#### Flaw 3: Structural Integrity of Vertical Stacking
- Current vertical stacking (`y_pos = 80 + row_idx * 110`) works well for standard 60px height nodes (giving 50px clearance).
- However, nodes at the same depth level must maintain deterministic order (e.g. sorted by ID or original insertion order) so visual builds remain reproducible across runs.

---

## 3. Proposed Fix & Architectural Strategy

### 3.1 Multi-Pass Topological Depth Calculation with Cycle Fallback

```python
# Step 1: Build graph structure
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

# Step 2: Primary Kahn's BFS (Root nodes with in_degree == 0)
queue = deque([nid for nid in all_node_ids if in_degree[nid] == 0])
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

# Step 3: Secondary Pass for Cyclic / Unvisited Nodes
while len(visited) < len(all_node_ids):
    unvisited = [n for n in all_node_ids if n not in visited]
    
    # Priority: Pick unvisited node with highest visited predecessor depth,
    # or node with minimum remaining in-degree
    best_cand = None
    best_pred_depth = -1
    
    for u in unvisited:
        visited_preds = [preds_node for preds_node in preds[u] if preds_node in visited]
        if visited_preds:
            max_d = max(depths[p] for p in visited_preds)
            if max_d > best_pred_depth:
                best_pred_depth = max_d
                best_cand = u
                
    if best_cand is None:
        # Isolated cycle: pick first unvisited node
        best_cand = sorted(unvisited)[0]
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
```

---

### 3.2 Coordinate Assignment Algorithm

```python
# Step 4: Group nodes by depth column and sort deterministically
depth_columns = defaultdict(list)
for nid in sorted(all_node_ids):
    d = depths[nid]
    depth_columns[d].append(nid)

# Step 5: Assign x = depth * 250 (with base margin x_start = 40 or 100) and y = 80 + row_idx * 110
node_coords = {}
x_start = 40  # Margin offset
y_start = 80  # Top offset

for col_idx in sorted(depth_columns.keys()):
    col_nodes = depth_columns[col_idx]
    x_pos = x_start + col_idx * 250  # x = depth * 250 layout formula
    for row_idx, nid in enumerate(col_nodes):
        y_pos = y_start + row_idx * 110
        label = node_labels.get(nid, nid)
        style = node_styles.get(nid, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;")
        builder.add_node(nid, label, x_pos, y_pos, style=style)
        node_coords[nid] = (x_pos, y_pos)
```

---

## 4. Verification & Testing Strategy

1. **Unit Test for Cyclic Graph Layout**:
   Verify that a graph containing cycles (`A -> B -> C -> A`) assigns distinct topological depth columns (`depth(A) = 0`, `depth(B) = 1`, `depth(C) = 2`) rather than dropping all nodes into depth 0.
2. **Collision Analysis**:
   Verify with `DrawIOVerifier.verify()` that no vertical or horizontal bounding box collisions occur between nodes at the same depth level.
3. **Step Size Assertions**:
   Verify `x(col_idx + 1) - x(col_idx) == 250`.
