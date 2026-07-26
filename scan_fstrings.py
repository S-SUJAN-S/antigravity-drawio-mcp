import os
import re

REPO_ROOT = r"C:\Users\ssuja\OneDrive\Desktop\Learn_Antigravity_Advance\draw_io_automation\antigravity_drawio_mcp"

# Pattern: look for f-strings (f"..." or f'...') where inside a {} there's a backslash
# We scan for lines containing f" or f' with a backslash inside curly braces
# This regex is a best-effort heuristic
FSTRING_WITH_BACKSLASH_IN_EXPR = re.compile(
    r'''f(?:""".*?"""|\'''.*?\'''|"[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')''',
    re.DOTALL
)

def check_file(fpath):
    issues = []
    with open(fpath, encoding="utf-8") as f:
        source = f.read()
        lines = source.splitlines()

    for lineno, line in enumerate(lines, 1):
        # Look for f-string expression containing backslash within {}
        # Heuristic: find patterns like f"...{...\...}..."
        # Match f" or f' start, then look for { containing backslash }
        if "f'" not in line and 'f"' not in line:
            continue

        # Find all f-string-like segments and check for backslash in {} expr
        # Look for: f"...{re.sub(r'\W+'...)}..." pattern
        matches = re.findall(r'f["\'].*?\{[^}]*\\[^}]*\}', line)
        if matches:
            issues.append((lineno, line.strip(), matches))
    return issues

found_any = False
for subdir in ["src", "tests"]:
    root = os.path.join(REPO_ROOT, subdir)
    for dirpath, dirs, files in os.walk(root):
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, REPO_ROOT)
            issues = check_file(fpath)
            if issues:
                found_any = True
                for lineno, content, matches in issues:
                    print(f"  FOUND: {rel}:{lineno}: {content}")
                    for m in matches:
                        print(f"    -> {m}")

if not found_any:
    print("No other backslash-in-f-string-expression issues found in src/ or tests/.")
