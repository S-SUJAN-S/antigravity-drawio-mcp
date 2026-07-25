import sys
import os
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from test_m2_empirical import parse_generated_xml, check_node_collisions

def run_all_checks():
    results = {}
    
    # 1. User Request Cyclic Graph
    code1 = """
    graph TD
        A --> B
        A --> C
        B --> D
        C --> D
        D --> A
    """
    xml1 = MermaidToDrawIO.convert(code1)
    nodes1, edges1 = parse_generated_xml(xml1)
    colls1 = check_node_collisions(nodes1)
    
    results["test_1"] = {
        "nodes": {nid: (n["x"], n["y"]) for nid, n in sorted(nodes1.items())},
        "edges_count": len(edges1),
        "collisions": len(colls1),
        "delta_x_0_1": nodes1["B"]["x"] - nodes1["A"]["x"],
        "delta_x_1_2": nodes1["D"]["x"] - nodes1["B"]["x"],
        "passed": (
            nodes1["A"]["x"] == 80.0 and
            nodes1["B"]["x"] == 330.0 and
            nodes1["C"]["x"] == 330.0 and
            nodes1["D"]["x"] == 580.0 and
            nodes1["B"]["y"] != nodes1["C"]["y"] and
            len(colls1) == 0
        )
    }
    
    # 2. Parallel Subgraphs
    code2 = """
    graph TD
        subgraph sg1 [Frontend]
            A[UI] --> B[State]
        end
        subgraph sg2 [Backend]
            C[API] --> D[DB]
        end
        B --> C
    """
    xml2 = MermaidToDrawIO.convert(code2)
    nodes2, _ = parse_generated_xml(xml2)
    colls2 = check_node_collisions(nodes2, include_swimlanes=False)
    results["test_2"] = {
        "sg1_bounds": (nodes2["sg1"]["x"], nodes2["sg1"]["y"], nodes2["sg1"]["width"], nodes2["sg1"]["height"]),
        "sg2_bounds": (nodes2["sg2"]["x"], nodes2["sg2"]["y"], nodes2["sg2"]["width"], nodes2["sg2"]["height"]),
        "child_collisions": len(colls2),
        "passed": len(colls2) == 0
    }

    # 3. Nested Subgraphs
    code3 = """
    graph TD
        subgraph outer [Outer System]
            subgraph inner [Inner Core]
                A[Core Node 1] --> B[Core Node 2]
            end
        end
    """
    xml3 = MermaidToDrawIO.convert(code3)
    nodes3, _ = parse_generated_xml(xml3)
    inner3 = nodes3["inner"]
    outer3 = nodes3["outer"]
    
    results["test_3"] = {
        "inner_bounds": (inner3["x"], inner3["y"], inner3["width"], inner3["height"]),
        "outer_bounds": (outer3["x"], outer3["y"], outer3["width"], outer3["height"]),
        "identical": (
            inner3["x"] == outer3["x"] and
            inner3["y"] == outer3["y"] and
            inner3["width"] == outer3["width"] and
            inner3["height"] == outer3["height"]
        ),
        "passed": False # Fails due to identical overlapping containers
    }
    
    return results

if __name__ == "__main__":
    res = run_all_checks()
    print("CONSOLIDATED SUMMARY:")
    for k, v in res.items():
        print(f"  {k}: {v}")
