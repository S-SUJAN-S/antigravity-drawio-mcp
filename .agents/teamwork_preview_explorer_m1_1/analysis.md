# 📊 Keyword & AI SEO Discovery Audit — Strategy & Recommendations

**Project**: `antigravity-drawio-mcp`  
**Milestone**: Milestone 1 — Keyword & AI SEO Discovery Audit  
**Agent**: Explorer 1 (`teamwork_preview_explorer_m1_1`)  
**Date**: 2026-07-24  

---

## 1. Executive Summary

This audit evaluates the search engine optimization (SEO), AI/LLM retrieval-augmented generation (RAG) indexing readiness, and developer discovery performance of `antigravity-drawio-mcp`. While `README.md` and `pyproject.toml` possess solid foundational descriptions, critical gaps exist in target search term coverage, exact acceptance criteria keyphrases, H1/H2 header keyword density, microdata/schema markup, badge routing, and social metadata. 

By implementing the concrete recommendations detailed in this report, `antigravity-drawio-mcp` will achieve maximum discoverability across **PyPI**, **GitHub Search**, **Google/Bing Search**, **Smithery.ai / Glama MCP Registries**, and **AI search engines (Perplexity, Gemini, ChatGPT Search, Claude Code)**.

---

## 2. Target Keyword & AI/LLM Search Query Audit

### 2.1 Acceptance Criteria Keyword Coverage Analysis

| Target Keyphrase | Status in `README.md` | Status in `pyproject.toml` | Findings & Gap Analysis |
| :--- | :--- | :--- | :--- |
| **`Draw.io MCP`** | 🟡 Partial | 🟢 Present (`"drawio-mcp"`) | Present in Title (`Draw.io MCP Server`) and PyPI description, but missing in body H2 headings and natural paragraph variations. |
| **`Flowchart AI Generator`** | 🟢 Present | 🟢 Present (`"flowchart-generator"`) | Present in Title and Line 11 blockquote. Missing in H2 headers and feature anchor texts. |
| **`Google Antigravity MCP`** | 🔴 Missing (Exact) | 🟡 Split | "Google Antigravity" and "MCP" appear separately. The exact compound phrase `"Google Antigravity MCP"` is missing in visible body text and headings (only exists in an HTML comment block). |
| **`Architecture Diagram AI`** | 🔴 Missing (Exact) | 🟡 Split | Phrased as "Architecture Diagrams with AI" or "C4 architecture diagram generator". Lacks exact phrase match for RAG vector search. |

### 2.2 Target Developer Search Queries Audit

1. **`"flowchart ai"`**:
   - *Current Coverage*: Title has "Flowchart AI Generator"; keywords have `"flowchart-ai"`.
   - *Recommendation*: Add explicit natural language phrases like "flowchart AI tool", "AI flowchart generator", and "create flowcharts with AI" in body copy and FAQ.
2. **`"drawio ai"`**:
   - *Current Coverage*: Appears as `"drawio"` and `"ai"` separately.
   - *Recommendation*: Integrate `"drawio ai"` as a unified search phrase in section intros and PyPI package summary.
3. **`"drawio mcp"`**:
   - *Current Coverage*: Included in H1 as `Draw.io MCP Server` and in `pyproject.toml` as `drawio-mcp`.
   - *Recommendation*: Add variations `"Draw.io MCP server"` and `"MCP server for Draw.io"` in H2 headings.
4. **`"diagram automation"`**:
   - *Current Coverage*: Line 9 contains `Automate Draw.io Flowcharts...`; `pyproject.toml` contains `diagram-automation`.
   - *Recommendation*: Promote `"Diagram Automation"` into an H2 section header: `## 🤖 Diagram Automation & Flowchart AI Features`.
5. **`"mcp server drawio"`**:
   - *Current Coverage*: `Draw.io MCP Server` is used. Standard query order `"mcp server drawio"` is missing.
   - *Recommendation*: Add standard phrasing in intro paragraph: "...the official MCP server for Draw.io diagram automation..."
6. **`"antigravity mcp"`**:
   - *Current Coverage*: `Antigravity Draw.io MCP Server` and `antigravity-drawio-mcp` exist.
   - *Recommendation*: Include `"Google Antigravity MCP server"` in Section 2 H2 header and setup text.
