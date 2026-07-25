import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src folder to sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "src"))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO

def parse_xml_elements(xml_str):
    root = ET.fromstring(xml_str)
    cells = root.findall(".//mxCell")
    
    nodes = {}
    edges = []
    
    for cell in cells:
        cid = cell.get("id")
        parent = cell.get("parent")
        value = cell.get("value", "")
        style = cell.get("style", "")
        source = cell.get("source")
        target = cell.get("target")
        edge = cell.get("edge")
        vertex = cell.get("vertex")
        
        if vertex == "1":
            nodes[cid] = {
                "id": cid,
                "value": value,
                "style": style,
                "parent": parent
            }
        elif edge == "1":
            edges.append({
                "id": cid,
                "value": value,
                "source": source,
                "target": target,
                "style": style
            })
            
    return nodes, edges

def test_mixed_node_shapes():
    print("=== Test 1: Mixed Node Shape Syntax ===")
    mermaid_input = """graph TD
    A{Start} --> B(Process) --> C[End]
    """
    xml_output = MermaidToDrawIO.convert(mermaid_input)
    nodes, edges = parse_xml_elements(xml_output)
    
    assert "A" in nodes and "B" in nodes and "C" in nodes
    assert nodes["A"]["value"] == "Start" and "rhombus" in nodes["A"]["style"]
    assert nodes["B"]["value"] == "Process" and "rounded=1" in nodes["B"]["style"]
    assert nodes["C"]["value"] == "End" and "rounded=0" in nodes["C"]["style"]
    
    assert len(edges) == 2
    edge_pairs = [(e["source"], e["target"]) for e in edges]
    assert ("A", "B") in edge_pairs and ("B", "C") in edge_pairs
    print("Test 1 PASSED!")

def test_multihop_chains_with_labels():
    print("\n=== Test 2: Multi-hop Chains with Labels ===")
    mermaid_input = """graph TD
    A -- step1 --> B -- step2 --> C -- step3 --> D
    """
    xml_output = MermaidToDrawIO.convert(mermaid_input)
    nodes, edges = parse_xml_elements(xml_output)
    
    for nid in ["A", "B", "C", "D"]:
        assert nid in nodes
        
    assert len(edges) == 3
    edge_map = {(e["source"], e["target"]): e["value"] for e in edges}
    assert edge_map.get(("A", "B")) == "step1"
    assert edge_map.get(("B", "C")) == "step2"
    assert edge_map.get(("C", "D")) == "step3"
    print("Test 2 PASSED!")

def test_combined_multihop_shapes_labels():
    print("\n=== Test 3: Combined Multi-hop Shapes + Labels ===")
    mermaid_input = """graph TD
    A{Start} -- step1 --> B(Process) -- step2 --> C[End]
    """
    xml_output = MermaidToDrawIO.convert(mermaid_input)
    nodes, edges = parse_xml_elements(xml_output)
    
    assert nodes["A"]["value"] == "Start" and "rhombus" in nodes["A"]["style"]
    assert nodes["B"]["value"] == "Process" and "rounded=1" in nodes["B"]["style"]
    assert nodes["C"]["value"] == "End" and "rounded=0" in nodes["C"]["style"]
    
    edge_map = {(e["source"], e["target"]): e["value"] for e in edges}
    assert edge_map.get(("A", "B")) == "step1"
    assert edge_map.get(("B", "C")) == "step2"
    print("Test 3 PASSED!")

def test_pipe_labels_multihop():
    print("\n=== Test 4: Multi-hop Chains with Pipe Labels ===")
    mermaid_input = """graph TD
    A -->|yes| B -->|no| C
    """
    xml_output = MermaidToDrawIO.convert(mermaid_input)
    nodes, edges = parse_xml_elements(xml_output)
    
    edge_map = {(e["source"], e["target"]): e["value"] for e in edges}
    assert edge_map.get(("A", "B")) == "yes"
    assert edge_map.get(("B", "C")) == "no"
    print("Test 4 PASSED!")

def test_subgraph_with_multihop_shapes():
    print("\n=== Test 5: Subgraph with Multi-hop Shapes & Labels ===")
    mermaid_input = """graph TD
    subgraph sg1 [Sub Graph One]
        A{Start} -- ok --> B(Work)
    end
    B -- done --> C[Finish]
    """
    xml_output = MermaidToDrawIO.convert(mermaid_input)
    nodes, edges = parse_xml_elements(xml_output)
    
    assert "sg1" in nodes, "Subgraph container node missing"
    assert "swimlane" in nodes["sg1"]["style"]
    assert nodes["sg1"]["value"] == "Sub Graph One"
    
    assert nodes["A"]["value"] == "Start" and "rhombus" in nodes["A"]["style"]
    assert nodes["B"]["value"] == "Work" and "rounded=1" in nodes["B"]["style"]
    assert nodes["C"]["value"] == "Finish" and "rounded=0" in nodes["C"]["style"]
    
    edge_map = {(e["source"], e["target"]): e["value"] for e in edges}
    assert edge_map.get(("A", "B")) == "ok"
    assert edge_map.get(("B", "C")) == "done"
    print("Test 5 PASSED!")

if __name__ == "__main__":
    test_mixed_node_shapes()
    test_multihop_chains_with_labels()
    test_combined_multihop_shapes_labels()
    test_pipe_labels_multihop()
    test_subgraph_with_multihop_shapes()
    print("\nALL 5 TESTS PASSED SUCCESSFULLY!")
