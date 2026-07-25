import sys
import os
import re
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from test_m2_empirical import parse_generated_xml, check_node_collisions

def test_purely_nested_subgraph_identicity():
    print("=== STRESS TEST 1: Purely Nested Subgraph (Outer contains ONLY Inner) ===")
    mermaid_code = """
    graph TD
        subgraph outer [Outer Group]
            subgraph inner [Inner Group]
                A --> B
            end
        end
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    outer = nodes.get("outer")
    inner = nodes.get("inner")
    
    print(f"Inner: x={inner['x']}, y={inner['y']}, w={inner['width']}, h={inner['height']}")
    print(f"Outer: x={outer['x']}, y={outer['y']}, w={outer['width']}, h={outer['height']}")
    
    identical_container = (
        outer['x'] == inner['x'] and
        outer['y'] == inner['y'] and
        outer['width'] == inner['width'] and
        outer['height'] == inner['height']
    )
    print(f"Are outer and inner containers 100% identical/overlapping? {identical_container}")
    return identical_container

def test_complex_cycles():
    print("=== STRESS TEST 2: Complex Cycles & Topological Depths ===")
    # 3-node cycle (A -> B -> C -> A) with external entry X -> A and exit C -> Y
    mermaid_code = """
    graph TD
        X --> A
        A --> B
        B --> C
        C --> A
        C --> Y
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': x={n['x']}, y={n['y']}")
        
    collisions = check_node_collisions(nodes)
    print(f"Child node collisions: {len(collisions)}")
    
    # Check X depth progression: X (depth 0) < A (depth 1) < B (depth 2) < C (depth 3) < Y (depth 4)
    x_x = nodes["X"]["x"]
    x_a = nodes["A"]["x"]
    x_b = nodes["B"]["x"]
    x_c = nodes["C"]["x"]
    x_y = nodes["Y"]["x"]
    
    correct_order = (x_x < x_a < x_b < x_c < x_y)
    print(f"X coords: X={x_x}, A={x_a}, B={x_b}, C={x_c}, Y={x_y}")
    print(f"Strict X depth progression maintained: {correct_order}")
    return correct_order and len(collisions) == 0

def test_disconnected_subgraphs_and_collisions():
    print("=== STRESS TEST 3: Disconnected Parallel Subgraphs ===")
    mermaid_code = """
    graph TD
        subgraph g1 [Group 1]
            A1 --> A2
        end
        subgraph g2 [Group 2]
            B1 --> B2
        end
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': x={n['x']}, y={n['y']}, w={n['width']}, h={n['height']}")
        
    g1 = nodes.get("g1")
    g2 = nodes.get("g2")
    
    overlap_x = max(0, min(g1["x"] + g1["width"], g2["x"] + g2["width"]) - max(g1["x"], g2["x"]))
    overlap_y = max(0, min(g1["y"] + g1["height"], g2["y"] + g2["height"]) - max(g1["y"], g2["y"]))
    
    print(f"G1 bounds: [{g1['x']}, {g1['x']+g1['width']}], [{g1['y']}, {g1['y']+g1['height']}]")
    print(f"G2 bounds: [{g2['x']}, {g2['x']+g2['width']}], [{g2['y']}, {g2['y']+g2['height']}]")
    print(f"G1 and G2 overlap area: {overlap_x * overlap_y}")
    return (overlap_x * overlap_y) > 0

def test_multi_arrow_styles():
    print("=== STRESS TEST 4: Multi-hop Arrow Styles & Labels ===")
    mermaid_code = """
    graph LR
        A ==>|thick| B -.->|dotted| C -- label --> D
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes count: {len(nodes)}, Edges count: {len(edges)}")
    for e in edges:
        print(f"  Edge {e['id']}: {e['source']} -> {e['target']}, label='{e['label']}'")
        
    expected_edges = [("A", "B", "thick"), ("B", "C", "dotted"), ("C", "D", "label")]
    matched = True
    for src, tgt, lbl in expected_edges:
        found = any(e["source"] == src and e["target"] == tgt and e["label"] == lbl for e in edges)
        if not found:
            print(f"  MISSING EDGE: {src} -> {tgt} with label '{lbl}'")
            matched = False
    return matched

if __name__ == "__main__":
    r1 = test_purely_nested_subgraph_identicity()
    r2 = test_complex_cycles()
    r3 = test_disconnected_subgraphs_and_collisions()
    r4 = test_multi_arrow_styles()
    
    print(f"\nSTRESS TEST RESULTS:")
    print(f"1. Purely nested subgraphs collapse into identical bounds: {r1}")
    print(f"2. Complex cycles depth ordering: {r2}")
    print(f"3. Disconnected parallel subgraphs collide: {r3}")
    print(f"4. Multi-arrow styles & pipe labels: {r4}")
