import sys
import os
import unittest

# Ensure src path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.parser import DrawIOParser
from antigravity_drawio_mcp.verifier import DrawIOVerifier

def verify_geometry_enclosure(parsed, expected_hierarchy):
    """
    parsed: output from DrawIOParser.parse()
    expected_hierarchy: dict mapping parent_id -> list of child_ids (nodes or subgraphs)
    Returns: list of error strings (empty if all pass)
    """
    nodes_by_id = {n["id"]: n for n in parsed["pages"][0]["nodes"]}
    errors = []

    # Identify swimlane containers (subgraphs) vs leaf nodes
    # Swimlane nodes have 'swimlane' in style
    swimlane_ids = {n["id"] for n in parsed["pages"][0]["nodes"] if "swimlane" in n.get("style", "")}
    
    for parent_id, child_ids in expected_hierarchy.items():
        if parent_id not in nodes_by_id:
            errors.append(f"Parent subgraph '{parent_id}' not found in parsed nodes.")
            continue

        parent = nodes_by_id[parent_id]
        px, py, pw, ph = parent["x"], parent["y"], parent["width"], parent["height"]
        p_right = px + pw
        p_bottom = py + ph
        header_height = 25  # startSize=25 in swimlane style

        for cid in child_ids:
            if cid not in nodes_by_id:
                errors.append(f"Child '{cid}' of parent '{parent_id}' not found in parsed nodes.")
                continue

            child = nodes_by_id[cid]
            cx, cy, cw, ch = child["x"], child["y"], child["width"], child["height"]
            c_right = cx + cw
            c_bottom = cy + ch

            # Check 1: Left boundary (px <= cx - 20)
            if px > cx - 19.9:
                errors.append(f"Left enclosure failure: parent '{parent_id}' x ({px}) should be <= child '{cid}' x-20 ({cx - 20})")

            # Check 2: Header title overlap (cy >= py + header_height)
            if cy < py + header_height:
                errors.append(f"Header title overlap failure: child '{cid}' y ({cy}) overlaps parent '{parent_id}' header bar [y={py}, y+header={py + header_height}]")

            # Check 3: Top margin (py <= cy - 35)
            if py > cy - 34.9:
                errors.append(f"Top margin failure: parent '{parent_id}' y ({py}) should be <= child '{cid}' y-35 ({cy - 35})")

            # Check 4: Right boundary (p_right >= c_right + 20)
            if p_right < c_right + 19.9:
                errors.append(f"Right enclosure failure: parent '{parent_id}' right ({p_right}) should be >= child '{cid}' right+20 ({c_right + 20})")

            # Check 5: Bottom boundary (p_bottom >= c_bottom + 10)
            if p_bottom < c_bottom + 9.9:
                errors.append(f"Bottom enclosure failure: parent '{parent_id}' bottom ({p_bottom}) should be >= child '{cid}' bottom+10 ({c_bottom + 10})")

    return errors


