# GitHub & PyPI Metadata Standards Audit — `antigravity-drawio-mcp`

**Explorer**: Explorer 3 (Milestone 1 — Keyword & AI SEO Discovery Audit)  
**Date**: 2026-07-24  
**Target Repository**: `C:/Users/ssuja/OneDrive/Desktop/Learn_Antigravity_Advance/draw_io_automation/antigravity_drawio_mcp`  

---

## 1. Executive Summary

This audit evaluates the package and repository metadata standards for **`antigravity-drawio-mcp`** across PyPI, GitHub, and AI search indexing engines (Perplexity, ChatGPT, Gemini, Claude, Cursor Search). 

### Key Findings
1. **`pyproject.toml` Core Metadata**: Well-configured basic attributes (name, version 1.0.5, description, authors, dependencies). However, keyword coverage, project URLs, and PyPI classifiers can be expanded to significantly boost package index ranking and search visibility.
2. **PyPI Keywords Array**: Currently contains 15 keywords. Key search terms like `mcp-server`, `draw.io` (dot notation), `diagram-as-code`, `windsurf`, and `c4-architecture` are missing.
3. **Project URLs Array**: Lacks direct links for `Documentation` and `Changelog`, and uses a raw `.git` URL for `Repository` rather than the web repository landing page.
4. **PyPI Trove Classifiers**: Currently missing `Environment :: Console`, `Operating System :: OS Independent`, Python 3.13 classifier, and relevant `Topic :: Multimedia :: Graphics :: Editors :: Vector-Based` / `Topic :: Software Development :: Documentation` classifiers.
5. **README Badges Audit**: Currently uses 5 static/third-party badges. Missing critical CI/CD build status badge (`publish.yml`) and PyPI monthly downloads badge.
6. **GitHub Repository Topics**: Curated recommendation of 20 optimized GitHub repository topics following GitHub's naming rules (lowercase, hyphenated, <=35 chars) to capture maximum topic taxonomy traffic.

---

## 2. Detailed Audit of `pyproject.toml` Metadata

### 2.1 Basic Package Identification & Description

| Field | Current Value | Assessment & Optimization Recommendation |
|---|---|---|
| `name` | `"antigravity-drawio-mcp"` | ✅ **Optimal**. Follows standard PyPI hyphenated naming convention. |
| `version` | `"1.0.5"` | ✅ **Optimal**. Aligns strictly with SemVer and matches `src/antigravity_drawio_mcp/__init__.py`. |
| `description` | `"Automate Flowcharts & Draw.io Diagrams with AI. Official Model Context Protocol (MCP) Server for Google Antigravity, Claude Code, Cursor, and VS Code."` | ✅ **Strong**. High keyword density (150 chars). Captures core search phrases: `Flowcharts`, `Draw.io`, `AI`, `Model Context Protocol`, `MCP Server`, `Google Antigravity`, `Claude Code`, `Cursor`, `VS Code`. |
| `readme` | `"README.md"` | ✅ **Optimal**. Standard setuptools long-description mapping. |
| `license` | `{ text = "MIT" }` | ⚠️ **Minor Update Recommended**. PEP 621 recommends `license = "MIT"` or `{ file = "LICENSE" }` alongside classifier `License :: OSI Approved :: MIT License`. |

---

### 2.2 PyPI Keywords Array Audit

#### Current PyPI Keywords (15 terms)
```toml
keywords = [
    "mcp",
    "drawio",
    "antigravity",
    "flowchart-ai",
    "flowchart-generator",
    "diagram-automation",
    "model-context-protocol",
    "ai-diagrams",
    "architecture-diagram",
    "mermaid-to-drawio",
    "cursor-ide",
    "claude-code",
    "google-antigravity",
    "fastmcp",
    "drawio-mcp"
]
```

#### Gap & Coverage Analysis
- **Missing Primary Search Query**: `mcp-server` is the single most common search phrase developers type on PyPI and GitHub when looking for MCP tools.
- **Missing Alternative Naming**: `draw.io` (with dot) and `draw-io` (with hyphen) are heavily searched variants of `drawio`.
- **Missing Developer Workflows**: `diagram-as-code` and `c4-architecture` reflect core software architecture paradigms supported by the package.
- **Missing Client Integrations**: `windsurf` is a key target AI IDE alongside Cursor and Claude Code.

#### Recommended Optimized PyPI Keywords Array (20 terms)
```toml
keywords = [
    "mcp",
    "mcp-server",
    "drawio",
    "draw.io",
    "antigravity",
    "google-antigravity",
    "model-context-protocol",
    "flowchart-ai",
    "flowchart-generator",
    "diagram-automation",
    "diagram-as-code",
    "ai-diagrams",
    "architecture-diagram",
    "mermaid-to-drawio",
    "cursor-ide",
    "claude-code",
    "windsurf",
    "fastmcp",
    "drawio-mcp",
    "c4-architecture"
]
```

---

### 2.3 Project URLs Array Audit

