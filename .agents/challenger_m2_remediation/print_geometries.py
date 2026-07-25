import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.parser import DrawIOParser

output_dir = os.path.join(os.path.dirname(__file__), "test_output")

scenarios = [
    ("Single Subgraph", "s1_single.drawio"),
    ("2-Level Nested Subgraph", "s2_2level.drawio"),
    ("3-Level Nested Subgraph", "s3_3level.drawio"),
    ("Sibling Subgraphs in Outer", "s4_siblings.drawio")
]

for name, filename in scenarios:
    filepath = os.path.join(output_dir, filename)
    parser = DrawIOParser(filepath)
    parsed = parser.parse()
    print(f"=== {name} ({filename}) ===")
    for n in parsed["pages"][0]["nodes"]:
        is_swimlane = "swimlane" in n.get("style", "")
        kind = "Swimlane Subgraph" if is_swimlane else "Leaf Node"
        x, y, w, h = n["x"], n["y"], n["width"], n["height"]
        right = x + w
        bottom = y + h
        print(f"  [{kind}] ID: '{n['id']}', Title: '{n['value']}' | x={x}, y={y}, w={w}, h={h} | right={right}, bottom={bottom}")
    print()
