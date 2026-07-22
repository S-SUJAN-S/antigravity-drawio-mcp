import subprocess
import os

class DrawIOExporter:
    @staticmethod
    def get_drawio_executable():
        possible_paths = [
            r"C:\Program Files\draw.io\draw.io.exe",
            r"C:\Program Files (x86)\draw.io\draw.io.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\draw.io\draw.io.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def export(cls, input_file, output_file, fmt="png", page_index=1, transparent=True):
        exe = cls.get_drawio_executable()
        if not exe:
            raise FileNotFoundError("Draw.io Desktop executable not found on host system.")

        # Release Electron process lock before CLI export
        subprocess.run(["powershell", "-Command", "Get-Process draw.io -ErrorAction SilentlyContinue | Stop-Process -Force"], check=False)
        import time
        time.sleep(1)

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

        if os.path.exists(output_file):
            os.remove(output_file)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return output_file
        raise RuntimeError(f"Draw.io export failed with code {result.returncode}. Stderr: {result.stderr}")

    @classmethod
    def open_in_app(cls, input_file):
        exe = cls.get_drawio_executable()
        if not exe:
            raise FileNotFoundError("Draw.io Desktop executable not found on host system.")
        subprocess.Popen([exe, input_file])
        return f"Opened {input_file} in Draw.io Desktop App"
