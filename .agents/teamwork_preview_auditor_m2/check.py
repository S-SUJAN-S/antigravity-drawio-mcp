import os
import json
import re

readme_path = r"C:/Users/ssuja/OneDrive/Desktop/Learn_Antigravity_Advance/draw_io_automation/antigravity_drawio_mcp/README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

m = re.search(r'<script type="application/ld\+json">(.*?)</script>', readme, re.DOTALL)
if m:
    json_str = m.group(1).strip()
    data = json.loads(json_str)
    print("JSON-LD parse SUCCESSFUL!")
    print(f"JSON-LD Context: {data.get('@context')}")
    print(f"Graph nodes count: {len(data.get('@graph', []))}")
    for item in data.get('@graph', []):
        print(f"  - Type: {item.get('@type')}, ID/Name: {item.get('name', item.get('@id'))}")
else:
    print("JSON-LD not found")
