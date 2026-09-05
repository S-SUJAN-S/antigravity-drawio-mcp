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
    try:
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
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def export_diagram(input_path: str, output_path: str, format: str = "png", page_index: int = 1) -> str:
    """Export a .drawio XML diagram to PNG, SVG, PDF, or JPEG using desktop CLI."""
    try:
        res = DrawIOExporter.export(input_path, output_path, fmt=format, page_index=page_index)
        return json.dumps({"status": "success", "exported_path": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def open_in_drawio(input_path: str) -> str:
    """Open a .drawio diagram file directly in the local Draw.io Desktop GUI app."""
    try:
        msg = DrawIOExporter.open_in_app(input_path)
        return json.dumps({"status": "success", "message": msg})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def parse_diagram(input_path: str) -> str:
    """Parse a .drawio XML file and extract structured nodes, edges, and page metadata."""
    try:
        parser = DrawIOParser(input_path)
        parsed = parser.parse()
        return json.dumps({"status": "success", "data": parsed})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def convert_mermaid_to_drawio(mermaid_code: str, output_path: str) -> str:
    """Convert a Mermaid JS graph definition string into native .drawio XML."""
    try:
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_res)
        return json.dumps({"status": "success", "path": output_path})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def validate_diagram(input_path: str) -> str:
    """Audit a .drawio diagram file for node collisions and text boundary overflows."""
    try:
        audit = DrawIOVerifier.verify(input_path)
        return json.dumps({"status": "success", "audit": audit})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def resolve_diagram_collisions(input_path: str, output_path: str = None) -> str:
    """Auto-resolve node collisions in a .drawio diagram by shifting overlapping coordinates."""
    try:
        audit = DrawIOVerifier.auto_resolve(input_path, output_path=output_path)
        return json.dumps({"status": "success", "audit": audit})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# Register with FastMCP / MCPServer across both mcp 1.x and 2.x
mcp_available = False
mcp = None

try:
    # mcp >= 2.0.0
    from mcp.server.mcpserver import MCPServer as FastMCP
    mcp = FastMCP("Antigravity Draw.io MCP Server")
    mcp_available = True
except (ImportError, ModuleNotFoundError):
    try:
        # mcp < 2.0.0
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Antigravity Draw.io MCP Server")
        mcp_available = True
    except (ImportError, ModuleNotFoundError):
        mcp_available = False

if mcp_available and mcp is not None:
    mcp.tool()(create_diagram)
    mcp.tool()(export_diagram)
    mcp.tool()(open_in_drawio)
    mcp.tool()(parse_diagram)
    mcp.tool()(convert_mermaid_to_drawio)
    mcp.tool()(validate_diagram)
    mcp.tool()(resolve_diagram_collisions)

# Standard MCP 2024-11-05 Tool Schemas for fallback
FALLBACK_TOOLS = [
    {
        "name": "create_diagram",
        "description": "Create a new .drawio XML diagram file with nodes and edges.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output path for .drawio file"},
                "nodes": {"type": "array", "items": {"type": "object"}, "description": "List of node definitions"},
                "edges": {"type": "array", "items": {"type": "object"}, "description": "List of edge definitions"},
                "page_name": {"type": "string", "default": "Page-1", "description": "Page name"}
            },
            "required": ["output_path", "nodes", "edges"]
        }
    },
    {
        "name": "export_diagram",
        "description": "Export a .drawio XML diagram to PNG, SVG, PDF, or JPEG using desktop CLI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to input .drawio file"},
                "output_path": {"type": "string", "description": "Output image path"},
                "format": {"type": "string", "default": "png", "description": "Format: png, svg, pdf, jpg"},
                "page_index": {"type": "integer", "default": 1, "description": "Page index (1-based)"}
            },
            "required": ["input_path", "output_path"]
        }
    },
    {
        "name": "open_in_drawio",
        "description": "Open a .drawio diagram file directly in the local Draw.io Desktop GUI app.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to .drawio file"}
            },
            "required": ["input_path"]
        }
    },
    {
        "name": "parse_diagram",
        "description": "Parse a .drawio XML file and extract structured nodes, edges, and page metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to .drawio file"}
            },
            "required": ["input_path"]
        }
    },
    {
        "name": "convert_mermaid_to_drawio",
        "description": "Convert a Mermaid JS graph definition string into native .drawio XML.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mermaid_code": {"type": "string", "description": "Mermaid JS diagram definition"},
                "output_path": {"type": "string", "description": "Output path for .drawio file"}
            },
            "required": ["mermaid_code", "output_path"]
        }
    },
    {
        "name": "validate_diagram",
        "description": "Audit a .drawio diagram file for node collisions and text boundary overflows.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to .drawio file to validate"}
            },
            "required": ["input_path"]
        }
    },
    {
        "name": "resolve_diagram_collisions",
        "description": "Auto-resolve node collisions in a .drawio diagram by shifting overlapping coordinates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to .drawio file to resolve"},
                "output_path": {"type": "string", "description": "Optional output path (overwrites input if omitted)"}
            },
            "required": ["input_path"]
        }
    }
]

def run_stdio_fallback():
    """StdIO JSON-RPC 2.0 protocol fallback conforming strictly to MCP 2024-11-05."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")

            # Ignore notifications (no id)
            if req_id is None or (method and method.startswith("notifications/")):
                continue

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False}
                        },
                        "serverInfo": {
                            "name": "Antigravity Draw.io MCP Server",
                            "version": "1.1.4"
                        }
                    }
                }
            elif method == "ping":
                res = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": FALLBACK_TOOLS
                    }
                }
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
                elif tool_name == "resolve_diagram_collisions":
                    output = resolve_diagram_collisions(args["input_path"], output_path=args.get("output_path"))
                else:
                    output = json.dumps({"status": "error", "message": f"Unknown tool {tool_name}"})

                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": output}]
                    }
                }
            else:
                res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as err:
            err_res = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(err)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

def main():
    if mcp_available and mcp is not None:
        try:
            mcp.run("stdio")
        except TypeError:
            mcp.run()
    else:
        run_stdio_fallback()

if __name__ == "__main__":
    main()
