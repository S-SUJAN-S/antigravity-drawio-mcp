import re
import json
import subprocess
from pathlib import Path

repo_root = Path("C:/Users/ssuja/OneDrive/Desktop/Learn_Antigravity_Advance/draw_io_automation/antigravity_drawio_mcp")
readme_path = repo_root / "README.md"
pyproject_path = repo_root / "pyproject.toml"

print("=== VICTORY AUDITOR INDEPENDENT VERIFIER ===")

# 1. READ README
readme_text = readme_path.read_text(encoding="utf-8")
words = re.findall(r'\w+', readme_text)
total_words = len(words)
print(f"Total word count in README.md: {total_words}")

# 2. KEYWORD DENSITY CHECK
target_keywords = [
    "Draw.io MCP",
    "Flowchart AI Generator",
    "Google Antigravity MCP",
    "Architecture Diagram AI"
]

print("\n--- Phase 3.1 Keyword Density Results ---")
for kw in target_keywords:
    pattern = re.compile(re.escape(kw), re.IGNORECASE)
    matches = pattern.findall(readme_text)
    count = len(matches)
    kw_words = len(re.findall(r'\w+', kw))
    density = (count * kw_words / total_words) * 100 if total_words > 0 else 0
    print(f"Keyword: '{kw}' | Occurrences: {count} | Density: {density:.2f}%")

# 3. AI SYSTEM PROMPT BLOCK CHECK
print("\n--- Phase 3.2 AI System Prompt & Quick Context Block Check ---")
prompt_block_found = "AI System Prompt & Quick Context" in readme_text or "AI System Prompt" in readme_text
json_ld_found = '<script type="application/ld+json">' in readme_text
metadata_rag_found = 'AI Search & RAG Indexing Metadata' in readme_text

print(f"System Prompt Callout Block present: {prompt_block_found}")
print(f"JSON-LD Schema block present: {json_ld_found}")
print(f"Metadata RAG comment present: {metadata_rag_found}")

# Extract JSON-LD blocks and validate
json_blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', readme_text, re.DOTALL)
print(f"Found {len(json_blocks)} JSON-LD blocks in README.md.")
for i, block in enumerate(json_blocks, 1):
    try:
        data = json.loads(block)
        print(f"  JSON-LD block {i} valid JSON. Type: {data.get('@type')}")
    except Exception as e:
        print(f"  JSON-LD block {i} ERROR: {e}")

# 4. GITHUB TOPICS CHECK
print("\n--- Phase 3.3 Recommended GitHub Topics Check ---")
github_topics_section = "GitHub Topics" in readme_text or "Recommended GitHub Topics" in readme_text
print(f"GitHub Topics section present in README.md: {github_topics_section}")

# Extract topics list from README
topics_in_readme = re.findall(r'`([a-z0-9\-]+)`', readme_text)
print(f"Found code tags in README.md (sample topics): {topics_in_readme[:10]}")

pyproject_text = pyproject_path.read_text(encoding="utf-8")
print("Keywords in pyproject.toml:")
keywords_match = re.search(r'keywords\s*=\s*\[(.*?)\]', pyproject_text, re.DOTALL)
if keywords_match:
    print("  " + keywords_match.group(0))

# 5. GIT COMMIT AND PUSH SYNC CHECK
print("\n--- Phase 3.4 Git Commit & Push Sync Check ---")
try:
    status_out = subprocess.check_output(["git", "status"], cwd=repo_root, text=True)
    log_out = subprocess.check_output(["git", "log", "-n", "1", "--oneline"], cwd=repo_root, text=True)
    remote_log = subprocess.check_output(["git", "log", "origin/main", "-n", "1", "--oneline"], cwd=repo_root, text=True)
    
    print(f"Git status summary: {'up to date' in status_out or 'Your branch is up to date' in status_out}")
    print(f"Local HEAD: {log_out.strip()}")
    print(f"Remote origin/main: {remote_log.strip()}")
    print(f"In sync: {log_out.strip() == remote_log.strip()}")
except Exception as e:
    print(f"Git check error: {e}")

# 6. CHEATING & HARDCODING DETECTION (PHASE 2)
print("\n--- Phase 2 Cheating & Hardcoding Detection ---")
suspicious_patterns = [
    r'TODO:', r'FIXME:', r'INSERT_HERE', r'http://example\.com', r'YOUR_NAME', r'PLACEHOLDER'
]

cheating_found = False
for pattern in suspicious_patterns:
    matches = re.findall(pattern, readme_text, re.IGNORECASE)
    if matches:
        print(f"WARNING: Found placeholder pattern '{pattern}' count: {len(matches)}")
        cheating_found = True

if not cheating_found:
    print("No forbidden placeholder patterns found in README.md.")