7. **`"ai architecture diagram generator"`**:
   - *Current Coverage*: Absent as a continuous string.
   - *Recommendation*: Add exact string into `README.md` intro and Section 5 industry examples header.

---

## 3. Header Density & Structure Audit (H1 / H2 / H3)

### 3.1 Current Header Hierarchy Inspection

```
H1: 🎨 Flowchart AI Generator & Draw.io MCP Server (antigravity-drawio-mcp)
├── H2: ⚡ Quick Install
├── H2: 🏗️ System Architecture
├── H2: 🔑 Key Features & AI Capabilities
├── H2: 🔌 AI Assistant & IDE Setup (Google Antigravity, Cursor, Claude, VS Code)
│   ├── H3: 1. 🌐 Google Antigravity
│   ├── H3: 2. 🤖 Claude Desktop / Claude Code
│   ├── H3: 3. ⚡ Cursor IDE (Features -> MCP Servers)
│   └── H3: 4. 💻 VS Code / Continue.dev
├── H2: 🛠️ MCP Tools Reference
├── H2: 🎨 Real-World Industry Diagram Examples
│   ├── H3: 1. SystemVerilog UVM Layered Testbench Architecture
│   ├── H3: 2. Graphic Organizer Selection Flowchart
│   └── H3: 3. DE10-Advanced FPGA Design & CAD Tool Flow
├── H2: 🚀 Proof of Concept (PoC) & Runnable Examples
├── H2: ❓ Frequently Asked Questions (FAQ)
│   ├── H3: How do I use AI to generate Draw.io flowcharts?
│   ├── H3: Can I convert Mermaid.js graphs to native Draw.io files?
│   └── H3: Are generated Draw.io diagrams editable?
├── H2: 🧪 Testing & Verification
└── H2: 📄 License
```

### 3.2 Key Header Deficiencies

1. **Emoji Padding**: While visually appealing, lead emojis without plain text keywords immediately following them can reduce keyword relevance weights in strict AST parsers.
2. **Missing Core Keywords in H2s**: None of the H2 headers explicitly contain `"Google Antigravity MCP"`, `"Architecture Diagram AI"`, or `"Diagram Automation"`.
3. **Sub-Optimal Header Keyword Density**: Heading density for target search terms is low (1 H1 mention of Draw.io MCP, 0 H2 mentions of Antigravity MCP or Architecture Diagram AI).

### 3.3 Recommended Optimized Header Hierarchy

```markdown
# 🎨 Flowchart AI Generator & Draw.io MCP Server (`antigravity-drawio-mcp`)

## ⚡ Quick Install & Setup
## 🏗️ System Architecture & C4 Diagram Model
## 🤖 Flowchart AI Generator & Diagram Automation Capabilities
## 🔌 Google Antigravity MCP & AI Assistant Setup (Cursor, Claude, VS Code)
### 1. 🌐 Google Antigravity MCP Integration
### 2. 🤖 Claude Desktop & Claude Code MCP Setup
### 3. ⚡ Cursor IDE MCP Configuration
### 4. 💻 VS Code / Continue.dev Setup
## 🛠️ Draw.io MCP Server Tools Reference
## 🏛️ Architecture Diagram AI & Real-World Industry Examples
### 1. SystemVerilog UVM Layered Testbench Architecture
### 2. Graphic Organizer Selection Flowchart
### 3. DE10-Advanced FPGA Design & CAD Tool Flow
## 🚀 Flowchart AI Generator PoC & Runnable Examples
## ❓ Frequently Asked Questions (FAQ — Draw.io MCP & Flowchart AI)
## 🧪 Testing & Verification
## 📄 License
```

---

## 4. Microdata & Schema.org Structures Audit

### 4.1 Findings

- **Current Implementation**: `README.md` uses an HTML comment block (`<!-- AI Search & RAG Indexing Metadata -->`).
- **Deficiencies**:
  1. Standard Markdown parsers, GitHub preview renderers, and PyPI HTML generation tools strip `<!-- ... -->` comments during processing.
  2. Search engine crawlers (Googlebot, Bingbot) and AI web indexers (Perplexity Bot, GPTBot, ClaudeBot) give zero weight to stripped HTML comments.
  3. No structured schema (`Schema.org/SoftwareApplication` or `Schema.org/SoftwareSourceCode`) is present.

