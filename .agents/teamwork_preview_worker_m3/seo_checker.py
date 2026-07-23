import re
import sys

# Ensure UTF-8 output encoding
sys.stdout.reconfigure(encoding='utf-8')

readme_path = "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    content = f.read()

words = re.findall(r'\b\w+\b', content)
total_words = len(words)

keywords = [
    "Draw.io MCP",
    "Flowchart AI Generator",
    "Google Antigravity MCP",
    "Architecture Diagram AI"
]

print("=== SEO KEYWORD DENSITY ANALYSIS ===")
print(f"Total Words in README.md: {total_words}")
for kw in keywords:
    matches = re.findall(re.escape(kw), content, flags=re.IGNORECASE)
    count = len(matches)
    kw_word_count = len(kw.split())
    total_kw_words = count * kw_word_count
    density = (total_kw_words / total_words) * 100
    print(f"Keyword: '{kw}' -> Count: {count}, Total Keyword Words: {total_kw_words}, Density: {density:.2f}%")

print("\n=== MARKDOWN HEADER HIERARCHY ANALYSIS ===")
headers = re.findall(r'^(#{1,6})\s+(.*)$', content, flags=re.MULTILINE)
previous_level = 0
hierarchy_ok = True

for hashes, title in headers:
    level = len(hashes)
    indent = "  " * (level - 1)
    if previous_level > 0 and level > previous_level + 1:
        print(f"{indent}[INVALID] H{level}: {title} (SKIPPED LEVEL from H{previous_level})")
        hierarchy_ok = False
    else:
        print(f"{indent}[OK] H{level}: {title}")
    previous_level = level

print(f"\nHeader Hierarchy Status: {'PASS' if hierarchy_ok else 'FAIL'}")
