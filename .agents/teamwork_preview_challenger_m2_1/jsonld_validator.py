import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\ssuja\OneDrive\Desktop\Learn_Antigravity_Advance\draw_io_automation\antigravity_drawio_mcp")
README_PATH = PROJECT_ROOT / "README.md"

content = README_PATH.read_text(encoding="utf-8")
match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', content, re.DOTALL)

data = json.loads(match.group(1))

print("=== JSON-LD Structural Deep-Dive ===")
print("Keys in root:", list(data.keys()))
print("@context:", data.get("@context"))
print("Graph items count:", len(data.get("@graph", [])))

for i, item in enumerate(data.get("@graph", [])):
    print(f"\n--- Graph Item [{i}] ({item.get('@type')}) ---")
    for k, v in item.items():
        if isinstance(v, list):
            print(f"  {k}: [list of {len(v)} items]")
        elif isinstance(v, dict):
            print(f"  {k}: dict with keys {list(v.keys())}")
        else:
            print(f"  {k}: {v}")

print("\n=== FAQ Q&A Detail Verification ===")
faq_item = next(item for item in data["@graph"] if item.get("@type") == "FAQPage")
for idx, q in enumerate(faq_item["mainEntity"], 1):
    q_name = q["name"]
    ans_text = q["acceptedAnswer"]["text"]
    print(f"Q{idx}: {q_name}")
    print(f"   A ({len(ans_text)} chars): {ans_text[:80]}...")
