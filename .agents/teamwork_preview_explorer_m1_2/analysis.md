# Analysis Report: Exporter Cross-Platform Resolution (Milestone 1 - R2)

## Executive Summary
This analysis evaluates `src/antigravity_drawio_mcp/exporter.py` to ensure robust, cross-platform resolution of the Draw.io Desktop executable and process termination handling across Windows, macOS, and Linux.

The evaluation confirms that the exporter architecture in `exporter.py` is well-structured, but requires clear verification and standardization of binary resolution paths, process kill commands, and mock-based unit testing to guarantee reliability across all supported operating systems.

---

## 1. Analysis of Current Implementation (`src/antigravity_drawio_mcp/exporter.py`)

### 1.1 Executable Resolution (`get_drawio_executable`)
- **Current Logic** (lines 10–42):
  - Uses `platform.system()` to branch path discovery across `"Windows"`, `"Darwin"` (macOS), and `"Linux"`/Unix.
  - Windows paths searched:
    - `C:\Program Files\draw.io\draw.io.exe`
    - `C:\Program Files (x86)\draw.io\draw.io.exe`
    - `~\AppData\Local\Programs\draw.io\draw.io.exe` (expanded via `os.path.expanduser`)
  - macOS paths searched:
    - `/Applications/draw.io.app/Contents/MacOS/draw.io`
    - `~/Applications/draw.io.app/Contents/MacOS/draw.io` (expanded)
  - Linux paths searched:
    - `/usr/bin/drawio`
    - `/usr/bin/draw.io`
    - `/opt/drawio/drawio`
    - `/snap/bin/drawio`
    - `/usr/local/bin/drawio`
  - Fallback check: `shutil.which("drawio") or shutil.which("draw.io")`.

- **Assessment & Enhancements**:
  - The PATH lookup via `shutil.which("drawio") or shutil.which("draw.io")` should be checked either prior to or immediately alongside standard hardcoded paths. Checking `shutil.which` first allows user-customized PATH binaries or environment overrides (e.g., custom package installs in `/usr/local/bin` or custom wrappers) to take precedence while preserving fallback to standard system locations.
  - All requested target paths from `PROJECT.md` and task specifications are covered:
    - macOS: `/Applications/draw.io.app/Contents/MacOS/draw.io`
    - Linux: `/usr/bin/drawio`, `/opt/drawio/drawio`
    - PATH: `shutil.which("drawio")` / `shutil.which("draw.io")`

---

### 1.2 Process Killing (`_kill_running_instances`)
- **Current Logic** (lines 45–58):
  ```python
  @classmethod
  def _kill_running_instances(cls):
      sys.stderr.write("Warning: Closing running Draw.io Desktop instances to release file locks for export — any unsaved changes in open diagrams will be lost.\n")
      sys.stderr.flush()
      system = platform.system()
      try:
          if system == "Windows":
              subprocess.run(["taskkill", "/IM", "draw.io.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
          else:
              subprocess.run(["pkill", "-f", "draw.io"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
              subprocess.run(["pkill", "-f", "drawio"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
          time.sleep(1)
      except Exception as e:
          sys.stderr.write(f"Warning: Process kill attempt encountered error: {e}\n")
  ```

- **Assessment & Enhancements**:
  - Process termination uses `platform.system()`:
    - Windows: `taskkill /IM draw.io.exe /F`
    - Unix/macOS/Linux: `pkill -f draw.io` (and `pkill -f drawio`)
  - Exception handling (`try...except Exception`) ensures that environments missing `taskkill` or `pkill` (such as minimal Linux Docker containers) do not throw uncaught exceptions, writing a warning to stderr instead.
  - **Deferred Execution**: In `export()` (lines 81–95), Attempt 1 executes directly without calling `_kill_running_instances()`. Only if Attempt 1 fails to produce a non-zero byte file does Attempt 2 invoke `_kill_running_instances()` before retrying. This satisfies the constraint that process termination is deferred until a file lock issue is encountered.

---

## 2. Proposed Implementation Strategy

