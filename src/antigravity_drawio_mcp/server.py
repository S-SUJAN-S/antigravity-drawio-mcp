import json
import os
import sys
from .builder import DrawIOBuilder
from .parser import DrawIOParser
from .exporter import DrawIOExporter
from .mermaid_converter import MermaidToDrawIO
from .verifier import DrawIOVerifier
from .templates import (
    generate_smart_diagram as _generate_smart_diagram,
    generate_c4_diagram as _generate_c4_diagram,
    generate_er_diagram as _generate_er_diagram,
    generate_sequence_diagram as _generate_sequence_diagram
)
from .editor import DiagramEditor
from .analyzer import DiagramAnalyzer

# ============================================================================
# Advanced Declarative & Generative Tools (v2.0)
# ============================================================================

def generate_smart_diagram(output_path: str, nodes: list, edges: list, containers: list = None, layout_direction: str = "TB", theme: str = "modern_slate", title: str = "Architecture Diagram") -> str:
    """Generate a professionally themed, auto-laid-out diagram without calculating manual pixel coordinates."""
    try:
        res = _generate_smart_diagram(
            output_path=output_path,
            nodes=nodes,
            edges=edges,
            containers=containers,
            layout_direction=layout_direction,
            theme=theme,
            title=title
        )
        return json.dumps({"status": "success", "path": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def generate_c4_diagram(output_path: str, spec: dict) -> str:
    """Generate an official C4 architecture diagram (Context, Container, or Component view) with actors, systems, and boundaries."""
    try:
        res = _generate_c4_diagram(output_path=output_path, spec=spec)
        return json.dumps({"status": "success", "path": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def generate_er_diagram(output_path: str, spec: dict) -> str:
    """Generate a relational database ER schema diagram with tables, primary/foreign keys, types, and cardinalities."""
    try:
        res = _generate_er_diagram(output_path=output_path, spec=spec)
        return json.dumps({"status": "success", "path": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def generate_sequence_diagram(output_path: str, spec: dict) -> str:
    """Generate a UML sequence diagram with lifelines, sync/async call arrows, and return messages."""
    try:
        res = _generate_sequence_diagram(output_path=output_path, spec=spec)
        return json.dumps({"status": "success", "path": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def patch_diagram(drawio_path: str, operations: list, output_path: str = None) -> str:
    """Surgically patch an existing diagram: add/delete/update nodes, rewire edges, group into containers, or highlight paths."""
    try:
        res = DiagramEditor.patch(drawio_path=drawio_path, operations=operations, output_path=output_path)
        return json.dumps({"status": "success", "result": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def beautify_diagram(input_path: str, output_path: str = None, theme: str = "modern_slate", layout_direction: str = "TB") -> str:
    """Beautify any existing diagram by running topological auto-layout, resolving overlapping links, and applying modern themes."""
    try:
        res = DiagramEditor.beautify(drawio_path=input_path, output_path=output_path, theme=theme, layout_direction=layout_direction)
        return json.dumps({"status": "success", "result": res})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def analyze_diagram(input_path: str) -> str:
    """Analyze diagram topology: extracts entry points, sinks, feedback cycles, bottlenecks, and critical execution paths."""
    try:
        metrics = DiagramAnalyzer.analyze(drawio_path=input_path)
        return json.dumps({"status": "success", "metrics": metrics})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# ============================================================================
# Core & Utility Tools (v1.x Backward Compatible)
# ============================================================================

def create_diagram(output_path: str, nodes: list, edges: list, page_name: str = "Page-1") -> str:
    """Create a new .drawio XML diagram file with nodes and edges at specified coordinates."""
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

# ============================================================================
# MCP Server Registration across mcp 1.x and 2.x
# ============================================================================

mcp_available = False
mcp = None

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
    mcp = FastMCP("Antigravity Draw.io MCP Server")
    mcp_available = True
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Antigravity Draw.io MCP Server")
        mcp_available = True
    except (ImportError, ModuleNotFoundError):
        mcp_available = False

if mcp_available and mcp is not None:
    mcp.tool()(generate_smart_diagram)
    mcp.tool()(generate_c4_diagram)
    mcp.tool()(generate_er_diagram)
    mcp.tool()(generate_sequence_diagram)
    mcp.tool()(patch_diagram)
    mcp.tool()(beautify_diagram)
    mcp.tool()(analyze_diagram)
    mcp.tool()(create_diagram)
    mcp.tool()(export_diagram)
    mcp.tool()(open_in_drawio)
    mcp.tool()(parse_diagram)
    mcp.tool()(convert_mermaid_to_drawio)
    mcp.tool()(validate_diagram)
    mcp.tool()(resolve_diagram_collisions)

# ============================================================================
# Fallback Tool Schemas (14 Tools, MCP 2024-11-05 Specification)
# ============================================================================

FALLBACK_TOOLS = [
    {
        "name": "generate_smart_diagram",
        "description": "Generate a professionally themed, auto-laid-out diagram without calculating manual pixel coordinates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output path for the .drawio file"},
                "nodes": {"type": "array", "items": {"type": "object"}, "description": "List of node dicts with id, label, shape, role, group"},
                "edges": {"type": "array", "items": {"type": "object"}, "description": "List of edge dicts with source, target, label, style"},
                "containers": {"type": "array", "items": {"type": "object"}, "description": "Optional list of container swimlane dicts with id, title"},
                "layout_direction": {"type": "string", "default": "TB", "description": "Layout direction: TB, LR, BT, RL, or grid"},
                "theme": {"type": "string", "default": "modern_slate", "description": "Design theme: modern_slate, cyberpunk_dark, cloud_aws, cloud_gcp, cloud_azure, c4_model, ocean_breeze, monochrome"},
                "title": {"type": "string", "default": "Architecture Diagram", "description": "Title of the diagram page"}
            },
            "required": ["output_path", "nodes", "edges"]
        }
    },
    {
        "name": "generate_c4_diagram",
        "description": "Generate an official C4 architecture diagram (Context, Container, or Component view) with actors, systems, and boundaries.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output path for .drawio file"},
                "spec": {"type": "object", "description": "C4 architecture specification (people, systems, containers, components, boundaries, relations)"}
            },
            "required": ["output_path", "spec"]
        }
    },
    {
        "name": "generate_er_diagram",
        "description": "Generate a relational database ER schema diagram with tables, primary/foreign keys, types, and cardinalities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output path for .drawio file"},
                "spec": {"type": "object", "description": "ER schema specification (entities with fields and relationships)"}
            },
            "required": ["output_path", "spec"]
        }
    },
    {
        "name": "generate_sequence_diagram",
        "description": "Generate a UML sequence diagram with lifelines, sync/async call arrows, and return messages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output path for .drawio file"},
                "spec": {"type": "object", "description": "Sequence specification (participants, messages)"}
            },
            "required": ["output_path", "spec"]
        }
    },
    {
        "name": "patch_diagram",
        "description": "Surgically patch an existing diagram: add/delete/update nodes, rewire edges, group into containers, or highlight paths.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "drawio_path": {"type": "string", "description": "Path to input .drawio diagram file"},
                "operations": {"type": "array", "items": {"type": "object"}, "description": "List of patch operations: add_node, delete_node, update_node, add_edge, delete_edge, group_nodes, highlight_path"},
                "output_path": {"type": "string", "description": "Optional destination path (overwrites drawio_path if omitted)"}
            },
            "required": ["drawio_path", "operations"]
        }
    },
    {
        "name": "beautify_diagram",
        "description": "Beautify any existing diagram by running topological auto-layout, resolving overlapping links, and applying modern themes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to messy or legacy .drawio file"},
                "output_path": {"type": "string", "description": "Optional output path"},
                "theme": {"type": "string", "default": "modern_slate", "description": "Theme palette name"},
                "layout_direction": {"type": "string", "default": "TB", "description": "Layout direction: TB or LR"}
            },
            "required": ["input_path"]
        }
    },
    {
        "name": "analyze_diagram",
        "description": "Analyze diagram topology: extracts entry points, sinks, feedback cycles, bottlenecks, and critical execution paths.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to .drawio file to analyze"}
            },
            "required": ["input_path"]
        }
    },
    {
        "name": "create_diagram",
        "description": "Create a new .drawio XML diagram file with nodes and edges at specified coordinates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Output path for .drawio file"},
                "nodes": {"type": "array", "items": {"type": "object"}, "description": "List of node definitions with x, y, width, height"},
                "edges": {"type": "array", "items": {"type": "object"}, "description": "List of edge definitions with source, target"},
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

            # Ignore notifications
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
                            "version": "2.0.1"
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

                if tool_name == "generate_smart_diagram":
                    output = generate_smart_diagram(
                        output_path=args["output_path"],
                        nodes=args["nodes"],
                        edges=args["edges"],
                        containers=args.get("containers"),
                        layout_direction=args.get("layout_direction", "TB"),
                        theme=args.get("theme", "modern_slate"),
                        title=args.get("title", "Architecture Diagram")
                    )
                elif tool_name == "generate_c4_diagram":
                    output = generate_c4_diagram(args["output_path"], args["spec"])
                elif tool_name == "generate_er_diagram":
                    output = generate_er_diagram(args["output_path"], args["spec"])
                elif tool_name == "generate_sequence_diagram":
                    output = generate_sequence_diagram(args["output_path"], args["spec"])
                elif tool_name == "patch_diagram":
                    output = patch_diagram(args["drawio_path"], args["operations"], output_path=args.get("output_path"))
                elif tool_name == "beautify_diagram":
                    output = beautify_diagram(args["input_path"], output_path=args.get("output_path"), theme=args.get("theme", "modern_slate"), layout_direction=args.get("layout_direction", "TB"))
                elif tool_name == "analyze_diagram":
                    output = analyze_diagram(args["input_path"])
                elif tool_name == "create_diagram":
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