PyPI renders explicit sidebar action buttons for recognized standard keys in `[project.urls]`.

#### Current `[project.urls]`
```toml
[project.urls]
Homepage = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp"
Repository = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp.git"
Issues = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp/issues"
```

#### Issues Identified
1. `Repository` points to git HTTPS URI (`.git` suffix). PyPI web users expect the web repository URL.
2. Missing `Documentation` link targeting the detailed integration guide (`docs/INTEGRATION_GUIDE.md`).
3. Missing `Changelog` link pointing to GitHub Releases.

#### Recommended Optimized `[project.urls]`
```toml
[project.urls]
Homepage = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp"
Documentation = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp/blob/main/docs/INTEGRATION_GUIDE.md"
Repository = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp"
Issues = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp/issues"
Changelog = "https://github.com/S-SUJAN-S/antigravity-drawio-mcp/releases"
```

---

### 2.4 PyPI Trove Classifiers Audit

PyPI relies on Trove Classifiers for index filtering, categories, and technical compatibility matching.

#### Current Classifiers (10 items)
```toml
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Code Generators",
]
```

#### Missing Trove Classifiers
1. `Environment :: Console` — Declares executable CLI/stdio capability.
2. `Intended Audience :: Information Technology` — Broader enterprise audience classification.
3. `Operating System :: OS Independent` — Multi-platform support (Windows, macOS, Linux).
4. `Programming Language :: Python :: 3 :: Only` — Clarifies Python 3 exclusive support.
5. `Programming Language :: Python :: 3.13` — Reflects latest stable Python release compatibility.
6. `Topic :: Multimedia :: Graphics :: Editors :: Vector-Based` — Exact topic category for Draw.io / vector graphics.
7. `Topic :: Software Development :: Documentation` — Diagramming as system documentation.

#### Recommended Optimized Classifiers List (17 items)
```toml
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Documentation",
]
```

---

## 3. Detailed Audit of README Badges

