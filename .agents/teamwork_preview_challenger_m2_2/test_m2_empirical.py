import sys
import os
import re
import xml.etree.ElementTree as ET

# Add project src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO

def parse_generated_xml(xml_str):
    """
    Parses Draw.io XML and extracts nodes (vertices) and edges with geometry.
    Returns:
        nodes: dict of node_id -> {value, x, y, width, height, style, is_swimlane}
        edges: list of {id, source, target, label, style}
    """
    root = ET.fromstring(xml_str)
    nodes = {}
    edges = []
    
    for cell in root.iter("mxCell"):
        cid = cell.attrib.get("id")
        if cid in ("0", "1"):
            continue
            
        is_vertex = cell.attrib.get("vertex") == "1"
        is_edge = cell.attrib.get("edge") == "1"
        
        geo = cell.find("mxGeometry")
        
        if is_vertex and geo is not None:
            style = cell.attrib.get("style", "")
            is_swimlane = "swimlane" in style
            nodes[cid] = {
                "id": cid,
                "value": cell.attrib.get("value", ""),
                "x": float(geo.attrib.get("x", 0)),
                "y": float(geo.attrib.get("y", 0)),
                "width": float(geo.attrib.get("width", 0)),
                "height": float(geo.attrib.get("height", 0)),
                "style": style,
                "is_swimlane": is_swimlane
            }
        elif is_edge:
            edges.append({
                "id": cid,
                "source": cell.attrib.get("source"),
                "target": cell.attrib.get("target"),
                "label": cell.attrib.get("value", ""),
                "style": cell.attrib.get("style", "")
            })
            
    return nodes, edges

def check_node_collisions(nodes, include_swimlanes=False):
    """
    Checks if any two nodes collide (overlap in bounding box).
    Returns list of collision descriptions.
    """
    target_nodes = [n for n in nodes.values() if include_swimlanes or not n["is_swimlane"]]
    collisions = []
    
    for i in range(len(target_nodes)):
        for j in range(i + 1, len(target_nodes)):
            n1 = target_nodes[i]
            n2 = target_nodes[j]
            
            # Check bounding box overlap
            n1_left, n1_right = n1["x"], n1["x"] + n1["width"]
            n1_top, n1_bottom = n1["y"], n1["y"] + n1["height"]
            
            n2_left, n2_right = n2["x"], n2["x"] + n2["width"]
            n2_top, n2_bottom = n2["y"], n2["y"] + n2["height"]
            
            overlap_x = max(0, min(n1_right, n2_right) - max(n1_left, n2_left))
            overlap_y = max(0, min(n1_bottom, n2_bottom) - max(n1_top, n2_top))
            
            if overlap_x > 0 and overlap_y > 0:
                collisions.append({
                    "node1": n1["id"],
                    "node2": n2["id"],
                    "overlap_w": overlap_x,
                    "overlap_h": overlap_y,
                    "area": overlap_x * overlap_y
                })
                
    return collisions

