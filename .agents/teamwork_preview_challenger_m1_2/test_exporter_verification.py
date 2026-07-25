import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import io
import subprocess

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))

from antigravity_drawio_mcp.exporter import DrawIOExporter

class TestDrawIOExporterResolution(unittest.TestCase):
    """Test cross-platform resolution logic (Windows, macOS/Darwin, Linux)"""

    @patch("shutil.which")
    def test_path_override(self, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/local/bin/drawio" if cmd == "drawio" else None
        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/usr/local/bin/drawio")

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Windows")
    @patch("os.path.exists")
    def test_windows_standard_path(self, mock_exists, mock_system, mock_which):
        def exists_side_effect(path):
            return path == r"C:\Program Files\draw.io\draw.io.exe"
        mock_exists.side_effect = exists_side_effect

        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, r"C:\Program Files\draw.io\draw.io.exe")

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Darwin")
    @patch("os.path.exists")
    def test_mac_standard_path(self, mock_exists, mock_system, mock_which):
        def exists_side_effect(path):
            return path == "/Applications/draw.io.app/Contents/MacOS/draw.io"
        mock_exists.side_effect = exists_side_effect

        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/Applications/draw.io.app/Contents/MacOS/draw.io")

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Linux")
    @patch("os.path.exists")
    def test_linux_standard_path(self, mock_exists, mock_system, mock_which):
        def exists_side_effect(path):
            return path == "/usr/bin/drawio"
        mock_exists.side_effect = exists_side_effect

        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/usr/bin/drawio")

    @patch("shutil.which", return_value=None)
    @patch("platform.system", return_value="Linux")
    @patch("os.path.exists", return_value=False)
    def test_executable_not_found(self, mock_exists, mock_system, mock_which):
        exe = DrawIOExporter.get_drawio_executable()
        self.assertIsNone(exe)


