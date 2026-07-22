"""
Example 01: Programmatically Building & Exporting a 3-Tier Web Architecture Diagram
================================================================-----------------
This PoC script demonstrates how to use `antigravity_drawio_mcp` to:
1. Construct a 3-tier web architecture diagram using `DrawIOBuilder`.
2. Audit the diagram for overlapping nodes using `DrawIOVerifier`.
3. Export the diagram to high-resolution PNG and SVG using `DrawIOExporter`.
"""

import os
import sys

# Ensure sys.stdout handles UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure src directory is in Python path
mcp_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, mcp_src)

from antigravity_drawio_mcp.builder import DrawIOBuilder
from antigravity_drawio_mcp.exporter import DrawIOExporter
from antigravity_drawio_mcp.verifier import DrawIOVerifier

def main():
    print("[Step 1] Constructing 3-Tier Web Architecture Diagram...")
    builder = DrawIOBuilder(page_name="Web Architecture PoC", width=1400, height=900)

    # 1. Add Client Tier
    builder.add_node(
        node_id="client",
        value="Web Browser Client\n(React SPA)",
        x=80, y=180, width=200, height=90,
        style="rounded=1;whiteSpace=wrap;html=0;fillColor=#1E3A8A;strokeColor=#1E40AF;strokeWidth=2;fontSize=14;fontColor=#FFFFFF;fontStyle=1;spacing=8;"
    )

    # 2. Add API Gateway Tier
    builder.add_node(
        node_id="gateway",
        value="API Gateway\n(NGINX / Reverse Proxy)",
        x=380, y=180, width=220, height=90,
        style="rounded=1;whiteSpace=wrap;html=0;fillColor=#0F172A;strokeColor=#334155;strokeWidth=2;fontSize=14;fontColor=#FFFFFF;fontStyle=1;spacing=8;"
    )

    # 3. Add Microservices Tier
    builder.add_node(
        node_id="auth_service",
        value="Auth Service\n(FastAPI / OAuth2)",
        x=700, y=100, width=200, height=80,
        style="rounded=1;whiteSpace=wrap;html=0;fillColor=#6D28D9;strokeColor=#5B21B6;strokeWidth=1.5;fontSize=13;fontColor=#FFFFFF;fontStyle=1;spacing=6;"
    )
    builder.add_node(
        node_id="data_service",
        value="Core Data Service\n(Python FastAPI)",
        x=700, y=260, width=200, height=80,
        style="rounded=1;whiteSpace=wrap;html=0;fillColor=#2563EB;strokeColor=#1D4ED8;strokeWidth=1.5;fontSize=13;fontColor=#FFFFFF;fontStyle=1;spacing=6;"
    )

    # 4. Add Database Tier
    builder.add_node(
        node_id="database",
        value="Primary Database\n(PostgreSQL 16 Cluster)",
        x=1020, y=180, width=220, height=90,
        style="rounded=1;whiteSpace=wrap;html=0;fillColor=#059669;strokeColor=#047857;strokeWidth=2;fontSize=14;fontColor=#FFFFFF;fontStyle=1;spacing=8;"
    )

    # 5. Connect Edges
    builder.add_edge("e1", "client", "gateway", label="HTTPS / JSON", style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;endArrow=classic;strokeColor=#1E3A8A;strokeWidth=2;fontSize=11;fontStyle=1;")
    builder.add_edge("e2", "gateway", "auth_service", label="gRPC", style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;endArrow=classic;strokeColor=#6D28D9;strokeWidth=1.5;fontSize=11;")
    builder.add_edge("e3", "gateway", "data_service", label="REST API", style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;endArrow=classic;strokeColor=#2563EB;strokeWidth=1.5;fontSize=11;")
    builder.add_edge("e4", "data_service", "database", label="SQL Connection", style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;endArrow=classic;strokeColor=#059669;strokeWidth=2;fontSize=11;")

    # Save to outputs directory
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs"))
    os.makedirs(out_dir, exist_ok=True)
    
    xml_path = os.path.join(out_dir, "01_basic_architecture.drawio")
    builder.save(xml_path)
    print(f"Saved Draw.io XML to: {xml_path}")

    # Audit check
    print("\n[Step 2] Auditing diagram layout with DrawIOVerifier...")
    audit = DrawIOVerifier.verify(xml_path)
    print(f"   Nodes Found: {audit['node_count']}")
    print(f"   Edges Found: {audit['edge_count']}")
    print(f"   Clean Layout: {audit['is_clean']}")

    # Export to PNG and SVG
    print("\n[Step 3] Exporting PNG & SVG via DrawIOExporter...")
    png_path = os.path.join(out_dir, "01_basic_architecture.png")
    svg_path = os.path.join(out_dir, "01_basic_architecture.svg")
    
    DrawIOExporter.export(xml_path, png_path, fmt="png")
    DrawIOExporter.export(xml_path, svg_path, fmt="svg")

    print(f"Exported PNG: {png_path}")
    print(f"Exported SVG: {svg_path}")
    print("\nBasic Architecture PoC Completed Successfully!")

if __name__ == "__main__":
    main()
