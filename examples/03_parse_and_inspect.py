"""
Example 03: Parsing & Decompressing Existing Draw.io Files
=========================================================
This PoC script demonstrates how to parse an existing `.drawio` XML diagram,
transparently handling zlib/base64 decompression and extracting graph metadata.
"""

import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure src directory is in Python path
mcp_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, mcp_src)

from antigravity_drawio_mcp.parser import DrawIOParser

def main():
    target_xml = os.path.abspath(os.path.join(os.path.dirname(__file__), "outputs", "01_basic_architecture.drawio"))
    if not os.path.exists(target_xml):
        print(f"Target file not found: {target_xml}. Please run 01_basic_architecture.py first.")
        return

    print(f"[Step 1] Loading and Parsing Draw.io XML: {target_xml}")
    parser = DrawIOParser(target_xml)
    parsed_data = parser.parse()

    print("\n[Step 2] Extracted Diagram Structure:")
    for page in parsed_data.get("pages", []):
        print(f"   Page Name: {page['name']}")
        print(f"   Nodes ({len(page['nodes'])}):")
        for node in page["nodes"]:
            print(f"     - ID: {node['id']} | Value: {repr(node['value'])} | Pos: ({node['x']}, {node['y']})")
        print(f"   Edges ({len(page['edges'])}):")
        for edge in page["edges"]:
            lbl = edge.get("label", edge.get("value", ""))
            print(f"     - ID: {edge['id']} | Source: {edge['source']} -> Target: {edge['target']} | Label: {repr(lbl)}")

    print("\nParse & Inspect PoC Completed Successfully!")

if __name__ == "__main__":
    main()
