import os
import re
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\ssuja\OneDrive\Desktop\Learn_Antigravity_Advance\draw_io_automation\antigravity_drawio_mcp")
README_PATH = PROJECT_ROOT / "README.md"

def test_json_ld():
    print("=== 1. Testing JSON-LD Schema ===")
    content = README_PATH.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', content, re.DOTALL)
    if not match:
        print("FAIL: JSON-LD script tag not found!")
        return False
    
    json_str = match.group(1)
    try:
        data = json.loads(json_str)
        print("SUCCESS: JSON-LD parses as valid JSON.")
    except Exception as e:
        print(f"FAIL: JSON-LD parsing error: {e}")
        return False

    errors = []
    # Check top-level properties
    if data.get("@context") != "https://schema.org":
        errors.append(f"Invalid @context: {data.get('@context')}")
    
    graph = data.get("@graph", [])
    if not isinstance(graph, list) or len(graph) == 0:
        errors.append("@graph is missing or empty")
    
    soft_app = next((item for item in graph if item.get("@type") == "SoftwareApplication"), None)
    faq_page = next((item for item in graph if item.get("@type") == "FAQPage"), None)
    
    if not soft_app:
        errors.append("SoftwareApplication entity missing from @graph")
    else:
        req_keys = ["name", "alternateName", "description", "operatingSystem", "applicationCategory", "softwareVersion", "license", "url", "codeRepository", "author"]
        for k in req_keys:
            if k not in soft_app:
                errors.append(f"SoftwareApplication missing property: {k}")
    
    if not faq_page:
        errors.append("FAQPage entity missing from @graph")
    else:
        main_entity = faq_page.get("mainEntity", [])
        if not isinstance(main_entity, list) or len(main_entity) == 0:
            errors.append("FAQPage mainEntity is empty or invalid")
        else:
            print(f"INFO: FAQPage contains {len(main_entity)} mainEntity questions.")
            for i, q in enumerate(main_entity):
                if q.get("@type") != "Question":
                    errors.append(f"FAQ mainEntity[{i}] is not @type Question")
                if "name" not in q or "acceptedAnswer" not in q:
                    errors.append(f"FAQ mainEntity[{i}] missing name or acceptedAnswer")
                elif q["acceptedAnswer"].get("@type") != "Answer" or "text" not in q["acceptedAnswer"]:
                    errors.append(f"FAQ mainEntity[{i}] acceptedAnswer invalid")

    # Cross-check JSON-LD FAQ questions with Markdown FAQ section
    print("\n--- Cross-checking JSON-LD FAQ vs Markdown FAQ ---")
    
    # Extract only FAQ section content
    faq_section_match = re.search(r'## ❓ Frequently Asked Questions.*?\n(.*?)(?=\n---\n\n## |\Z)', content, re.DOTALL)
    if faq_section_match:
        faq_content = faq_section_match.group(1)
        md_faq_matches = re.findall(r'###\s+\d+\.\s+(.*?)\n(.*?)(?=\n###|\n---|\Z)', faq_content, re.DOTALL)
        print(f"INFO: Markdown FAQ section found {len(md_faq_matches)} H3 FAQ entries.")
        
        if faq_page and "mainEntity" in faq_page:
            json_faqs = faq_page["mainEntity"]
            if len(json_faqs) != len(md_faq_matches):
                errors.append(f"FAQ Count Mismatch: JSON-LD has {len(json_faqs)} questions, Markdown has {len(md_faq_matches)} questions.")
            
            for idx, q_json in enumerate(json_faqs):
                q_title_json = q_json.get("name", "").strip()
                if idx < len(md_faq_matches):
                    q_title_md = md_faq_matches[idx][0].strip()
                    # Clean markdown formatting like `...` if present
                    clean_md_title = re.sub(r'`([^`]+)`', r'\1', q_title_md)
                    if q_title_json.lower() != clean_md_title.lower():
                        print(f"MISMATCH DETECTED (Q{idx+1}):\n  JSON-LD: '{q_title_json}'\n  Markdown: '{q_title_md}'")
                        errors.append(f"FAQ Q{idx+1} title mismatch between JSON-LD and Markdown")
                    else:
                        print(f"  ✅ Q{idx+1} title matches perfectly.")
                else:
                    errors.append(f"JSON-LD question {idx+1} has no corresponding Markdown H3.")
    else:
        errors.append("Could not locate Markdown FAQ section in README.md")

    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        return False
    else:
        print("SUCCESS: JSON-LD schema is fully compliant and matches Markdown content.")
        return True

def test_heading_hierarchy():
    print("\n=== 2. Testing Heading Hierarchy ===")
    content = README_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    headings = []
    in_code_block = False
    
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append((line_num, level, text))

    print(f"INFO: Found {len(headings)} headings in README.md.")
    
    hierarchy_issues = []
    prev_level = 0
    
    for line_num, level, text in headings:
        print(f"Line {line_num:3d}: {'  ' * (level-1)}H{level} - {text}")
        if prev_level > 0 and level > prev_level + 1:
            hierarchy_issues.append(f"Line {line_num}: Skipped heading level from H{prev_level} to H{level} ('{text}')")
        prev_level = level

    if hierarchy_issues:
        print("\nISSUES FOUND in Heading Hierarchy:")
        for issue in hierarchy_issues:
            print(f"  - {issue}")
        return False
    else:
        print("SUCCESS: Heading hierarchy is strictly sequential (no skipped levels).")
        return True

