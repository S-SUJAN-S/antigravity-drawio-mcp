# Analysis Report: DrawIOExporter Non-Destructive Export & Process Safety (Milestone 1 - R2)

## 1. Executive Summary

This report provides a detailed analysis of `src/antigravity_drawio_mcp/exporter.py` and formulates a robust implementation plan for **Milestone 1 - R2 (Exporter Non-Destructive Export & Process Safety)**.

The objective is to ensure that Draw.io diagram export:
1. **Runs non-destructively by default**: Tries running CLI export without terminating existing Draw.io Desktop instances, avoiding data loss in user-opened diagrams.
2. **Executes fallback process termination conditionally**: Only attempts process termination (with clear `sys.stderr` warning logging) if Attempt 1 fails due to file locking or process conflicts.
3. **Guarantees cross-platform process safety**: Ensures process termination routines never crash or throw unhandled exceptions on non-Windows platforms (macOS, Linux), environments lacking `taskkill`/`pkill`/`killall`, or restricted shells.

---

## 2. Analysis of Existing Codebase (`src/antigravity_drawio_mcp/exporter.py`)

### 2.1 Code Structure & Functionality
`exporter.py` defines `DrawIOExporter` with three main methods:
- `get_drawio_executable()`: Scans platform-specific default installation paths (`C:\Program Files\draw.io\draw.io.exe`, `/Applications/draw.io.app/Contents/MacOS/draw.io`, `/usr/bin/drawio`, etc.) and falls back to `shutil.which("drawio")` / `shutil.which("draw.io")`.
- `_kill_running_instances()`: Emits a warning to `sys.stderr` and uses system commands (`taskkill` on Windows, `pkill` on macOS/Linux) to terminate open Draw.io Desktop instances.
- `export()`: Pre-cleans output file, invokes Draw.io CLI `--export` command, and handles fallback logic.
- `open_in_app()`: Launches Draw.io GUI for interactive viewing.

### 2.2 Vulnerabilities & Limitations Identified in Current Code

| Issue Location | Defect / Vulnerability | Risk / Impact |
|---|---|---|
| `export()` Attempt 1 | Uncaught exceptions during `subprocess.run` (e.g. `PermissionError`, `OSError`, `SubprocessError`) | Direct crash without falling back to Attempt 2 or attempting process termination. |
| `_kill_running_instances()` | Single `try...except` wrapping sequential `pkill` calls on POSIX | If `pkill` is missing (`FileNotFoundError`), execution immediately jumps to `except` block and skips secondary targets (`pkill -f drawio`). |
| Windows `taskkill` scope | Targets only `draw.io.exe` | Does not attempt `drawio.exe`, missing process variants on some Windows distributions. |
| Process tool dependency | Direct invocation of `taskkill`/`pkill` without `shutil.which` pre-check | Raises `FileNotFoundError` in minimal containers, stripped Linux, or restricted Windows environments lacking system utilities in `%PATH%`. |
| Partial Output Handling | Direct `os.remove(output_file)` without `try...except OSError` | If `output_file` is locked or read-only, `os.remove` raises `PermissionError`/`OSError`, halting the export pipeline prematurely. |

---

## 3. Implementation Strategy

To satisfy all requirements of Milestone 1 - R2 while maintaining full backwards compatibility and high stability across all platforms:

### 3.1 Non-Destructive Export Pipeline (Attempt 1)
1. **Initial Clean-up**: Safely attempt removal of pre-existing `output_file` using `try...except OSError: pass`.
2. **Attempt 1 Execution**: Run Draw.io CLI `--export` directly without calling `_kill_running_instances()`.
3. **Success Verification**: Check if `os.path.exists(output_file)` and `os.path.getsize(output_file) > 0`.
4. **Immediate Return**: If Attempt 1 yields a non-empty export artifact, return `output_file` immediately. Open Draw.io GUI instances and unsaved user diagrams are left completely untouched.

### 3.2 Conditional Fallback & Warning Logging (Attempt 2)
1. **Trigger Condition**: Attempt 1 returned non-zero code, produced missing/0-byte output file, or raised a subprocess exception.
2. **Warning Emission**: Call `_kill_running_instances()`, which flushes a clear warning message to `sys.stderr`:
   `Warning: Closing running Draw.io Desktop instances to release file locks for export — any unsaved changes in open diagrams will be lost.`
3. **Safe Process Termination**:
   - Check availability of termination utilities (`shutil.which("taskkill")`, `shutil.which("pkill")`, `shutil.which("killall")`).
   - Execute termination per process target inside isolated `try...except Exception: pass` blocks.
   - Pause briefly (`time.sleep(1)`) to allow OS handle release.
4. **Attempt 2 Execution**: Re-run Draw.io CLI `--export` command.
5. **Final Evaluation**: Return `output_file` if successful; otherwise, raise a descriptive `RuntimeError` with return code and `stderr` diagnostic logs.

### 3.3 Cross-Platform & Utility-Safe Process Termination Matrix

