# 🎨 Antigravity Draw.io MCP Server (`antigravity-drawio-mcp`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-purple.svg)](https://modelcontextprotocol.io)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Production-grade **Model Context Protocol (MCP) Server** framework connecting **Google Antigravity**, LLM agents, and IDE tools to the **Draw.io Desktop App** and native CLI environment.

---

## 🏗️ System Architecture

![Antigravity Draw.io MCP Architecture](docs/architecture.png)

The `antigravity-drawio-mcp` framework is structured into a 3-tier C4 Software Component Architecture (Level 3):

1. **Software System Boundary (AI Clients)**: Communicates via standard JSON-RPC 2.0 over Stdio transport with Google Antigravity Core Agent or any MCP-compatible IDE (VS Code, Cursor, Claude Desktop, Windsurf).
2. **Container: Antigravity Draw.io MCP Server (`src/antigravity_drawio_mcp`)**:
   - `FastMCP Request Handler`: FastMCP protocol engine and tool request dispatcher.
   - `Draw.io XML Builder`: Programmatic XML DOM construction and geometry engine.
   - `Draw.io File Parser`: Direct `.drawio` XML parsing & native zlib/base64 decompressor.
   - `CLI Export Engine`: Process lock manager and Draw.io desktop CLI wrapper (`--export`).
   - `Diagram Validator`: Automated collision detector & label boundary auditor.
   - `Mermaid Conversion Engine`: Bi-directional Mermaid JS to Draw.io converter.
3. **External Systems & Storage**: Interoperates with local `draw.io.exe` for headless image rendering (PNG, SVG, PDF) and persistent file storage.

---

## ⚡ Key Features

- 🎨 **Programmatic XML Construction**: Build complex multi-page Draw.io diagrams natively in Python without external dependencies.
- 🖼️ **Headless Image Rendering**: Instant export to PNG, SVG, PDF, or JPEG using local `draw.io.exe` desktop CLI integration.
- 🖥️ **Desktop GUI Interop**: Automatically launch generated `.drawio` files directly in the Draw.io Desktop application.
- 🔍 **Native Zlib Parsing**: Inspect existing Draw.io diagrams, automatically decompressing compressed XML streams.
- 🔄 **Mermaid JS Bridge**: Convert standard Mermaid JS graphs straight into native Draw.io XML cells.
- 🛡️ **Automated Boundary Verification**: Audit diagrams for overlapping nodes, text bounds, and broken edge paths.

---

## 🔌 Integration Guidelines (AI Assistants & IDEs)

For detailed step-by-step setup guides, refer to the [**Integration Guide**](docs/INTEGRATION_GUIDE.md).

### Quick Setup Snippets

#### 🌐 Google Antigravity (`~/.gemini/config/mcp_config.json`)
```json
{
  "mcpServers": {
    "drawio": {
      "command": "uvx",
      "args": ["antigravity-drawio-mcp"]
    }
  }
}
```
*Or using standard python:*
```json
{
  "mcpServers": {
    "drawio": {
      "command": "python",
      "args": ["-m", "antigravity_drawio_mcp.server"]
    }
  }
}
```

#### 🤖 Claude Desktop / Claude Code (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "antigravity_drawio": {
      "command": "python",
      "args": ["-m", "antigravity_drawio_mcp.server"]
    }
  }
}
```

#### ⚡ Cursor IDE (Features -> MCP Servers)
- **Command**: `python -m antigravity_drawio_mcp.server`

---

## 🎨 Real-World Industry Diagrams & Replications

`antigravity-drawio-mcp` powers production-grade architectural diagrams across hardware, software, and decision-tree domains:

### 1. SystemVerilog UVM Layered Testbench Architecture
![SystemVerilog UVM Testbench](docs/real_world_examples/project_01_uvm_testbench.png)
*IEEE 1800 Object-Oriented Verification Framework diagram featuring Driver, Monitor, Sequencer, Scoreboard, and DUT Interface layers.*

### 2. Graphic Organizer Selection Flowchart
![Graphic Organizer Decision Flowchart](docs/real_world_examples/project_03_graphic_organizer.png)
*27-node decision flowchart mapping complex pedagogical visual learning structures.*

### 3. DE10-Advanced FPGA Design & CAD Tool Flow
![DE10-Advanced FPGA Design Flow](docs/real_world_examples/project_04_fpga_flow.png)
*Intel Quartus Prime CAD compilation, System Builder, and FPGA programming workflow.*

---

## 🚀 Proof of Concept (PoC) & Examples

Comprehensive Python PoC scripts are available in the [`examples/`](examples/) directory:

| Example Script | Procedure Demonstrated |
| :--- | :--- |
| [`examples/01_basic_architecture.py`](examples/01_basic_architecture.py) | Programmatic 3-tier web architecture graph creation, verification, PNG & SVG rendering. |
| [`examples/02_mermaid_to_drawio.py`](examples/02_mermaid_to_drawio.py) | Converts a standard Mermaid JS flowchart definition string into native `.drawio` XML elements. |
| [`examples/03_parse_and_inspect.py`](examples/03_parse_and_inspect.py) | Loads an existing `.drawio` XML diagram, transparently handles zlib stream decompression, and extracts nodes/edges. |
| [`examples/04_mcp_client_simulation.py`](examples/04_mcp_client_simulation.py) | Simulates how AI Assistants (e.g. Google Antigravity) dispatch Model Context Protocol (MCP) tool requests. |

---

## 🚀 Production Publishing

For complete production release steps, refer to the [**Publishing Guide**](docs/PUBLISHING_GUIDE.md).

```bash
# 1. Build distribution wheel & sdist
python -m build

# 2. Upload to PyPI via Twine
python -m twine upload dist/*
```

---

## 📦 Installation

### From PyPI
```bash
pip install antigravity-drawio-mcp
```

### From Source (Development)
```bash
git clone https://github.com/S-SUJAN-S/antigravity-drawio-mcp.git
cd antigravity-drawio-mcp
pip install -e .
```

---

## 🛠️ MCP Tools Reference

The `antigravity-drawio-mcp` server exposes 7 production tools over Model Context Protocol:

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `create_diagram` | `output_path`, `nodes`, `edges`, `page_name` | Generates a native `.drawio` XML diagram file from structured JSON nodes & edges. |
| `export_diagram` | `input_path`, `output_path`, `format`, `page_index` | Renders a `.drawio` file to high-res PNG, vector SVG, PDF, or JPEG via Draw.io CLI. |
| `open_in_drawio` | `input_path` | Launches the specified `.drawio` file directly inside Draw.io Desktop GUI. |
| `parse_diagram` | `input_path` | Parses raw or zlib-compressed `.drawio` XML files and extracts node/edge data. |
| `convert_mermaid_to_drawio` | `mermaid_code`, `output_path` | Converts Mermaid JS flowchart syntax directly to a `.drawio` file. |
| `validate_diagram` | `input_path` | Audits a diagram for node collisions, layout overlaps, and text clipping issues. |

---

## 🧪 Testing & Verification

Run the comprehensive unit test suite:

```bash
python -m unittest tests/test_mcp_server.py
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).
