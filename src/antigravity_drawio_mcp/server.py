import json
import os
import sys
from .builder import DrawIOBuilder
from .parser import DrawIOParser
from .exporter import DrawIOExporter
from .mermaid_converter import MermaidToDrawIO
from .verifier import DrawIOVerifier

# Core tool function definitions
def create_diagram(output_path: str, nodes: list, edges: list, page_name: str = "Page-1") -> str:
    """Create a new .drawio XML diagram file with nodes and edges."""
    builder = DrawIOBuilder(page_name=page_name)
    for n in nodes:
        builder.add_node(
            node_id=n.get("id"),
            value=n.get("value", ""),
            x=n.get("x", 100),
            y=n.get("y", 100),
            width=n.get("width", 140),
            height=n.get("height", 60),
            style=n.get("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;")
        )
    for e in edges:
        builder.add_edge(
            edge_id=e.get("id"),
            source=e.get("source"),
            target=e.get("target"),
            label=e.get("label", e.get("value", "")),
            style=e.get("style", "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;strokeColor=#000000;strokeWidth=1.5;")
        )
    saved = builder.save(output_path)
    return json.dumps({"status": "success", "path": saved})

def export_diagram(input_path: str, output_path: str, format: str = "png", page_index: int = 1) -> str:
    """Export a .drawio XML diagram to PNG, SVG, PDF, or JPEG using desktop CLI."""
    res = DrawIOExporter.export(input_path, output_path, fmt=format, page_index=page_index)
    return json.dumps({"status": "success", "exported_path": res})

def open_in_drawio(input_path: str) -> str:
    """Open a .drawio diagram file directly in the local Draw.io Desktop GUI app."""
    msg = DrawIOExporter.open_in_app(input_path)
    return json.dumps({"status": "success", "message": msg})

def parse_diagram(input_path: str) -> str:
    """Parse a .drawio XML file and extract structured nodes, edges, and page metadata."""
    parser = DrawIOParser(input_path)
    parsed = parser.parse()
    return json.dumps({"status": "success", "data": parsed})

def convert_mermaid_to_drawio(mermaid_code: str, output_path: str) -> str:
    """Convert a Mermaid JS graph definition string into native .drawio XML."""
    xml_res = MermaidToDrawIO.convert(mermaid_code)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_res)
    return json.dumps({"status": "success", "path": output_path})

def validate_diagram(input_path: str) -> str:
    """Audit a .drawio diagram file for node collisions and text boundary overflows."""
    audit = DrawIOVerifier.verify(input_path)
    return json.dumps({"status": "success", "audit": audit})

# Register with FastMCP if installed
try:
    from mcp.server.fastmcp import FastMCP
    mcp_available = True
except ImportError:
    mcp_available = False

if mcp_available:
    mcp = FastMCP("Antigravity Draw.io MCP Server", description="Bulletproof Draw.io MCP Server for AI coding assistants")
    mcp.tool()(create_diagram)
    mcp.tool()(export_diagram)
    mcp.tool()(open_in_drawio)
    mcp.tool()(parse_diagram)
    mcp.tool()(convert_mermaid_to_drawio)
    mcp.tool()(validate_diagram)

def run_stdio_fallback():
    """StdIO JSON protocol fallback for non-FastMCP environments."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")
            
            if method == "initialize":
                res = {"jsonrpc": "2.0", "id": req_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "Antigravity Draw.io MCP Server", "version": "1.0.0"}}}
            elif method == "tools/list":
                res = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [
                    {"name": "create_diagram", "description": "Create a new .drawio XML diagram file"},
                    {"name": "export_diagram", "description": "Export .drawio to PNG/SVG/PDF"},
                    {"name": "open_in_drawio", "description": "Open .drawio in desktop GUI"},
                    {"name": "parse_diagram", "description": "Parse .drawio XML into JSON"},
                    {"name": "convert_mermaid_to_drawio", "description": "Convert Mermaid JS to .drawio"},
                    {"name": "validate_diagram", "description": "Audit diagram for collisions & overflow"}
                ]}}
            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})
                
                if tool_name == "create_diagram":
                    output = create_diagram(args["output_path"], args.get("nodes", []), args.get("edges", []), args.get("page_name", "Page-1"))
                elif tool_name == "export_diagram":
                    output = export_diagram(args["input_path"], args["output_path"], format=args.get("format", "png"), page_index=args.get("page_index", 1))
                elif tool_name == "open_in_drawio":
                    output = open_in_drawio(args["input_path"])
                elif tool_name == "parse_diagram":
                    output = parse_diagram(args["input_path"])
                elif tool_name == "convert_mermaid_to_drawio":
                    output = convert_mermaid_to_drawio(args["mermaid_code"], args["output_path"])
                elif tool_name == "validate_diagram":
                    output = validate_diagram(args["input_path"])
                else:
                    output = json.dumps({"status": "error", "message": f"Unknown tool {tool_name}"})
                
                res = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": output}]}}
            else:
                res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
                
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as err:
            err_res = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(err)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

def main():
    if mcp_available:
        mcp.run()
    else:
        run_stdio_fallback()

if __name__ == "__main__":
    main()
