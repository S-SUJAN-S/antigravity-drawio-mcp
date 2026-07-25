# Execution Plan: antigravity-drawio-mcp Code Audit & 10 Fix Items

## Overview
Decomposed into 4 milestones targeting security, cross-platform stability, converter/layout engine, builder/verifier tools, test suite expansion, and release prep.

## Milestone Breakdown
### Milestone 1: Security & Process Safety (R1 & R2)
- Objectives:
  1. Replace `xml.etree.ElementTree` with `defusedxml.ElementTree` in `parser.py`.
  2. Narrow `_decode_diagram_text` exception handling to `(binascii.Error, zlib.error, UnicodeDecodeError)` and add tracebacks on malformed XML.
  3. Update `get_drawio_executable()` in `exporter.py` for macOS, Linux, and PATH lookup (`shutil.which`).
  4. Make process termination cross-platform using `platform.system()` and attempt non-killing export first.
- Execution steps:
  - Dispatch Explorer M1 to inspect `parser.py` and `exporter.py`.
  - Dispatch Worker M1 to implement R1 & R2 fixes.
  - Dispatch Reviewer M1 & Challenger M1 to review code and test security/process handling.
  - Dispatch Forensic Auditor M1 to verify integrity.

### Milestone 2: Mermaid Converter & Layout Engine (R3)
- Objectives:
  1. Support `{rhombus}` and `(rounded)` node shapes in `mermaid_converter.py`.
  2. Support single-line multi-hop arrows (`A --> B --> C`).
  3. Support `subgraph` grouping containers.
  4. Implement topological depth calculation (`x = depth * 250`) and vertical stacking for collision-free layout.
- Execution steps:
  - Dispatch Explorer M2 to analyze parsing grammar & layout calculation in `mermaid_converter.py`.
  - Dispatch Worker M2 to implement converter enhancements.
  - Dispatch Reviewer M2 & Challenger M2 to review & run synthetic tests.
  - Dispatch Forensic Auditor M2 for integrity check.

### Milestone 3: Builder Validation & Auto-Collision Tool (R4)
- Objectives:
  1. Duplicate node ID check in `builder.py` (`add_node`) and dangling edge check (`add_edge`), returning clean JSON errors in `server.py`.
  2. Implement `DrawIOVerifier.auto_resolve()` in `verifier.py` to auto-shift overlapping nodes down until 0 collisions (`is_clean` is True).
  3. Expose `resolve_diagram_collisions` as an MCP tool in `server.py`.
- Execution steps:
  - Dispatch Explorer M3 to audit `builder.py`, `verifier.py`, and `server.py`.
  - Dispatch Worker M3 to implement validation and auto-collision tool.
  - Dispatch Reviewer M3 & Challenger M3 to verify API contracts and JSON error responses.
  - Dispatch Forensic Auditor M3 for integrity check.

### Milestone 4: Test Suite Expansion, Version Bump & Release Prep (R5)
- Objectives:
  1. Expand `tests/test_mcp_server.py` to 10+ test cases covering XXE, compressed XML, malformed XML, missing files, duplicate node IDs, dangling edges, and direct tool wrapper calls for all 7 MCP tools.
  2. Run unit test suite `python -m unittest tests/test_mcp_server.py` and ensure 100% pass.
  3. Bump version in `pyproject.toml` and `__init__.py`.
  4. Build package (sdist/wheel), tag git release, prepare PyPI publication.
- Execution steps:
  - Dispatch Explorer M4 to outline test suite expansion and release checklist.
  - Dispatch Worker M4 to write test suite, run tests, bump version, build package, tag release.
  - Dispatch Reviewer M4 & Challenger M4 to verify test coverage and release artifacts.
  - Dispatch Forensic Auditor M4 for final integrity verification.
