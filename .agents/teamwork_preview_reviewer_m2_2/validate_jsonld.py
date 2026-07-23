import json
import re
import sys

def validate():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'<script type="application/ld\+json">\s*({.*?})\s*</script>', content, re.DOTALL)
    if not match:
        print("ERROR: Could not find JSON-LD script block in README.md")
        sys.exit(1)

    json_str = match.group(1)
    try:
        data = json.loads(json_str)
        print("JSON-LD Syntax: OK")
        print(f"Context: {data.get('@context')}")
        graph = data.get("@graph", [])
        print(f"Graph length: {len(graph)}")
        for item in graph:
            print(f" - Item @type: {item.get('@type')}, @id: {item.get('@id')}")
            if item.get("@type") == "SoftwareApplication":
                print(f"   Name: {item.get('name')}, Version: {item.get('softwareVersion')}")
            elif item.get("@type") == "FAQPage":
                questions = item.get("mainEntity", [])
                print(f"   FAQ Count: {len(questions)}")
                for q in questions:
                    print(f"     Q: {q.get('name')}")
    except Exception as e:
        print(f"JSON-LD Parsing Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate()
