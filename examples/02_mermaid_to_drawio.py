"""
Example 02: Converting Mermaid JS Syntax to Native Draw.io XML
============================================================
This PoC script demonstrates how to convert a standard Mermaid JS flowchart
definition into native, editable Draw.io XML elements.
"""

import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure src directory is in Python path
mcp_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, mcp_src)

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.exporter import DrawIOExporter

def main():
    print("[Step 1] Defining Mermaid JS Flowchart Definition...")
    mermaid_code = """
    graph TD
        A[User Input Request] --> B[FastMCP Server Protocol]
        B --> C[DrawIOBuilder XML Generator]
        B --> D[DrawIOParser Zlib Decoder]
        C --> E[DrawIOExporter Win32 CLI]
        D --> E
        E --> F[Rendered PNG / SVG Output]
    """
    print(mermaid_code)

    print("\n[Step 2] Converting Mermaid Code to Draw.io XML...")
    drawio_xml = MermaidToDrawIO.convert(mermaid_code)

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs"))
    os.makedirs(out_dir, exist_ok=True)
    xml_path = os.path.join(out_dir, "02_mermaid_converted.drawio")

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(drawio_xml)
    print(f"Saved Converted Draw.io XML: {xml_path}")

    print("\n[Step 3] Exporting Converted Diagram to PNG & SVG...")
    png_path = os.path.join(out_dir, "02_mermaid_converted.png")
    svg_path = os.path.join(out_dir, "02_mermaid_converted.svg")

    DrawIOExporter.export(xml_path, png_path, fmt="png")
    DrawIOExporter.export(xml_path, svg_path, fmt="svg")

    print(f"Exported PNG: {png_path}")
    print(f"Exported SVG: {svg_path}")
    print("\nMermaid Conversion PoC Completed Successfully!")

if __name__ == "__main__":
    main()
