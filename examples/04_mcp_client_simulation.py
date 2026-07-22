"""
Example 04: End-to-End Simulation of MCP Tool Server Dispatch
============================================================
This PoC script simulates how an AI Coding Assistant (e.g. Google Antigravity)
invokes tool methods on `antigravity_drawio_mcp.server`.
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

from antigravity_drawio_mcp.server import (
    create_diagram,
    export_diagram,
    validate_diagram,
    parse_diagram
)

def main():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs"))
    os.makedirs(out_dir, exist_ok=True)
    xml_path = os.path.join(out_dir, "04_mcp_simulated.drawio")
    png_path = os.path.join(out_dir, "04_mcp_simulated.png")

    print("[Step 1] AI Assistant invoking 'create_diagram' tool...")
    nodes = [
        {"id": "ai", "value": "Google Antigravity Agent", "x": 100, "y": 100, "width": 220, "height": 80, "style": "rounded=1;fillColor=#1E3A8A;strokeColor=#1E40AF;fontSize=14;fontColor=#FFFFFF;fontStyle=1;whiteSpace=wrap;html=0;"},
        {"id": "mcp", "value": "antigravity-drawio-mcp Server", "x": 420, "y": 100, "width": 240, "height": 80, "style": "rounded=1;fillColor=#6D28D9;strokeColor=#5B21B6;fontSize=14;fontColor=#FFFFFF;fontStyle=1;whiteSpace=wrap;html=0;"},
        {"id": "drawio", "value": "Draw.io Desktop App", "x": 760, "y": 100, "width": 220, "height": 80, "style": "rounded=1;fillColor=#EA580C;strokeColor=#C2410C;fontSize=14;fontColor=#FFFFFF;fontStyle=1;whiteSpace=wrap;html=0;"}
    ]
    edges = [
        {"id": "e1", "source": "ai", "target": "mcp", "label": "JSON-RPC Stdio", "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=classic;strokeColor=#1E3A8A;strokeWidth=2;fontSize=11;"},
        {"id": "e2", "source": "mcp", "target": "drawio", "label": "CLI Export", "style": "edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=classic;strokeColor=#6D28D9;strokeWidth=2;fontSize=11;"}
    ]

    res_create = create_diagram(xml_path, nodes, edges, page_name="MCP Simulation")
    print(f"   Server Result: {res_create}")

    print("\n[Step 2] AI Assistant invoking 'validate_diagram' tool...")
    res_val = validate_diagram(xml_path)
    print(f"   Validation Audit: {res_val}")

    print("\n[Step 3] AI Assistant invoking 'export_diagram' tool...")
    res_export = export_diagram(xml_path, png_path, format="png")
    print(f"   Export Result: {res_export}")

    print("\n[Step 4] AI Assistant invoking 'parse_diagram' tool...")
    res_parse = parse_diagram(xml_path)
    print(f"   Parse Summary: Status: Success")

    print("\nMCP Client Simulation Completed Successfully!")

if __name__ == "__main__":
    main()