def test_links():
    print("\n=== 3. Testing Link & Asset Integrity ===")
    content = README_PATH.read_text(encoding="utf-8")
    
    # Extract markdown links [text](target) and html src/href
    md_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
    html_srcs = re.findall(r'src=["\']([^"\']+)["\']', content)
    html_hrefs = re.findall(r'href=["\']([^"\']+)["\']', content)
    
    all_targets = set()
    for _, target in md_links:
        all_targets.add(target.strip())
    for target in html_srcs + html_hrefs:
        all_targets.add(target.strip())
        
    print(f"INFO: Found {len(all_targets)} unique link/asset targets.")
    
    broken_local_links = []
    external_links = []
    
    for target in all_targets:
        # Ignore anchor-only links or mailto
        if target.startswith("#") or target.startswith("mailto:"):
            continue
        if target.startswith("http://") or target.startswith("https://"):
            external_links.append(target)
            continue
        
        # Relative file path check
        # Remove any anchor if present e.g. file.md#section
        clean_target = target.split("#")[0]
        if not clean_target:
            continue
            
        local_path = PROJECT_ROOT / clean_target
        if not local_path.exists():
            broken_local_links.append((target, str(local_path)))

    print(f"\nInternal Relative Links Check:")
    if broken_local_links:
        print("FAIL: Broken local file/image links detected:")
        for target, full in broken_local_links:
            print(f"  ❌ Target '{target}' -> File non-existent at '{full}'")
    else:
        print("SUCCESS: All internal relative links and images exist on disk.")

    print(f"\nExternal Links Summary ({len(external_links)} links):")
    invalid_ext = []
    for ext in sorted(external_links):
        # Validate URI format basics
        if not re.match(r'^https?://[a-zA-Z0-9.\-_]+(?:/[^\s]*)?$', ext):
            invalid_ext.append(ext)
        print(f"  🔗 {ext}")
        
    if invalid_ext:
        print(f"FAIL: Invalid external URL formats: {invalid_ext}")

    return len(broken_local_links) == 0 and len(invalid_ext) == 0

def test_keyphrase_density():
    print("\n=== 4. Testing Keyphrase Density & GEO Optimization ===")
    content = README_PATH.read_text(encoding="utf-8")
    
    # Strip code blocks for natural text word count
    text_only = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    text_only = re.sub(r'<script.*?</script>', '', text_only, flags=re.DOTALL)
    
    words = re.findall(r'\b\w+\b', text_only)
    total_words = len(words)
    print(f"INFO: Total natural language word count (excl. code/scripts): {total_words}")
    
    keyphrases = [
        "antigravity-drawio-mcp",
        "Flowchart AI Generator",
        "Draw.io MCP",
        "Google Antigravity MCP",
        "Architecture Diagram AI",
        "Claude Code",
        "Cursor IDE",
        "VS Code",
        "Windsurf",
        "Mermaid to Draw.io",
        "validate_diagram",
        "parse_diagram",
        "convert_mermaid_to_drawio",
        "create_diagram",
        "export_diagram",
        "open_in_drawio"
    ]
    
    print("\nKeyphrase Occurrences & Density in Full README:")
    for kp in keyphrases:
        count = len(re.findall(re.escape(kp), content, flags=re.IGNORECASE))
        kp_words = len(kp.split())
        density = (count * kp_words / total_words) * 100 if total_words > 0 else 0
        print(f"  - '{kp}': {count} occurrences ({density:.2f}% density)")

    print("\nGEO Elements Verification:")
    has_system_prompt_box = "AI System Prompt & Quick Context" in content
    has_rag_index_metadata = "AI Search & RAG Indexing Metadata" in content
    has_faq = "Frequently Asked Questions" in content
    has_c4_section = "System Architecture & C4 Diagram Model" in content
    
    print(f"  - AI System Prompt & Quick Context Box: {'✅ Present' if has_system_prompt_box else '❌ Missing'}")
    print(f"  - AI Search & RAG Indexing Metadata Comment: {'✅ Present' if has_rag_index_metadata else '❌ Missing'}")
    print(f"  - FAQ Section: {'✅ Present' if has_faq else '❌ Missing'}")
    print(f"  - C4 Architecture Section: {'✅ Present' if has_c4_section else '❌ Missing'}")

def main():
    print("Starting Empirical Verification of README.md...")
    res_json = test_json_ld()
    res_headings = test_heading_hierarchy()
    res_links = test_links()
    test_keyphrase_density()
    
    print("\n================ SUMMARY ================")
    print(f"JSON-LD Schema: {'PASS' if res_json else 'FAIL'}")
    print(f"Heading Hierarchy: {'PASS' if res_headings else 'FAIL'}")
    print(f"Link Integrity: {'PASS' if res_links else 'FAIL'}")
    print("==========================================")

if __name__ == "__main__":
    main()