### 4.2 Recommendation 1: Structured JSON-LD Schema

Embed a valid Schema.org JSON-LD microdata block inside `README.md` (or HTML docs). Search engines and modern AI RAG engines parse embedded JSON-LD scripts directly:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "antigravity-drawio-mcp",
  "alternateName": ["Draw.io MCP", "Flowchart AI Generator", "Google Antigravity MCP", "Architecture Diagram AI"],
  "headline": "Flowchart AI Generator & Draw.io MCP Server",
  "description": "Production-grade Model Context Protocol (MCP) Server for Google Antigravity, Claude Code, Cursor, and VS Code to automate Draw.io flowcharts and architecture diagrams with AI.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Windows, macOS, Linux",
  "license": "https://opensource.org/licenses/MIT",
  "codeRepository": "https://github.com/S-SUJAN-S/antigravity-drawio-mcp",
  "programmingLanguage": "Python",
  "author": {
    "@type": "Person",
    "name": "SUJAN S"
  },
  "keywords": [
    "Draw.io MCP",
    "Flowchart AI Generator",
    "Google Antigravity MCP",
    "Architecture Diagram AI",
    "diagram automation",
    "mcp server drawio",
    "drawio ai",
    "flowchart ai"
  ]
}
</script>
```

### 4.3 Recommendation 2: Visible AI Assistant Summary Callout Card

Replace the HTML comment with a visible markdown summary block optimized for LLM RAG context windows:

```markdown
> 🤖 **AI Search & RAG Context Summary**  
> **`antigravity-drawio-mcp`** is the official open-source **Draw.io MCP Server** and **Flowchart AI Generator** connecting **Google Antigravity MCP**, Claude Code, Cursor, and VS Code. It provides automated **Architecture Diagram AI** generation, native `.drawio` XML building, 4-5 iteration boundary verification, Mermaid JS conversion, zlib decompression, and headless CLI export to PNG, SVG, and PDF.
```

---

## 5. PyPI Badge Markup Audit

### 5.1 Current Badge Audit

```markdown
[![PyPI version](https://badge.fury.io/py/antigravity-drawio-mcp.svg)](https://badge.fury.io/py/antigravity-drawio-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-purple.svg)](https://modelcontextprotocol.io)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

### 5.2 Deficiencies & Issues

1. **Outdated Badge Vendor**: `badge.fury.io` is used instead of standard `img.shields.io`. Fury.io badges often experience slow response times and redirect users to Fury rather than PyPI.
2. **PyPI Destination Routing**: The PyPI version badge link points to `https://badge.fury.io/py/antigravity-drawio-mcp` instead of the official PyPI package page `https://pypi.org/project/antigravity-drawio-mcp/`.
3. **Missing Metrics Badges**: Missing PyPI Monthly Downloads badge and official PyPI Python Versions badge, which build social proof and search authority on registry indexes.
4. **Missing GitHub Authority Badges**: Missing GitHub repository stars badge and CI/CD workflow status badge.

### 5.3 Recommended Optimized Badge Suite

```markdown
[![PyPI Version](https://img.shields.io/pypi/v/antigravity-drawio-mcp.svg?color=blue&style=flat-square)](https://pypi.org/project/antigravity-drawio-mcp/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/antigravity-drawio-mcp.svg?color=brightgreen&style=flat-square)](https://pypi.org/project/antigravity-drawio-mcp/)
[![Python Version](https://img.shields.io/pypi/pyversions/antigravity-drawio-mcp.svg?style=flat-square)](https://pypi.org/project/antigravity-drawio-mcp/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-purple.svg?style=flat-square)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/S-SUJAN-S/antigravity-drawio-mcp?style=social)](https://github.com/S-SUJAN-S/antigravity-drawio-mcp)
```

---

## 6. GitHub Topics & Repository Metadata Recommendations

### 6.1 Audit of `pyproject.toml` Keywords

Current `pyproject.toml` keywords array (15 entries):
`"mcp"`, `"drawio"`, `"antigravity"`, `"flowchart-ai"`, `"flowchart-generator"`, `"diagram-automation"`, `"model-context-protocol"`, `"ai-diagrams"`, `"architecture-diagram"`, `"mermaid-to-drawio"`, `"cursor-ide"`, `"claude-code"`, `"google-antigravity"`, `"fastmcp"`, `"drawio-mcp"`

### 6.2 Deficiencies

- Lacks the single most searched GitHub Topic tag for Model Context Protocol servers: `mcp-server`.
- Lacks acceptance criteria exact hyphenated tags: `google-antigravity-mcp`, `architecture-diagram-ai`.
- Lacks C4 architecture tags: `c4-model`.

### 6.3 Recommended GitHub Repository Topics (Set via GitHub UI / API)

1. `mcp-server` *(Primary GitHub topic for MCP servers)*
2. `drawio`
3. `drawio-mcp`
4. `antigravity`
5. `google-antigravity`
6. `google-antigravity-mcp`
7. `flowchart-ai`
8. `diagram-automation`
9. `architecture-diagram-ai`
10. `model-context-protocol`
11. `mermaid-to-drawio`
12. `c4-model`
13. `cursor-mcp`
14. `claude-mcp`

### 6.4 Updated `pyproject.toml` Keywords Block Recommendation

```toml
keywords = [
    "drawio-mcp",
    "mcp-server",
    "flowchart-ai",
    "flowchart-ai-generator",
    "google-antigravity-mcp",
    "architecture-diagram-ai",
    "diagram-automation",
    "model-context-protocol",
    "drawio",
    "antigravity",
    "google-antigravity",
    "mermaid-to-drawio",
    "c4-model",
    "cursor-mcp",
    "claude-mcp",
    "fastmcp"
]
```

---

## 7. OpenGraph & Social Preview Metadata Strategy

### 7.1 Current State
- `README.md` references `docs/architecture.png` inline.
- OpenGraph (`og:*`) and Twitter (`twitter:*`) HTML meta tags are absent.

### 7.2 Recommendations for OpenGraph Optimization

1. **Add HTML OpenGraph Metadata in `README.md`**:
```html
<meta property="og:title" content="Flowchart AI Generator & Draw.io MCP Server (antigravity-drawio-mcp)" />
<meta property="og:description" content="Automate Draw.io Flowcharts & Architecture Diagrams with AI. Official Google Antigravity MCP Server." />
<meta property="og:image" content="https://raw.githubusercontent.com/S-SUJAN-S/antigravity-drawio-mcp/main/docs/architecture.png" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Flowchart AI Generator & Draw.io MCP Server" />
<meta name="twitter:description" content="Automate Draw.io Flowcharts & Architecture Diagrams with AI using Google Antigravity MCP." />
<meta name="twitter:image" content="https://raw.githubusercontent.com/S-SUJAN-S/antigravity-drawio-mcp/main/docs/architecture.png" />
```

2. **Set GitHub Social Preview Image**:
   - Upload `docs/architecture.png` under GitHub Repository **Settings -> General -> Social Preview**.

---

## 8. Summary of Concrete Implementation Recommendations

1. **Update `README.md` Title & Paragraph 1**:
   - Ensure explicit mentions of `Draw.io MCP`, `Flowchart AI Generator`, `Google Antigravity MCP`, and `Architecture Diagram AI`.
2. **Re-structure H2 Headings**:
   - Embed target search queries into section titles while preserving clarity and emoji icons.
3. **Upgrade Badges**:
   - Switch from `badge.fury.io` to official `img.shields.io` PyPI version, PyPI downloads, Python versions, and GitHub stars badges pointing to official URLs.
4. **Implement JSON-LD Schema & Visible RAG Context Box**:
   - Replace HTML comment with JSON-LD `<script>` tag and visible RAG blockquote card.
5. **Sync `pyproject.toml` Keywords & GitHub Topics**:
   - Add `mcp-server`, `google-antigravity-mcp`, `architecture-diagram-ai`, and `c4-model`.

---

*Report prepared by Explorer 1 (`teamwork_preview_explorer_m1_1`) for Milestone 1.*