def run_empirical_tests():
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}

    # Scenario 1: Single Subgraph
    s1_mermaid = """graph TD
    subgraph sub1 [Single Subgraph]
        A[Node A] --> B[Node B]
    end"""
    s1_xml = MermaidToDrawIO.convert(s1_mermaid)
    s1_file = os.path.join(output_dir, "s1_single.drawio")
    with open(s1_file, "w", encoding="utf-8") as f:
        f.write(s1_xml)
    
    parsed_1 = DrawIOParser(s1_file).parse()
    errs_1 = verify_geometry_enclosure(parsed_1, {"sub1": ["A", "B"]})
    audit_1 = DrawIOVerifier.verify(s1_file)
    results["Single Subgraph"] = {
        "errors": errs_1,
        "is_clean": audit_1["is_clean"],
        "node_count": audit_1["node_count"]
    }

    # Scenario 2: 2-Level Nested Subgraph
    s2_mermaid = """graph TD
    subgraph outer [Outer Container]
        subgraph inner [Inner Container]
            A[Node A] --> B[Node B]
        end
    end"""
    s2_xml = MermaidToDrawIO.convert(s2_mermaid)
    s2_file = os.path.join(output_dir, "s2_2level.drawio")
    with open(s2_file, "w", encoding="utf-8") as f:
        f.write(s2_xml)
    
    parsed_2 = DrawIOParser(s2_file).parse()
    errs_2 = verify_geometry_enclosure(parsed_2, {
        "outer": ["inner"],
        "inner": ["A", "B"]
    })
    audit_2 = DrawIOVerifier.verify(s2_file)
    results["2-Level Nested Subgraph"] = {
        "errors": errs_2,
        "is_clean": audit_2["is_clean"],
        "node_count": audit_2["node_count"]
    }

    # Scenario 3: 3-Level Nested Subgraph
    s3_mermaid = """graph TD
    subgraph L1 [Level 1 Outer]
        subgraph L2 [Level 2 Middle]
            subgraph L3 [Level 3 Inner]
                A[Node A] --> B[Node B]
                B --> C[Node C]
            end
        end
    end"""
    s3_xml = MermaidToDrawIO.convert(s3_mermaid)
    s3_file = os.path.join(output_dir, "s3_3level.drawio")
    with open(s3_file, "w", encoding="utf-8") as f:
        f.write(s3_xml)

    parsed_3 = DrawIOParser(s3_file).parse()
    errs_3 = verify_geometry_enclosure(parsed_3, {
        "L1": ["L2"],
        "L2": ["L3"],
        "L3": ["A", "B", "C"]
    })
    audit_3 = DrawIOVerifier.verify(s3_file)
    results["3-Level Nested Subgraph"] = {
        "errors": errs_3,
        "is_clean": audit_3["is_clean"],
        "node_count": audit_3["node_count"]
    }

    # Scenario 4: Sibling Subgraphs Inside Outer Subgraph
    s4_mermaid = """graph TD
    subgraph outer [Outer System]
        subgraph subA [Frontend Module]
            UI[User Interface] --> API[API Gateway]
        end
        subgraph subB [Backend Module]
            SVC[Service Layer] --> DB[Database]
        end
        API --> SVC
    end"""
    s4_xml = MermaidToDrawIO.convert(s4_mermaid)
    s4_file = os.path.join(output_dir, "s4_siblings.drawio")
    with open(s4_file, "w", encoding="utf-8") as f:
        f.write(s4_xml)

    parsed_4 = DrawIOParser(s4_file).parse()
    errs_4 = verify_geometry_enclosure(parsed_4, {
        "outer": ["subA", "subB"],
        "subA": ["UI", "API"],
        "subB": ["SVC", "DB"]
    })
    audit_4 = DrawIOVerifier.verify(s4_file)
    results["Sibling Subgraphs in Outer"] = {
        "errors": errs_4,
        "is_clean": audit_4["is_clean"],
        "node_count": audit_4["node_count"]
    }

    # Output detailed report
    print("\n================ EMPIRICAL VERIFICATION RESULTS ================")
    all_passed = True
    for name, res in results.items():
        status = "PASSED" if not res["errors"] and res["is_clean"] else "FAILED"
        if status == "FAILED":
            all_passed = False
        print(f"Scenario [{name}]: {status}")
        print(f"  Clean Audit: {res['is_clean']} (Nodes/Cells count: {res['node_count']})")
        if res["errors"]:
            print("  Errors:")
            for err in res["errors"]:
                print(f"    - {err}")
        else:
            print("  No spatial enclosure or header overlap violations found.")
        print("-" * 65)

    return all_passed, results, {
        "s1": parsed_1,
        "s2": parsed_2,
        "s3": parsed_3,
        "s4": parsed_4
    }

if __name__ == "__main__":
    success, results, parsed_data = run_empirical_tests()
    if not success:
        sys.exit(1)