def test_user_requested_graph():
    print("=== TEST 1: Branching & Cyclic Graph (A -> B, A -> C, B -> D, C -> D, D -> A) ===")
    mermaid_code = """
    graph TD
        A --> B
        A --> C
        B --> D
        C --> D
        D --> A
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': x={n['x']}, y={n['y']}, w={n['width']}, h={n['height']}")
        
    print(f"Edges found ({len(edges)}):")
    for e in edges:
        print(f"  Edge '{e['id']}': {e['source']} -> {e['target']} (label='{e['label']}')")
        
    # Check depth positions
    # Expected: A at x=80 (depth 0), B & C at x=330 (depth 1), D at x=580 (depth 2)
    depth_0_x = nodes["A"]["x"]
    depth_1_x_b = nodes["B"]["x"]
    depth_1_x_c = nodes["C"]["x"]
    depth_2_x = nodes["D"]["x"]
    
    diff_0_1 = depth_1_x_b - depth_0_x
    diff_1_2 = depth_2_x - depth_1_x_b
    
    print(f"Depth 0 x: {depth_0_x}")
    print(f"Depth 1 x (B): {depth_1_x_b}, (C): {depth_1_x_c}")
    print(f"Depth 2 x (D): {depth_2_x}")
    print(f"Delta depth 0->1: {diff_0_1}")
    print(f"Delta depth 1->2: {diff_1_2}")
    
    collisions = check_node_collisions(nodes)
    print(f"Collisions among non-swimlane nodes: {len(collisions)}")
    if collisions:
        for c in collisions:
            print(f"  COLLISION: {c['node1']} and {c['node2']} overlap area={c['area']}")
            
    pass_test = (
        depth_0_x == 80.0 and
        depth_1_x_b == 330.0 and
        depth_1_x_c == 330.0 and
        depth_2_x == 580.0 and
        diff_0_1 == 250.0 and
        diff_1_2 == 250.0 and
        nodes["B"]["y"] != nodes["C"]["y"] and
        len(collisions) == 0
    )
    print(f"TEST 1 RESULT: {'PASS' if pass_test else 'FAIL'}\n")
    return pass_test

def test_shape_and_multihop():
    print("=== TEST 2: Shape Syntax & Multi-Hop Chain ===")
    mermaid_code = """
    graph LR
        A{Decision} --> B(Rounded) --> C[Rectangle]
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': label='{n['value']}', x={n['x']}, y={n['y']}, style='{n['style']}'")
        
    print(f"Edges found ({len(edges)}):")
    for e in edges:
        print(f"  Edge '{e['id']}': {e['source']} -> {e['target']}")
        
    rhombus_ok = "rhombus" in nodes["A"]["style"]
    rounded_ok = "rounded=1" in nodes["B"]["style"]
    rect_ok = "rounded=0" in nodes["C"]["style"]
    
    edge_ab = any(e["source"] == "A" and e["target"] == "B" for e in edges)
    edge_bc = any(e["source"] == "B" and e["target"] == "C" for e in edges)
    
    print(f"Shape A (rhombus): {rhombus_ok}")
    print(f"Shape B (rounded): {rounded_ok}")
    print(f"Shape C (rectangle): {rect_ok}")
    print(f"Edges parsed: A->B ({edge_ab}), B->C ({edge_bc})")
    
    collisions = check_node_collisions(nodes)
    pass_test = rhombus_ok and rounded_ok and rect_ok and edge_ab and edge_bc and len(collisions) == 0
    print(f"TEST 2 RESULT: {'PASS' if pass_test else 'FAIL'}\n")
    return pass_test

def test_single_subgraph():
    print("=== TEST 3: Single Subgraph Container Bounds & Child Nodes ===")
    mermaid_code = """
    graph TD
        subgraph sg1 [Service Group]
            A[Service A] --> B[Service B]
        end
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': is_swimlane={n['is_swimlane']}, x={n['x']}, y={n['y']}, w={n['width']}, h={n['height']}")
        
    sg = nodes.get("sg1")
    node_a = nodes.get("A")
    node_b = nodes.get("B")
    
    if not (sg and node_a and node_b):
        print("FAIL: Missing nodes or subgraph container")
        return False
        
    # Verify sg bounds enclose A and B
    min_x = min(node_a["x"], node_b["x"])
    max_x_end = max(node_a["x"] + node_a["width"], node_b["x"] + node_b["width"])
    min_y = min(node_a["y"], node_b["y"])
    max_y_end = max(node_a["y"] + node_a["height"], node_b["y"] + node_b["height"])
    
    encloses_x = (sg["x"] <= min_x) and (sg["x"] + sg["width"] >= max_x_end)
    encloses_y = (sg["y"] <= min_y) and (sg["y"] + sg["height"] >= max_y_end)
    
    print(f"Child bounds: X=[{min_x}, {max_x_end}], Y=[{min_y}, {max_y_end}]")
    print(f"Container bounds: X=[{sg['x']}, {sg['x'] + sg['width']}], Y=[{sg['y']}, {sg['y'] + sg['height']}]")
    print(f"Encloses X: {encloses_x}, Encloses Y: {encloses_y}")
    
    collisions = check_node_collisions(nodes, include_swimlanes=False)
    pass_test = encloses_x and encloses_y and len(collisions) == 0
    print(f"TEST 3 RESULT: {'PASS' if pass_test else 'FAIL'}\n")
    return pass_test

def test_multiple_subgraphs():
    print("=== TEST 4: Multiple Subgraphs Bounds & Collisions ===")
    mermaid_code = """
    graph TD
        subgraph sg1 [Frontend]
            A[UI Component] --> B[State Store]
        end
        subgraph sg2 [Backend]
            C[API Gateway] --> D[Database]
        end
        B --> C
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': swimlane={n['is_swimlane']}, x={n['x']}, y={n['y']}, w={n['width']}, h={n['height']}")
        
    sg1 = nodes.get("sg1")
    sg2 = nodes.get("sg2")
    
    # Check node collisions (child nodes)
    child_collisions = check_node_collisions(nodes, include_swimlanes=False)
    print(f"Child node collisions: {len(child_collisions)}")
    
    # Check if sg1 and sg2 swimlanes overlap each other
    swimlane_collisions = []
    if sg1 and sg2:
        overlap_x = max(0, min(sg1["x"] + sg1["width"], sg2["x"] + sg2["width"]) - max(sg1["x"], sg2["x"]))
        overlap_y = max(0, min(sg1["y"] + sg1["height"], sg2["y"] + sg2["height"]) - max(sg1["y"], sg2["y"]))
        if overlap_x > 0 and overlap_y > 0:
            swimlane_collisions.append((sg1["id"], sg2["id"], overlap_x, overlap_y))
            print(f"  SWIMLANE COLLISION: {sg1['id']} and {sg2['id']} overlap by w={overlap_x}, h={overlap_y}")
            
    pass_test = len(child_collisions) == 0 and len(swimlane_collisions) == 0
    print(f"TEST 4 RESULT: {'PASS' if pass_test else 'FAIL'}\n")
    return pass_test

