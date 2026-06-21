import os
import json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"

def check_result(simulation_result, folder_name):
    result_dir = DATA_DIR
    result_dir.mkdir(parents=True, exist_ok=True)

    success_file = result_dir / "success.json"
    failure_file = result_dir / "failure.json"

    output_text = (simulation_result.stdout or "") + "\n" + (simulation_result.stderr or "")
    success_keywords = [
        "All tests passed!", "Mismatches: 0", "all tests passed",
        "Your Design Passed", "ERRORS:    0"
    ]
    is_success = any(k in output_text for k in success_keywords)

    result_entry = {"name": folder_name, "message": output_text.strip()}
    target_file = success_file if is_success else failure_file
    print("success" if is_success else "fail")

    data = []
    if target_file.exists():
        with open(target_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []

    data.append(result_entry)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def run_testbench(testbench_file, verilog_file, folder_path, folder_name):
    result_file = folder_path / "result.txt"

    result = subprocess.run(
        ['iverilog', '-g2012', '-o', "sim.vvp", testbench_file, verilog_file],
        capture_output=True, text=True, cwd=folder_path
    )
    if result.returncode != 0:
        print(f"Failed to compile {verilog_file}")
        result_file.write_text(result.stderr)
        return

    simulation_result = subprocess.run(
        ['vvp', "sim.vvp"], capture_output=True, text=True, cwd=folder_path
    )
    if simulation_result.returncode != 0:
        print(f"Failed to run vvp for {verilog_file}")
        result_file.write_text(simulation_result.stderr)
        return

    check_result(simulation_result, folder_name)

def find_files_in_subdirectories(directory):
    count = 0
    directory = Path(directory)
    for root, dirs, files in os.walk(directory):
        if not dirs:
            testbench_file = verilog_file = None
            for file in files:
                if file.startswith("testbench") and file.endswith((".v", ".sv")):
                    testbench_file = file
                elif file.endswith((".v", ".sv")) and not file.startswith("testbench"):
                    verilog_file = file

            folder_path = Path(root)
            folder_name = folder_path.name
            print(f"Run {folder_name}")
            count += 1

            if (folder_path / "waveform.png").exists():
                print(f"skip {folder_name}")
                continue

            if testbench_file and verilog_file:
                run_testbench(testbench_file, verilog_file, folder_path, folder_name)

    print(f"Total problems: {count}")

if __name__ == "__main__":
    find_files_in_subdirectories(DATA_DIR / "all_problems")
