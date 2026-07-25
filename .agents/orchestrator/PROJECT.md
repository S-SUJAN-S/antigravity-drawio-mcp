# Project: antigravity-drawio-mcp Code Audit & 10 Fix Items

## Architecture & Goals
Execute a comprehensive code refactor and feature enhancement for `antigravity-drawio-mcp` resolving 10 critical, functional, and robustness audit items, including XML security (`defusedxml`), cross-platform export support, Mermaid JS converter enhancements (shapes, multi-hop, subgraphs, topological layout), builder validation, auto-collision resolution, test suite expansion, package version bump, build, tag, and PyPI release preparation.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Security & Process Safety | Parser `defusedxml` conversion, narrowed decoding exceptions, exporter cross-platform resolution (macOS, Linux, PATH) & process handling | None | DONE |
| 2 | M2: Mermaid Converter & Layout Engine | Mermaid shape syntax (`{rhombus}`, `(rounded)`), multi-hop lines (`A-->B-->C`), `subgraph` support, topological depth calculation (`x = depth * 250`) | None | DONE |
| 3 | M3: Builder Validation & Auto-Collision Tool | `builder.py` duplicate node ID validation & dangling edge detection, `verifier.py` `auto_resolve()` implementation, `resolve_diagram_collisions` MCP tool | M1, M2 | DONE |
| 4 | M4: Comprehensive Test Suite, Version Bump & Release Prep | Expand `tests/test_mcp_server.py` (XXE, compressed XML, error paths, all 7 MCP tool wrappers, validation), unit test verification, version bump, sdist/wheel build, git tag, PyPI release prep | M1, M2, M3 | PLANNED |

## Interface Contracts & Standards
- `parser.py`: Use `defusedxml.ElementTree.fromstring` for XML parsing. Exception handling in `_decode_diagram_text` must be narrowed to `(binascii.Error, zlib.error, UnicodeDecodeError)`.
- `exporter.py`: `get_drawio_executable()` check macOS (`/Applications/draw.io.app/Contents/MacOS/draw.io`), Linux (`/usr/bin/drawio`, `/opt/drawio/drawio`), and `shutil.which("drawio")`. Process termination must be cross-platform (`platform.system()`) and deferred until locking occurs.
- `mermaid_converter.py`: Node syntax `{label}` -> rhombus, `(label)` -> rounded. Support multi-hop (`A --> B --> C`). Support `subgraph`. Layout calculation based on topological depth (`x = depth * 250`).
- `builder.py`: `add_node()` raises `ValueError` on duplicate node IDs. `add_edge()` raises `ValueError` on dangling source/target node IDs. Exposed cleanly as JSON error response in `server.py`.
- `verifier.py`: `DrawIOVerifier.auto_resolve()` shifts overlapping nodes vertically down until 0 collisions (`is_clean` is True). Expose `resolve_diagram_collisions` tool in `server.py`.
- `tests/test_mcp_server.py`: 10+ comprehensive unit test cases, 100% passing.
- `pyproject.toml` & `__init__.py`: Version bump, build wheel/sdist, git tag.
