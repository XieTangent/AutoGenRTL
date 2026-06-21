import subprocess
from src.api import config


def compile_verilog(verilog_code):
    workspace = config.SRC_DIR / "vlog_workspace"
    verilog_path = workspace / "verilog.v"
    output_vvp = workspace / "sim.vvp"
    workspace.mkdir(exist_ok=True)

    with open(verilog_path, "w", encoding="utf-8") as f:
        f.write(verilog_code)

    result = subprocess.run(
        ['iverilog', '-g2012', '-o', str(output_vvp), str(verilog_path)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return {"status": "success", "message": "Compilation successful"}
    return {"status": "error", "error_message": result.stderr}
