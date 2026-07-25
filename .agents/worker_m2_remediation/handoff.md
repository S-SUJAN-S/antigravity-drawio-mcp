# Handoff Report — Milestone 2 Remediation (Nested Subgraph Bounds)

## 1. Observation
- File analyzed: `src/antigravity_drawio_mcp/mermaid_converter.py` lines 247-282 previously computed subgraph bounding boxes using only `valid_nodes = [nid for nid in sub_nodes if nid in node_coords]`.
- For nested subgraphs (e.g. `subgraph outer` wrapping `subgraph inner`), outer subgraphs calculated bounding boxes directly from leaf nodes, resulting in identical `sub_x`, `sub_y`, `sub_w`, `sub_h` values for outer and inner subgraphs.
- Test command `python -m unittest tests/test_mcp_server.py` ran 16 tests in initial baseline run, all 16 passed.
- After code modification in `src/antigravity_drawio_mcp/mermaid_converter.py` and addition of `test_17_mermaid_nested_subgraphs` in `tests/test_mcp_server.py`, command output:
```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.081s

OK
Test 01: Builder & Parser PASSED!
Test 02: Mermaid Conversion & Shapes PASSED!
Test 03: Verifier PASSED!
Test 04: Exporter executable found at: C:\Program Files\draw.io\draw.io.exe PASSED!
Test 05: DefusedXML XXE Bomb Protection PASSED!
Test 06: Compressed Diagram Parsing PASSED!
Test 07: Builder Validation (Duplicate Node & Dangling Edge) PASSED!
Test 08: Auto Resolve Collisions PASSED!
Test 09: Server Tool Wrappers PASSED!
Test 10: Parser Malformed XML Diagnostic Traceback PASSED!
Test 11: Exporter Cross-Platform Resolution PASSED!
Test 12: Exporter Non-Destructive Flow PASSED!
Test 13: Mermaid Shapes Exact Style PASSED!
Test 14: Mermaid Multi-Hop Chain PASSED!
Test 15: Mermaid Subgraph Containers & Verifier PASSED!
Test 16: Mermaid Topological Depth Layout & Cycle Tolerance PASSED!
Test 17: Mermaid Nested Subgraphs Bounding Box Enclosure PASSED!
```

## 2. Logic Chain
- Step 1: In `mermaid_converter.py`, subgraphs form a hierarchy tracked via `parent_id`. When inner subgraphs are nested inside outer subgraphs, computing bounding boxes solely from node coordinates ignores the margins and header space (`startSize=25`) of inner subgraphs.
- Step 2: To solve this, a recursive/memoized bottom-up bounding box calculator `get_subgraph_bounds(sub_id)` was implemented. It aggregates extreme coordinates from both leaf nodes AND all child subgraphs (`cx`, `cy`, `cx + cw`, `cy + ch`).
- Step 3: By applying standard swimlane padding (`margin_left=20`, `margin_top=35`, `margin_right=20`, `margin_bottom=10`) at each level of hierarchy, outer subgraphs expand outward relative to inner subgraphs by 20px on the left/right, 35px on the top (giving 25px header + 10px padding), and 10px on the bottom.
- Step 4: Subgraphs are assigned a nesting depth (`get_depth(sub_id)`), and added to `DrawIOBuilder` sorted by depth top-down (depth 0 first, depth 1 second, etc.) so that outer swimlane background cells render behind inner swimlane cells in Draw.io XML layer ordering.
- Step 5: `test_17_mermaid_nested_subgraphs` was added to `tests/test_mcp_server.py`. It converts a nested Mermaid diagram (`outer` -> `inner` -> `A --> B`), parses the resulting `.drawio` file using `DrawIOParser`, and asserts that:
  - `outer.x < inner.x` (outer left margin)
  - `outer.y < inner.y` (outer top margin)
  - `outer.width > inner.width`
  - `outer.height > inner.height`
  - `outer_right >= inner_right + 20`
  - `outer_bottom >= inner_bottom + 10`
  - `DrawIOVerifier.verify` confirms diagram structure is clean and valid.

## 3. Caveats
- No caveats. The implementation relies entirely on existing `DrawIOBuilder` and `DrawIOParser` contracts without introducing external dependencies or altering public method signatures.

## 4. Conclusion
- Nested subgraph bounding box calculation in `src/antigravity_drawio_mcp/mermaid_converter.py` has been successfully fixed.
- All 17 unit tests pass cleanly with 0 failures and 0 errors.

## 5. Verification Method
1. Run test suite command from project root:
   `python -m unittest tests/test_mcp_server.py`
2. Confirm output contains 17 passing tests, including `Test 17: Mermaid Nested Subgraphs Bounding Box Enclosure PASSED!`.
3. Inspect modified source files:
   - `src/antigravity_drawio_mcp/mermaid_converter.py`
   - `tests/test_mcp_server.py`