class TestProcessTerminationSafety(unittest.TestCase):
    """Test platform-specific process kill logic"""

    @patch("platform.system", return_value="Windows")
    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("time.sleep")
    def test_windows_process_kill(self, mock_sleep, mock_run, mock_which, mock_system):
        mock_which.side_effect = lambda cmd: "C:\\Windows\\System32\\taskkill.exe" if cmd == "taskkill" else None
        stderr_buf = io.StringIO()
        with patch("sys.stderr", stderr_buf):
            DrawIOExporter._kill_running_instances()
        
        self.assertIn("Warning: Closing running Draw.io Desktop instances", stderr_buf.getvalue())
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_has_calls([
            call(["taskkill", "/IM", "draw.io.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False),
            call(["taskkill", "/IM", "drawio.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        ])

    @patch("platform.system", return_value="Darwin")
    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("time.sleep")
    def test_posix_pkill_process_kill(self, mock_sleep, mock_run, mock_which, mock_system):
        mock_which.side_effect = lambda cmd: "/usr/bin/pkill" if cmd == "pkill" else None
        stderr_buf = io.StringIO()
        with patch("sys.stderr", stderr_buf):
            DrawIOExporter._kill_running_instances()
        
        self.assertIn("Warning: Closing running Draw.io Desktop instances", stderr_buf.getvalue())
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_has_calls([
            call(["pkill", "-f", "draw.io"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False),
            call(["pkill", "-f", "drawio"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        ])

    @patch("platform.system", return_value="Linux")
    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("time.sleep")
    def test_posix_killall_fallback(self, mock_sleep, mock_run, mock_which, mock_system):
        mock_which.side_effect = lambda cmd: "/usr/bin/killall" if cmd == "killall" else None
        stderr_buf = io.StringIO()
        with patch("sys.stderr", stderr_buf):
            DrawIOExporter._kill_running_instances()
        
        self.assertIn("Warning: Closing running Draw.io Desktop instances", stderr_buf.getvalue())
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_has_calls([
            call(["killall", "-9", "draw.io"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False),
            call(["killall", "-9", "drawio"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        ])


class TestNonDestructiveExportFallback(unittest.TestCase):
    """Test non-destructive export fallback logic"""

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value="/usr/bin/drawio")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("os.remove")
    @patch("subprocess.run")
    @patch.object(DrawIOExporter, "_kill_running_instances")
    def test_attempt_1_success_no_process_kill(self, mock_kill, mock_run, mock_remove, mock_getsize, mock_exists, mock_exe):
        # Setup: Output file exists and size > 0 after Attempt 1
        # os.path.exists checks:
        # 1. output_file cleanup check before attempt 1 -> return False
        # 2. output_file check after attempt 1 -> return True
        mock_exists.side_effect = [False, True]
        mock_getsize.return_value = 1024
        
        stderr_buf = io.StringIO()
        with patch("sys.stderr", stderr_buf):
            res = DrawIOExporter.export("input.drawio", "output.png")
            
        self.assertEqual(res, "output.png")
        self.assertEqual(mock_run.call_count, 1)
        mock_kill.assert_not_called()
        self.assertEqual(stderr_buf.getvalue(), "")

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value="/usr/bin/drawio")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("os.remove")
    @patch("subprocess.run")
    @patch("platform.system", return_value="Linux")
    @patch("shutil.which", return_value="/usr/bin/pkill")
    @patch("time.sleep")
    def test_attempt_1_fail_attempt_2_retry_and_success(self, mock_sleep, mock_which, mock_system, mock_run, mock_remove, mock_getsize, mock_exists, mock_exe):
        # Attempt 1: output file does not exist after run
        # Attempt 2: output file exists and has size > 0 after second run
        # os.path.exists calls:
        # 1. output_file cleanup before attempt 1 -> False
        # 2. output_file check after attempt 1 -> False
        # 3. output_file cleanup before attempt 2 -> False
        # 4. output_file check after attempt 2 -> True
        mock_exists.side_effect = [False, False, False, True]
        mock_getsize.return_value = 2048

        stderr_buf = io.StringIO()
        with patch("sys.stderr", stderr_buf):
            res = DrawIOExporter.export("input.drawio", "output.png")

        self.assertEqual(res, "output.png")
        self.assertEqual(mock_run.call_count, 4)  # 1 initial export attempt + 2 pkill commands in _kill_running_instances + 1 retry export attempt
        # Wait, let's verify mock_run calls:
        # Attempt 1: subprocess.run(build_cmd())
        # _kill_running_instances(): pkill draw.io, pkill drawio (2 calls)
        # Attempt 2: subprocess.run(build_cmd())
        # Total subprocess.run calls = 4
        self.assertIn("Warning: Closing running Draw.io Desktop instances to release file locks for export", stderr_buf.getvalue())

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value=None)
    def test_export_no_executable_raises_file_not_found(self, mock_exe):
        with self.assertRaises(FileNotFoundError):
            DrawIOExporter.export("input.drawio", "output.png")

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value="/usr/bin/drawio")
    @patch("os.path.exists", return_value=False)
    @patch.object(DrawIOExporter, "_kill_running_instances")
    @patch("subprocess.run")
    def test_both_attempts_fail_raises_runtime_error(self, mock_run, mock_kill, mock_exists, mock_exe):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Export failed: corrupted input"
        mock_run.return_value = mock_result

        with self.assertRaises(RuntimeError) as ctx:
            DrawIOExporter.export("input.drawio", "output.png")
        
        self.assertIn("Draw.io export failed with code 1. Stderr: Export failed: corrupted input", str(ctx.exception))
        self.assertEqual(mock_kill.call_count, 1)

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value="/usr/bin/drawio")
    @patch("os.path.exists")
    @patch("os.path.getsize", return_value=512)
    @patch("subprocess.run")
    def test_cmd_building_options(self, mock_run, mock_getsize, mock_exists, mock_exe):
        mock_exists.side_effect = [False, True]
        
        # Test PDF format without transparent flag
        DrawIOExporter.export("input.drawio", "output.pdf", fmt="pdf", page_index=2, transparent=True)
        expected_cmd = ["/usr/bin/drawio", "--export", "--format", "pdf", "--output", "output.pdf", "--page-index", "2", "input.drawio"]
        mock_run.assert_called_with(expected_cmd, capture_output=True, text=True, check=False)

        # Test PNG with transparent=True
        mock_exists.side_effect = [False, True]
        DrawIOExporter.export("input.drawio", "output.png", fmt="png", page_index=1, transparent=True)
        expected_cmd_png = ["/usr/bin/drawio", "--export", "--format", "png", "--transparent", "--output", "output.png", "--page-index", "1", "input.drawio"]
        mock_run.assert_called_with(expected_cmd_png, capture_output=True, text=True, check=False)

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value="/usr/bin/drawio")
    @patch("subprocess.Popen")
    def test_open_in_app(self, mock_popen, mock_exe):
        res = DrawIOExporter.open_in_app("diagram.drawio")
        mock_popen.assert_called_once_with(["/usr/bin/drawio", "diagram.drawio"])
        self.assertIn("Opened diagram.drawio in Draw.io Desktop App", res)

    @patch.object(DrawIOExporter, "get_drawio_executable", return_value=None)
    def test_open_in_app_no_exe(self, mock_exe):
        with self.assertRaises(FileNotFoundError):
            DrawIOExporter.open_in_app("diagram.drawio")

if __name__ == "__main__":
    unittest.main()
