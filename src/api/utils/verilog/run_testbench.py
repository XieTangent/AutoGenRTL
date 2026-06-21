import subprocess
import sys
from src.api import config
from src.api.utils.verilog.gen_waveform import generate_waveform


def check_result(simulation_result):
    output_text = (simulation_result.stdout or "") + "\n" + (simulation_result.stderr or "")
    success_keywords = [
        "All tests passed!", "Mismatches: 0", "all tests passed",
        "Your Design Passed", "ERRORS:    0"
    ]
    return any(k in output_text for k in success_keywords)


def run_testbench(verilog_code, testbench_path, if_generate_waveform=False):
    workspace = config.SRC_DIR / "vlog_workspace"

    if testbench_path.suffix == ".v":
        verilog_path = workspace / "verilog.v"
        testbench_path = workspace / "testbench.v"
    elif testbench_path.suffix == ".sv":
        verilog_path = workspace / "verilog.sv"
        testbench_path = workspace / "testbench.sv"

    output_vvp = workspace / "sim.vvp"
    wave_path = workspace / "wave.vcd"

    with open(verilog_path, "w", encoding="utf-8") as f:
        f.write(verilog_code)

    result = subprocess.run(
        ['iverilog', '-g2012', '-o', output_vvp, testbench_path, verilog_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return {"status": "error", "message": result.stderr}

    if wave_path.exists():
        wave_path.unlink()

    simulation_result = subprocess.run(
        ['vvp', output_vvp], capture_output=True, text=True, cwd=workspace
    )
    if simulation_result.returncode != 0:
        print("vvp failed:", simulation_result.stderr)
        sys.exit(1)

    status = "success" if check_result(simulation_result) else "failure"
    if if_generate_waveform:
        generate_waveform()
    return {"status": status, "message": simulation_result.stdout}