def test_nested_subgraphs():
    print("=== TEST 5: Nested Subgraphs Swimlane Container Bounds & Collisions ===")
    mermaid_code = """
    graph TD
        subgraph outer [Outer System]
            subgraph inner [Inner Core]
                A[Core Node 1] --> B[Core Node 2]
            end
            C[Peripheral Node]
        end
    """
    xml_str = MermaidToDrawIO.convert(mermaid_code)
    nodes, edges = parse_generated_xml(xml_str)
    
    print(f"Nodes found ({len(nodes)}):")
    for nid, n in sorted(nodes.items()):
        print(f"  Node '{nid}': swimlane={n['is_swimlane']}, x={n['x']}, y={n['y']}, w={n['width']}, h={n['height']}")
        
    outer = nodes.get("outer")
    inner = nodes.get("inner")
    
    if not (outer and inner):
        print("FAIL: Missing outer or inner subgraph container")
        return False
        
    # Check if outer fully encloses inner
    # Outer left <= inner left, outer top <= inner top, outer right >= inner right, outer bottom >= inner bottom
    outer_left, outer_right = outer["x"], outer["x"] + outer["width"]
    outer_top, outer_bottom = outer["y"], outer["y"] + outer["height"]
    
    inner_left, inner_right = inner["x"], inner["x"] + inner["width"]
    inner_top, inner_bottom = inner["y"], inner["y"] + inner["height"]
    
    encloses_inner_x = (outer_left <= inner_left) and (outer_right >= inner_right)
    encloses_inner_y = (outer_top <= inner_top) and (outer_bottom >= inner_bottom)
    
    print(f"Inner bounds: X=[{inner_left}, {inner_right}], Y=[{inner_top}, {inner_bottom}]")
    print(f"Outer bounds: X=[{outer_left}, {outer_right}], Y=[{outer_top}, {outer_bottom}]")
    print(f"Outer encloses Inner X: {encloses_inner_x}, Outer encloses Inner Y: {encloses_inner_y}")
    
    # Are outer and inner identical/overlapping boundaries?
    same_bounds = (outer_left == inner_left) and (outer_top == inner_top) and (outer_right == inner_right) and (outer_bottom == inner_bottom)
    if same_bounds:
        print("WARNING/BUG: Outer and Inner swimlane containers have IDENTICAL coordinates!")
        
    child_collisions = check_node_collisions(nodes, include_swimlanes=False)
    print(f"Child node collisions: {len(child_collisions)}")
    
    pass_test = encloses_inner_x and encloses_inner_y and not same_bounds and len(child_collisions) == 0
    print(f"TEST 5 RESULT: {'PASS' if pass_test else 'FAIL'}\n")
    return pass_test

if __name__ == "__main__":
    t1 = test_user_requested_graph()
    t2 = test_shape_and_multihop()
    t3 = test_single_subgraph()
    t4 = test_multiple_subgraphs()
    t5 = test_nested_subgraphs()
    
    all_passed = t1 and t2 and t3 and t4 and t5
    print("========================================")
    print(f"OVERALL EMPIRICAL TEST RESULT: {'ALL PASS' if all_passed else 'FAILURES DETECTED'}")
    print("========================================")
