# 🚀 Proof of Concept (PoC) & Usage Examples (`antigravity-drawio-mcp`)

This directory contains standalone, runnable **Proof of Concept (PoC) Python scripts** demonstrating key workflows and procedures for using the `antigravity-drawio-mcp` package.

---

## 📁 Examples Overview

| File | PoC Procedure | Output Assets (`examples/outputs/`) |
| :--- | :--- | :--- |
| [`01_basic_architecture.py`](01_basic_architecture.py) | Programmatic 3-tier web architecture graph creation, verification, PNG & SVG rendering. | `01_basic_architecture.drawio`<br/>`01_basic_architecture.png`<br/>`01_basic_architecture.svg` |
| [`02_mermaid_to_drawio.py`](02_mermaid_to_drawio.py) | Converts a standard Mermaid JS flowchart definition string into native `.drawio` XML elements. | `02_mermaid_converted.drawio`<br/>`02_mermaid_converted.png`<br/>`02_mermaid_converted.svg` |
| [`03_parse_and_inspect.py`](03_parse_and_inspect.py) | Loads an existing `.drawio` XML diagram, transparently handles zlib stream decompression, and extracts nodes/edges. | Printed console structure report |
| [`04_mcp_client_simulation.py`](04_mcp_client_simulation.py) | Simulates how AI Assistants (e.g. Google Antigravity) dispatch Model Context Protocol (MCP) tool requests. | `04_mcp_simulated.drawio`<br/>`04_mcp_simulated.png` |

---

## ⚡ How to Run the Examples

### Prerequisites
Make sure `antigravity-drawio-mcp` is installed or linked in editable mode:
```bash
cd antigravity_drawio_mcp
pip install -e .
```

### Run All Examples
Run the entire example suite sequentially:
```bash
python examples/01_basic_architecture.py
python examples/02_mermaid_to_drawio.py
python examples/03_parse_and_inspect.py
python examples/04_mcp_client_simulation.py
```

---

## 🛠️ Code Snippets & Procedures

### 1. Programmatically Building a Diagram (`DrawIOBuilder`)
```python
from antigravity_drawio_mcp.builder import DrawIOBuilder
from antigravity_drawio_mcp.exporter import DrawIOExporter

# 1. Initialize Builder
builder = DrawIOBuilder(page_name="Architecture PoC", width=1400, height=900)

# 2. Add Nodes
builder.add_node("client", "Web Client\n(React)", x=80, y=180, width=200, height=90)
builder.add_node("server", "API Server\n(FastAPI)", x=380, y=180, width=200, height=90)

# 3. Add Edge Connectors
builder.add_edge("e1", "client", "server", label="HTTPS / REST")

# 4. Save XML & Export PNG/SVG
xml_path = builder.save("architecture.drawio")
DrawIOExporter.export(xml_path, "architecture.png", fmt="png")
```

### 2. Converting Mermaid JS Syntax (`MermaidToDrawIO`)
```python
from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO

mermaid_code = """
graph TD
    A[Client Request] --> B[FastMCP Server]
    B --> C[DrawIOBuilder Engine]
"""

drawio_xml = MermaidToDrawIO.convert(mermaid_code)
with open("mermaid_flowchart.drawio", "w") as f:
    f.write(drawio_xml)
```

### 3. Parsing & Inspecting Existing Diagrams (`DrawIOParser`)
```python
from antigravity_drawio_mcp.parser import DrawIOParser

parser = DrawIOParser("diagram.drawio")
data = parser.parse()

for page in data["pages"]:
    print(f"Page: {page['name']} | Nodes: {len(page['nodes'])} | Edges: {len(page['edges'])}")
```
