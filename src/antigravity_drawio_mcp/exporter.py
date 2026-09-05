import subprocess
import os
import sys
import shutil
import platform
import time

class DrawIOExporter:
    @staticmethod
    def get_drawio_executable():
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
                "/usr/local/bin/drawio"
            ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

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
    def export(cls, input_file, output_file, fmt="png", page_index=1, transparent=False, border=25, scale=2.0, theme="light"):
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
                "--border", str(border),
                "--scale", str(scale),
                "--theme", theme,
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
