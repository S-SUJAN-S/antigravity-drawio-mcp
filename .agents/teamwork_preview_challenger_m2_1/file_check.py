import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\ssuja\OneDrive\Desktop\Learn_Antigravity_Advance\draw_io_automation\antigravity_drawio_mcp")

files_to_check = [
    "README.md",
    "LICENSE",
    "docs/architecture.png",
    "docs/INTEGRATION_GUIDE.md",
    "docs/real_world_examples/project_01_uvm_testbench.png",
    "docs/real_world_examples/project_03_graphic_organizer.png",
    "docs/real_world_examples/project_04_fpga_flow.png",
    "examples/",
    "examples/01_basic_architecture.py",
    "examples/02_mermaid_to_drawio.py",
    "examples/03_parse_and_inspect.py",
    "examples/04_mcp_client_simulation.py",
]

print("=== Detailed File Status Check ===")
for item in files_to_check:
    path = PROJECT_ROOT / item
    if path.exists():
        if path.is_file():
            print(f"[OK] FILE  : {item:<55} ({path.stat().st_size} bytes)")
        else:
            print(f"[OK] DIR   : {item:<55}")
    else:
        print(f"[FAIL] MISSING: {item:<55}")
