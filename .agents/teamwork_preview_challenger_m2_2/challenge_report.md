# Milestone 2 Challenge Report — Topological Layout & Subgraph Converter

## Challenge Summary

**Overall risk assessment**: MEDIUM

Empirical stress testing of `src/antigravity_drawio_mcp/mermaid_converter.py` was conducted using standalone Python test harnesses.
- **Topological Layout & Depth (`x = depth * 250`)**: **CONFIRMED (PASS)**. Depth ordering correctly places root nodes at depth 0 (`x=80.0`), intermediate nodes at depth 1 (`x=330.0`), and downstream nodes at depth 2 (`x=580.0`), yielding exact `delta_x = 250.0`. Cyclic back-edges (`D -> A`) are correctly resolved via Kahn's secondary queue without infinite recursion or node collisions.
- **Single & Parallel Subgraphs**: **CONFIRMED (PASS)**. Single and parallel swimlane container boundaries encompass child nodes with required padding (`x_min - 20`, `y_min - 35`, `w + 40`, `h + 45`). Parallel swimlane containers maintain clear separation without collisions.
- **Nested Subgraphs**: **REJECTED / VULNERABILITY FOUND (HIGH RISK)**. When subgraphs are nested (e.g., `subgraph outer` wrapping `subgraph inner`), outer swimlane bounds are computed exclusively from raw child node coordinates rather than including inner container geometry. As a result:
  - If `outer` contains only `inner`, `outer` container bounds collapse to `(60.0, 45.0, 430.0, 105.0)` — 100% IDENTICAL to `inner` container bounds `(60.0, 45.0, 430.0, 105.0)`.
  - The swimlane header titles ("Outer Group" and "Inner Group") render directly on top of each other at `(60.0, 45.0)`.

---

## Challenges

### [High] Challenge 1: Nested Subgraph Container Boundary Collapse & Header Overlap

- **Assumption challenged**: That iterating over `all_subgraphs` and computing bounds from `sub["nodes"]` handles nested subgraphs correctly.
- **Attack scenario**: Convert a Mermaid flowchart with nested subgraphs (`subgraph outer` -> `subgraph inner` -> `A --> B`).
- **Blast radius**: Outer swimlane containers overlap inner swimlane containers exactly. Title text and header borders collide at pixel coordinates `(60.0, 45.0)`, visually breaking diagram hierarchy and causing title unreadability in Draw.io.
- **Mitigation**: In `mermaid_converter.py`, bottom-up container boundary calculation should be implemented so that outer subgraphs calculate their bounding boxes over all contained child nodes AND all nested child subgraph container boxes (adding proper swimlane header height padding of ~30px for nested titles).

---

## Stress Test Results

| Scenario | Expected Behavior | Actual Behavior | Result |
|----------|-------------------|-----------------|--------|
| Branching & Cyclic Graph (`A->B, A->C, B->D, C->D, D->A`) | Topological depth: A=0 (`x=80`), B/C=1 (`x=330`), D=2 (`x=580`). `delta_x=250`. Zero node collisions. | A: (80.0, 80.0), B: (330.0, 80.0), C: (330.0, 190.0), D: (580.0, 80.0). `delta_x=250.0`. 0 collisions. | **PASS** |
| Multi-hop Chain (`A ==> B -.-> C -- D`) | 3 edges parsed, correct shapes & arrow labels. | `A->B` (thick), `B->C` (dotted), `C->D` (label) parsed cleanly. | **PASS** |
| Single Subgraph (`subgraph sg1`) | Swimlane box wraps nodes with 20px/35px margin padding. | `sg1`: x=60.0, y=45.0, w=430.0, h=105.0 enclosing A and B. | **PASS** |
| Multiple Parallel Subgraphs (`sg1`, `sg2`) | Separate non-overlapping swimlane containers. | `sg1`: (60,45,430,105), `sg2`: (560,45,430,105). 0 collisions. | **PASS** |
| Purely Nested Subgraphs (`outer` wrapping `inner`) | `outer` swimlane box encloses `inner` swimlane box with extra margin for nested title. | `outer` bounds: (60.0, 45.0, 430.0, 105.0) == `inner` bounds: (60.0, 45.0, 430.0, 105.0). Headers overlap. | **FAIL** |

---

## Unchallenged Areas

- **Draw.io GUI Rendering Engine**: Internal rendering behavior within native Draw.io Desktop application (tested XML output structure and mxGeometry values directly).
