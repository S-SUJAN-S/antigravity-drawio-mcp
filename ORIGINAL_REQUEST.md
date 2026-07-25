# Original User Request

## Initial Request — 2026-07-23T19:25:16Z

# Teamwork Project Prompt — GitHub & AI SEO Optimization for `antigravity-drawio-mcp`

Optimize `antigravity-drawio-mcp` for maximum search discoverability across Google, GitHub Search, PyPI, and AI/LLM Search engines (perplexity, ChatGPT, Claude, Antigravity) through comprehensive keyword research, README optimization, repository metadata enhancements, and indexability best practices.

Working directory: C:/Users/ssuja/OneDrive/Desktop/Learn_Antigravity_Advance/draw_io_automation/antigravity_drawio_mcp
Integrity mode: development

## Requirements

### R1. Keyword & AI SEO Discovery Audit
Perform web search and keyword analysis on high-volume developer search queries for "flowchart ai", "drawio ai", "drawio mcp", "diagram automation", "mcp server drawio", "antigravity mcp", and "ai architecture diagram generator". Identify missing search terms, meta tags, topic tags, and LLM-indexing semantic structures.

### R2. README & Documentation Optimization
Transform `README.md` and related docs into an SEO and GEO (Generative Engine Optimization) powerhouse:
- High-intent H1/H2 header keyword density.
- Structured microdata/schema summaries & LLM-friendly FAQ sections.
- PyPI badges, GitHub Topics list recommendation, and clear OpenGraph/Social preview metadata.
- Comprehensive search-indexed feature bullet points targeting developer search intents.

### R3. Automated SEO & Discoverability Verification
Verify keyword density, markdown header hierarchy, PyPI package metadata compatibility, and ensure `git commit` & `git push` sync the optimized documentation to GitHub (`S-SUJAN-S/antigravity-drawio-mcp`).

## Acceptance Criteria

### Search & LLM Discoverability
- [ ] `README.md` includes high-density keywords for "Draw.io MCP", "Flowchart AI Generator", "Google Antigravity MCP", and "Architecture Diagram AI".
- [ ] Includes an LLM-targeted "AI System Prompt & Quick Context" block for Perplexity/Claude/ChatGPT retrieval indexing.
- [ ] List of recommended GitHub Topics (tags) provided for repository settings (e.g., `mcp-server`, `drawio`, `antigravity`, `flowchart-ai`, `diagram-automation`, `model-context-protocol`).
- [ ] Changes committed and pushed to GitHub main branch.

## Follow-up — 2026-07-25T11:11:41Z

# Teamwork Project Prompt — Code Audit & 10 Fix Items for `antigravity-drawio-mcp`

Execute a comprehensive code refactor and feature enhancement for `antigravity-drawio-mcp` resolving 10 critical, functional, and robustness items identified in the code audit report, including XML security (`defusedxml`), cross-platform export support, Mermaid JS converter enhancements, builder validation, auto-collision resolution, and extended test coverage.

Working directory: C:/Users/ssuja/OneDrive/Desktop/Learn_Antigravity_Advance/draw_io_automation/antigravity_drawio_mcp
Integrity mode: development

## Requirements

### R1. Security & XML Parsing Integrity (`defusedxml`)
In `src/antigravity_drawio_mcp/parser.py`, replace standard `xml.etree.ElementTree` with `defusedxml.ElementTree` across all `ET.fromstring()` calls to prevent entity-expansion vulnerabilities. Narrow `_decode_diagram_text` exception handling to `(binascii.Error, zlib.error, UnicodeDecodeError)` and provide diagnostic error tracebacks on malformed XML.

### R2. Cross-Platform Executable Resolution & Process Safety
In `src/antigravity_drawio_mcp/exporter.py`:
- Update `get_drawio_executable()` to inspect macOS (`/Applications/draw.io.app/Contents/MacOS/draw.io`), Linux (`/usr/bin/drawio`, `/opt/drawio/drawio`), and `shutil.which("drawio")`.
- Make process-killing cross-platform using `platform.system()` (`taskkill /IM draw.io.exe /F` on Windows, `pkill -f draw.io` on Unix).
- Try export without process killing first; only attempt process termination with a stderr warning if file locking occurs.

### R3. Mermaid JS Converter Enhancements & Topological Layout
In `src/antigravity_drawio_mcp/mermaid_converter.py`:
- Support node shape syntax: `{label}` (rhombus/decision) and `(label)` (rounded) in addition to `[label]`.
- Parse multi-hop arrow chains on a single line (`A --> B --> C`).
- Support `subgraph` grouping containers.
- Replace fixed two-column cursor layout with topological depth calculation (`x = depth * 250`) and collision-free vertical stacking.

### R4. Builder Validation & Auto-Collision Resolution Tool
- In `src/antigravity_drawio_mcp/builder.py`, validate duplicate node IDs in `add_node()` and check for dangling edge references in `add_edge()`. Surface clean JSON error responses in `server.py`.
- In `src/antigravity_drawio_mcp/verifier.py`, implement `DrawIOVerifier.auto_resolve()` to automatically shift overlapping nodes down until 0 collisions remain, and expose `resolve_diagram_collisions` as an MCP tool.

### R5. Comprehensive Unit Test Suite Expansion
In `tests/test_mcp_server.py`, add tests for:
- XXE / entity-expansion rejection via `defusedxml`.
- Parsing zlib/base64-compressed `.drawio` XML.
- Malformed XML and missing file error handling.
- Direct invocation of all MCP server tool wrappers (`create_diagram`, `parse_diagram`, `validate_diagram`, `convert_mermaid_to_drawio`, `resolve_diagram_collisions`, `export_diagram`, `open_in_drawio`).
- Duplicate node IDs and dangling edge validation.

## Acceptance Criteria

### Security & Robustness
- [ ] `defusedxml.ElementTree` is used in `parser.py` and an entity-bomb test case passes by raising an exception.
- [ ] `exporter.py` runs gracefully without crashing on non-Windows platforms or missing PowerShell binaries.
- [ ] `builder.py` raises `ValueError` on duplicate node IDs and dangling edge references, returned as clean JSON errors.

### Features & Converters
- [ ] Mermaid converter correctly renders `{decision}` rhombus nodes, `(rounded)` nodes, multi-arrow lines (`A --> B --> C`), and `subgraph` blocks.
- [ ] Topological depth layout prevents node overlaps on branching Mermaid diagrams.
- [ ] `resolve_diagram_collisions` tool automatically adjusts overlapping node coordinates until `is_clean` is true.

### Test Suite & PyPI Release
- [ ] Unit test suite expanded from 4 to 10+ comprehensive test cases covering compressed parsing, error paths, and all MCP server tool wrappers.
- [ ] All unit tests pass cleanly (`python -m unittest tests/test_mcp_server.py`).
- [ ] Version bumped in `pyproject.toml` and `__init__.py`, built, tagged, and published to PyPI.