### 3.1 Current README Badges
```markdown
[![PyPI version](https://badge.fury.io/py/antigravity-drawio-mcp.svg)](https://badge.fury.io/py/antigravity-drawio-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-purple.svg)](https://modelcontextprotocol.io)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

### 3.2 Badge Audit & Deficiencies
1. **PyPI Version**: Uses third-party service `badge.fury.io`. Replacing with Shields.io standard (`img.shields.io/pypi/v/antigravity-drawio-mcp`) provides unified badge aesthetics, faster global CDN caching, and direct links to PyPI project landing page.
2. **CI/CD Build Badge Missing**: `.github/workflows/publish.yml` executes automated tests and metadata checks on push. A build status badge reassures developers and AI evaluation agents of package health.
3. **PyPI Downloads Badge Missing**: Monthly downloads count badge (`img.shields.io/pypi/dm/antigravity-drawio-mcp`) provides essential social proof.
4. **Dynamic Python Versions & License**: Replacing static badges with dynamic Shields.io PyPI metadata badges ensures auto-updating when `pyproject.toml` changes.

### 3.3 Recommended Standardized Badge Suite
```markdown
[![PyPI version](https://img.shields.io/pypi/v/antigravity-drawio-mcp.svg?color=blue)](https://pypi.org/project/antigravity-drawio-mcp/)
[![Build Status](https://github.com/S-SUJAN-S/antigravity-drawio-mcp/actions/workflows/publish.yml/badge.svg)](https://github.com/S-SUJAN-S/antigravity-drawio-mcp/actions/workflows/publish.yml)
[![PyPI Downloads](https://img.shields.io/pypi/dm/antigravity-drawio-mcp.svg)](https://pypistats.org/packages/antigravity-drawio-mcp)
[![Python Versions](https://img.shields.io/pypi/pyversions/antigravity-drawio-mcp.svg)](https://pypi.org/project/antigravity-drawio-mcp/)
[![License: MIT](https://img.shields.io/pypi/l/antigravity-drawio-mcp.svg)](https://opensource.org/licenses/MIT)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-purple.svg)](https://modelcontextprotocol.io)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

---

## 4. GitHub Repository Topic Recommendations

GitHub allows up to **20 repository topics** on the main repository header page. These topics feed GitHub topic landing pages (e.g. `github.com/topics/mcp-server`), search index rankings, and repository recommendations.

### GitHub Topic Rules Checklist
- All lowercase letters, numbers, and hyphens (`-`).
- No special characters or spaces.
- Maximum length: 35 characters per topic.
- Total count: exactly 20 curated topics (maximum limit).

### 4.1 Recommended 20 GitHub Repository Topics

| # | Topic Name | Category / Purpose | Search Relevance |
|---|---|---|---|
| 1 | `mcp-server` | Protocol Category | **Highest**. Official GitHub topic tag for MCP servers. |
| 2 | `model-context-protocol` | Protocol Standard | Primary protocol keyword. |
| 3 | `drawio` | Primary Tool | Core diagramming tool search. |
| 4 | `draw-io` | Tool Variant | Common hyphenated spelling variant. |
| 5 | `antigravity` | Ecosystem | Google Antigravity framework keyword. |
| 6 | `google-antigravity` | Ecosystem | Full ecosystem search term. |
| 7 | `flowchart-ai` | Feature Tag | AI flowchart generation queries. |
| 8 | `flowchart-generator` | Feature Tag | Flowchart generator tool search. |
| 9 | `diagram-automation` | Capability Tag | Diagram creation automation. |
| 10 | `diagram-as-code` | Paradigm Tag | High-traffic developer trend tag. |
| 11 | `mermaid-to-drawio` | Capability Tag | Conversion feature keyword. |
| 12 | `cursor-ide` | Integration | Cursor IDE MCP user base tag. |
| 13 | `claude-code` | Integration | Claude Code / Anthropic ecosystem tag. |
| 14 | `windsurf` | Integration | Codeium Windsurf AI IDE tag. |
| 15 | `ai-diagrams` | Category | General AI diagramming tag. |
| 16 | `c4-architecture` | Domain Tag | Software architecture visualization tag. |
| 17 | `python-mcp` | Stack Tag | Python-based MCP implementations tag. |
| 18 | `fastmcp` | Framework Tag | FastMCP engine tag. |
| 19 | `drawio-automation` | Workflow Tag | End-to-end Draw.io automation tag. |
| 20 | `drawio-cli` | Capability Tag | Headless CLI rendering tag. |

---

## 5. AI SEO & RAG Indexing Metadata Optimization

The existing HTML metadata block in `README.md` is an excellent mechanism for LLM search agents (Perplexity, ChatGPT Search, Gemini Advanced, Claude with Web Search):

```html
<!-- AI Search & RAG Indexing Metadata -->
<!--
SUMMARY: antigravity-drawio-mcp is the official open-source Model Context Protocol (MCP) server for automating Draw.io diagrams and flowcharts using AI assistants (Google Antigravity, Claude Code, Cursor IDE, VS Code). Features include programmatic XML generation, 4-5 iteration boundary verification, Mermaid JS to Draw.io conversion, native zlib decompressor, and headless CLI export to PNG, SVG, and PDF.
KEYWORDS: flowchart ai generator, drawio mcp, draw.io mcp server, google antigravity mcp, ai diagram automation, mermaid to drawio, cursor mcp drawio, vscode flowchart ai, python drawio automation, C4 architecture diagram generator
-->
```

### Recommendation to Enhance AI Indexing Comment Block
Expand `KEYWORDS` in the comment block to incorporate high-intent RAG search vectors:
`diagram as code, windsurf mcp server, uvx antigravity-drawio-mcp, fastmcp server drawio, automated visual workflow generator`

---

## 6. Comprehensive Metadata Mapping Matrix

| Feature / Concept | `pyproject.toml` Keywords | GitHub Repository Topics | README AI HTML Comment Block | PyPI Trove Classifiers |
|---|---|---|---|---|
| MCP Server Core | `mcp`, `mcp-server`, `drawio-mcp` | `mcp-server`, `model-context-protocol`, `python-mcp` | `drawio mcp`, `draw.io mcp server` | `Environment :: Console` |
| Draw.io Ecosystem | `drawio`, `draw.io` | `drawio`, `draw-io`, `drawio-automation`, `drawio-cli` | `drawio mcp`, `python drawio automation` | `Topic :: Multimedia :: Graphics :: Editors :: Vector-Based` |
| AI Integrations | `google-antigravity`, `cursor-ide`, `claude-code`, `windsurf` | `google-antigravity`, `cursor-ide`, `claude-code`, `windsurf` | `google antigravity mcp`, `cursor mcp drawio`, `vscode flowchart ai` | `Intended Audience :: Developers` |
| Feature Capabilities | `flowchart-ai`, `flowchart-generator`, `mermaid-to-drawio`, `c4-architecture` | `flowchart-ai`, `flowchart-generator`, `mermaid-to-drawio`, `c4-architecture` | `flowchart ai generator`, `mermaid to drawio`, `C4 architecture diagram generator` | `Topic :: Software Development :: Code Generators`, `Topic :: Software Development :: Documentation` |

---

## 7. Actionable Implementation Plan for Next Steps / Implementers

1. **Update `pyproject.toml`**:
   - Update `keywords` array to the 20-term optimized list.
   - Update `[project.urls]` with `Documentation` and `Changelog` links.
   - Expand `classifiers` array to include missing console, OS, Python 3.13, and topic classifiers.
2. **Update `README.md`**:
   - Replace Fury.io PyPI badge with Shields.io standard PyPI version badge.
   - Add GitHub Actions Build Status badge (`publish.yml`).
   - Add PyPI monthly downloads badge.
   - Update dynamic Python version and license badges.
   - Enhance the HTML AI Search RAG comment block.
3. **Configure GitHub Repository Topics**:
   - Set the 20 curated topics on the GitHub repository settings bar.