### 2.1 Refactored `get_drawio_executable()` Code Specification

```python
@staticmethod
def get_drawio_executable():
    """Locate the Draw.io Desktop executable across Windows, macOS, Linux, and PATH."""
    # 1. Check system PATH first for user or environment overrides
    which_drawio = shutil.which("drawio") or shutil.which("draw.io")
    if which_drawio:
        return which_drawio

    # 2. Inspect platform-specific standard installation locations
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
            "/usr/local/bin/drawio",
            os.path.expanduser("~/.local/bin/drawio")
        ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None
```

### 2.2 Refactored `_kill_running_instances()` Code Specification

```python
@classmethod
def _kill_running_instances(cls):
    """Release file locks by terminating running Draw.io Desktop instances cross-platform."""
    sys.stderr.write("Warning: Closing running Draw.io Desktop instances to release file locks for export — any unsaved changes in open diagrams will be lost.\n")
    sys.stderr.flush()
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["taskkill", "/IM", "draw.io.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            # Unix / macOS / Linux
            subprocess.run(["pkill", "-f", "draw.io"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            subprocess.run(["pkill", "-f", "drawio"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        time.sleep(1)
    except Exception as e:
        sys.stderr.write(f"Warning: Process kill attempt encountered error: {e}\n")
```

---

## 3. Unit Test Strategy (`tests/test_exporter.py`)

To ensure 100% test coverage without requiring physical installations of Draw.io Desktop on CI/CD environments, we propose comprehensive unit tests using Python's `unittest.mock`:

```python
import unittest
from unittest.mock import patch, MagicMock
import os
from antigravity_drawio_mcp.exporter import DrawIOExporter

class TestDrawIOExporterCrossPlatform(unittest.TestCase):

    @patch("shutil.which")
    @patch("platform.system")
    def test_get_executable_path_first(self, mock_system, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/custom/bin/drawio" if cmd == "drawio" else None
        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/usr/custom/bin/drawio")

    @patch("shutil.which", return_value=None)
    @patch("os.path.exists")
    @patch("platform.system", return_value="Darwin")
    def test_get_executable_macos(self, mock_system, mock_exists, mock_which):
        mock_exists.side_effect = lambda path: path == "/Applications/draw.io.app/Contents/MacOS/draw.io"
        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/Applications/draw.io.app/Contents/MacOS/draw.io")

    @patch("shutil.which", return_value=None)
    @patch("os.path.exists")
    @patch("platform.system", return_value="Linux")
    def test_get_executable_linux(self, mock_system, mock_exists, mock_which):
        mock_exists.side_effect = lambda path: path == "/opt/drawio/drawio"
        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/opt/drawio/drawio")

    @patch("subprocess.run")
    @patch("platform.system", return_value="Windows")
    def test_kill_instances_windows(self, mock_system, mock_run):
        DrawIOExporter._kill_running_instances()
        mock_run.assert_called_once_with(["taskkill", "/IM", "draw.io.exe", "/F"], stdout=-3, stderr=-3, check=False)

    @patch("subprocess.run")
    @patch("platform.system", return_value="Linux")
    def test_kill_instances_linux(self, mock_system, mock_run):
        DrawIOExporter._kill_running_instances()
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(["pkill", "-f", "draw.io"], stdout=-3, stderr=-3, check=False)
        mock_run.assert_any_call(["pkill", "-f", "drawio"], stdout=-3, stderr=-3, check=False)
```

---

## 4. Conclusion & Recommendations
1. The analysis confirms all cross-platform paths for macOS (`/Applications/draw.io.app/Contents/MacOS/draw.io`), Linux (`/usr/bin/drawio`, `/opt/drawio/drawio`), and System PATH (`shutil.which`) are properly targeted.
2. Checking `shutil.which` first prioritizes system PATH binary resolution before falling back to fixed installation paths.
3. Process killing correctly isolates Windows (`taskkill /IM draw.io.exe /F`) from Unix/macOS/Linux (`pkill -f draw.io`), and is safely deferred until an export file lock failure occurs.
