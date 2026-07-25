import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.parser import DrawIOParser
from antigravity_drawio_mcp.verifier import DrawIOVerifier
from verify_nested_subgraphs import verify_geometry_enclosure

def test_adversarial_subgraphs():
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    
    # Adversarial Scenario 1: Mixed direct nodes and child subgraphs
    adv1_mermaid = """graph TD
    subgraph outer [Outer Complex]
        DirectTop[Direct Top Node]
        subgraph inner [Inner Module]
            DeepNode1[Deep Node 1] --> DeepNode2[Deep Node 2]
        end
        DirectTop --> DeepNode1
    end"""
    
    adv1_xml = MermaidToDrawIO.convert(adv1_mermaid)
    adv1_file = os.path.join(output_dir, "adv1_mixed.drawio")
    with open(adv1_file, "w", encoding="utf-8") as f:
        f.write(adv1_xml)
        
    parsed_1 = DrawIOParser(adv1_file).parse()
    errs_1 = verify_geometry_enclosure(parsed_1, {
        "outer": ["DirectTop", "inner"],
        "inner": ["DeepNode1", "DeepNode2"]
    })
    audit_1 = DrawIOVerifier.verify(adv1_file)
    print("Adversarial 1 (Mixed Direct Nodes & Child Subgraphs):")
    print(f"  Clean: {audit_1['is_clean']}, Errs: {errs_1}")

    # Adversarial Scenario 2: Empty subgraph or subgraphs with no nodes
    adv2_mermaid = """graph TD
    subgraph outer [Outer Container]
        subgraph empty_sub [Empty Subgraph]
        end
        A[Node A]
    end"""
    adv2_xml = MermaidToDrawIO.convert(adv2_mermaid)
    adv2_file = os.path.join(output_dir, "adv2_empty.drawio")
    with open(adv2_file, "w", encoding="utf-8") as f:
        f.write(adv2_xml)

    parsed_2 = DrawIOParser(adv2_file).parse()
    audit_2 = DrawIOVerifier.verify(adv2_file)
    print("Adversarial 2 (Empty Subgraph):")
    print(f"  Clean: {audit_2['is_clean']}")

if __name__ == "__main__":
    test_adversarial_subgraphs()