| Platform | Primary Tool | Secondary / Fallback Tool | Target Process Names | Exception Guard |
|---|---|---|---|---|
| **Windows** | `taskkill /IM <proc> /F` | N/A | `draw.io.exe`, `drawio.exe` | Pre-check `shutil.which("taskkill")`, isolate each call in `try...except Exception` |
| **macOS (Darwin)** | `pkill -f <target>` | `killall -9 <target>` | `draw.io`, `drawio` | Pre-check `shutil.which("pkill")` / `shutil.which("killall")`, isolate calls |
| **Linux / Unix** | `pkill -f <target>` | `killall -9 <target>` | `draw.io`, `drawio` | Pre-check `shutil.which("pkill")` / `shutil.which("killall")`, isolate calls |
| **Minimal / Container** | Any available tool | Fail gracefully (log warning to stderr) | Any | Top-level `try...except Exception as e:` guarantees caller never crashes |

---

## 4. Proposed Code Replacement

The proposed replacement code for `src/antigravity_drawio_mcp/exporter.py` is provided below:

```python
import subprocess
import os
import sys
import shutil
import platform
import time

class DrawIOExporter:
    @staticmethod
    def get_drawio_executable():
        system = platform.system()
        possible_paths = []
        
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\draw.io\draw.io.exe",
                r"C:\Program Files (x86)\draw.io\draw.io.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\draw.io\draw.io.exe")
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/draw.io.app/Contents/MacOS/draw.io",
                os.path.expanduser("~/Applications/draw.io.app/Contents/MacOS/draw.io")
            ]
        else:  # Linux / Unix
            possible_paths = [
                "/usr/bin/drawio",
                "/usr/bin/draw.io",
                "/opt/drawio/drawio",
                "/snap/bin/drawio",
                "/usr/local/bin/drawio"
            ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        which_drawio = shutil.which("drawio") or shutil.which("draw.io")
        if which_drawio:
            return which_drawio

        return None

    @classmethod
    def _kill_running_instances(cls):
        sys.stderr.write("Warning: Closing running Draw.io Desktop instances to release file locks for export — any unsaved changes in open diagrams will be lost.\n")
        sys.stderr.flush()
        system = platform.system()
        try:
            if system == "Windows":
                if shutil.which("taskkill"):
                    for proc_name in ["draw.io.exe", "drawio.exe"]:
                        try:
                            subprocess.run(["taskkill", "/IM", proc_name, "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                        except Exception:
                            pass
            else:
                targets = ["draw.io", "drawio"]
                has_pkill = shutil.which("pkill") is not None
                has_killall = shutil.which("killall") is not None

                for target in targets:
                    if has_pkill:
                        try:
                            subprocess.run(["pkill", "-f", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                        except Exception:
                            pass
                    elif has_killall:
                        try:
                            subprocess.run(["killall", "-9", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                        except Exception:
                            pass
            time.sleep(1)
        except Exception as e:
            sys.stderr.write(f"Warning: Process kill attempt encountered error: {e}\n")
            sys.stderr.flush()

    @classmethod
    def export(cls, input_file, output_file, fmt="png", page_index=1, transparent=True):
        exe = cls.get_drawio_executable()
        if not exe:
            raise FileNotFoundError("Draw.io Desktop executable not found on host system.")

        def build_cmd():
            cmd = [
                exe,
                "--export",
                "--format", fmt,
                "--output", output_file,
                "--page-index", str(page_index),
                input_file
            ]
            if transparent and fmt in ["png", "svg"]:
                cmd.insert(4, "--transparent")
            return cmd

        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass

        # Attempt 1: Export directly without killing process
        try:
            result = subprocess.run(build_cmd(), capture_output=True, text=True, check=False)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return output_file
        except Exception:
            result = None

        # Attempt 2: Fallback to closing process lock if first attempt failed
        cls._kill_running_instances()
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass

        try:
            result = subprocess.run(build_cmd(), capture_output=True, text=True, check=False)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return output_file
        except Exception as e:
            raise RuntimeError(f"Draw.io export execution failed: {e}") from e

        err_msg = result.stderr if result and result.stderr else "Unknown error or zero-byte output."
        code = result.returncode if result else -1
        raise RuntimeError(f"Draw.io export failed with code {code}. Stderr: {err_msg}")

    @classmethod
    def open_in_app(cls, input_file):
        exe = cls.get_drawio_executable()
        if not exe:
            raise FileNotFoundError("Draw.io Desktop executable not found on host system.")
        subprocess.Popen([exe, input_file])
        return f"Opened {input_file} in Draw.io Desktop App"
```

---

## 5. Verification Plan

1. **Unit Test Verification**: Run `python -m unittest discover -s tests` to confirm zero regression across the existing test suite.
2. **Mock Non-Destructive Export Test**: Mock `subprocess.run` to simulate a successful first export attempt and verify that `_kill_running_instances()` is never called.
3. **Mock Fallback Export Test**: Mock `subprocess.run` to return code 1 on first attempt and code 0 on second attempt; verify `_kill_running_instances()` is called and stderr warning is emitted.
4. **Missing Tool Simulation Test**: Mock `shutil.which` to return `None` for `taskkill`, `pkill`, and `killall` on both Windows and POSIX systems; verify `_kill_running_instances()` completes without throwing an exception.
