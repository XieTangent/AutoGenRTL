import subprocess
import sys
from src.api import config


def generate_waveform():
    workspace = config.SRC_DIR / "vlog_workspace"
    wave_path = workspace / "wave.vcd"
    wave_json_path = workspace / "wave.json"
    waveform_path = workspace / "waveform.png"

    if not wave_path.exists():
        print("Error: wave.vcd not found.")
        sys.exit(1)

    result = subprocess.run(
        ["python", "-m", "vcd2wavedrom.vcd2wavedrom", "-i", wave_path, "-o", wave_json_path],
        shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("vcd2wavedrom failed:", result.stderr)
        sys.exit(1)

    result = subprocess.run(
        ['npx', 'wavedrom-cli', '-i', wave_json_path, '-p', waveform_path],
        shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("wavedrom-cli failed:", result.stderr)
        sys.exit(1)
