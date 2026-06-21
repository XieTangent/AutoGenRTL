import re
import os
import json
import base64
import shutil
import subprocess
import sys
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

IF_GENERATE_WAVEFORM = False
IF_GENERATE_WAVEFORM_JSON = False
SCRIPT_DIR = Path(__file__).parent

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

MODEL_FORMATS = {
    "openai": [
        "gpt-4", "o1-mini", "gpt-4o-mini", "gpt-4o",
        "gpt-3.5-turbo", "o3-mini", "o1"
    ],
    "grok": [
        "grok-3-mini-beta"
    ],
}

def write_json_to_files(json_data, folder_name, file_name):
    target_dir = os.path.join(folder_name, file_name)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    file_count = len([n for n in os.listdir(target_dir) if n.startswith('result') and n.endswith('.json')])
    next_filename = os.path.join(target_dir, f'result{file_count + 1}.json')
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    with open(next_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_verilog_code(response):
    patterns = [
        re.compile(r'```verilog\n(.*?)\n```', re.DOTALL),
        re.compile(r'```verilog\n(.*?)\n ```', re.DOTALL),
        re.compile(r'```verilog \n(.*?)\n```', re.DOTALL),
        re.compile(r'``` verilog\n(.*?)\n```', re.DOTALL),
        re.compile(r'``` verilog \n(.*?)\n```', re.DOTALL),
        re.compile(r'```Verilog\n(.*?)\n```', re.DOTALL),
        re.compile(r'```Verilog \n(.*?)\n```', re.DOTALL),
        re.compile(r'``` Verilog\n(.*?)\n```', re.DOTALL),
        re.compile(r'``` Verilog \n(.*?)\n```', re.DOTALL),
        re.compile(r'```\n(.*?)\n```', re.DOTALL),
        re.compile(r'```(.*?)\n```', re.DOTALL),
        re.compile(r'``` \n(.*?)\n```', re.DOTALL),
        re.compile(r'```v\n(.*?)\n```', re.DOTALL),
        re.compile(r'```V\n(.*?)\n```', re.DOTALL),
        re.compile(r'```SV\n(.*?)\n```', re.DOTALL),
        re.compile(r'```Sv\n(.*?)\n```', re.DOTALL),
        re.compile(r'```sV\n(.*?)\n```', re.DOTALL),
        re.compile(r'```sv\n(.*?)\n```', re.DOTALL),
        re.compile(r'(module\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\);.*?endmodule)', re.DOTALL),
    ]
    for pattern in patterns:
        matches = pattern.findall(response)
        if matches:
            return matches[0].strip()
    print(f"Fail to extract verilog\nResponse: {response}")
    return f"Fail to extract verilog. Response: {response}"

def get_model_type(model_name):
    for model_type, models in MODEL_FORMATS.items():
        if model_name in models:
            return model_type
    return None

def chat_with_llm(messages, llm_name):
    def chat_with_gpt(messages, model):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client.chat.completions.create(model=model, messages=messages).choices[0].message.content

    def chat_with_grok(messages, model):
        if not XAI_API_KEY:
            raise ValueError("XAI_API_KEY is not set.")
        client = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")
        return client.chat.completions.create(model=model, messages=messages).choices[0].message.content

    model_type = get_model_type(llm_name)
    if model_type == "openai":
        return chat_with_gpt(messages, llm_name)
    elif model_type == "grok":
        return chat_with_grok(messages, llm_name)
    raise ValueError(f"Unsupported model: {llm_name}")

def get_initial_message(llm_name, question):
    content = [
        {"type": "text", "text": "You are a Verilog code generator. Please provide the code starts with ```verilog\n and ends with ```\n."},
        {"type": "text", "text": "This is the description of the functionality of the circuit:"},
        {"type": "text", "text": question},
    ]
    return [{"role": "user", "content": content}]

def get_syntax_error_message(llm_name, verilog_code, error_message, question):
    content = [
        {"type": "text", "text": "You are a Verilog code generator. Please provide the code starts with ```\n and ends with \n```."},
        {"type": "text", "text": "Please review the error message and modify the Verilog code accordingly."},
        {"type": "text", "text": "This is the error verilog code:"},
        {"type": "text", "text": "```\\n" + verilog_code + "\\n```"},
        {"type": "text", "text": "This is the error message:"},
        {"type": "text", "text": "```\\n" + error_message + "\\n```"},
        {"type": "text", "text": "This is the description of the functionality of the circuit:"},
        {"type": "text", "text": "```\\n" + question + "\\n```"},
    ]
    return [{"role": "user", "content": content}]

def get_testbench_error_message(llm_name, verilog_code, testbench_code, testbench_response, question):
    content = [
        {"type": "text", "text": "You are a Verilog code generator. Please provide the code starts with ```\n and ends with \n```."},
        {"type": "text", "text": "Please review the testbench result and modify the Verilog code accordingly."},
        {"type": "text", "text": "This is the error Verilog code:"},
        {"type": "text", "text": f"```\\n{verilog_code}\\n```"},
        {"type": "text", "text": "This is the testbench code:"},
        {"type": "text", "text": f"```\\n{testbench_code}\\n```"},
        {"type": "text", "text": "This is the testbench response:"},
        {"type": "text", "text": f"```\\n{testbench_response}\\n```"},
        {"type": "text", "text": "This is the description of the functionality of the circuit:"},
        {"type": "text", "text": f"```\\n{question}\\n```"},
    ]

    if IF_GENERATE_WAVEFORM:
        waveform_path = SCRIPT_DIR / "vlog_workspace" / "waveform.png"
        with open(waveform_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        if IF_GENERATE_WAVEFORM_JSON:
            json_path = SCRIPT_DIR / "vlog_workspace" / "wave.json"
            with open(json_path, "r") as f:
                json_content = f.read()
            content.extend([
                {"type": "text", "text": "This is the waveform (json) generated by running the answer through the testbench."},
                {"type": "text", "text": json_content},
            ])
        else:
            content.extend([
                {"type": "text", "text": "This is the waveform generated by running the answer through the testbench."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ])

    return [{"role": "user", "content": content}]

def generate_final_report(verilog_code, change_count, simulation_status, testbench_success_rate, testbench_response):
    return {
        "Final_verilog": verilog_code,
        "Change_verilog_count": change_count,
        "Simulation_status": simulation_status,
        "Testbench_successful_rate": testbench_success_rate,
        "Testbench_response": testbench_response,
    }

def generate_change_report(change_count, change_type, gpt_response, verilog_code, error_message, response_verilog_code):
    entry = {
        "change_id": change_count,
        "change_by": change_type,
        "gpt_response": gpt_response,
        "error_verilog_code": verilog_code,
        "error_messages": error_message,
        "new_verilog_code": response_verilog_code,
    }
    if change_type == "testbench" and IF_GENERATE_WAVEFORM:
        image_path = SCRIPT_DIR / "vlog_workspace" / "waveform.png"
        with open(image_path, "rb") as f:
            entry["image_base64"] = base64.b64encode(f.read()).decode('utf-8')
    return entry

def generate_waveform():
    workspace = SCRIPT_DIR / "vlog_workspace"
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

def check_result(simulation_result):
    output_text = (simulation_result.stdout or "") + "\n" + (simulation_result.stderr or "")
    success_keywords = [
        "All tests passed!", "Mismatches: 0", "all tests passed",
        "Your Design Passed", "ERRORS:    0"
    ]
    return any(k in output_text for k in success_keywords)

def run_testbench(verilog_code, testbench_path):
    workspace = SCRIPT_DIR / "vlog_workspace"

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
    if IF_GENERATE_WAVEFORM:
        generate_waveform()
    return {"status": status, "message": simulation_result.stdout}

def compile_verilog(verilog_code):
    workspace = SCRIPT_DIR / "vlog_workspace"
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

def Corrected_Simulation_Code(question, verilog_code, model_matrix, testbench_path, max_change_count=25):
    result = []
    change_count = 0
    simulation_status = "Fail"
    model_count = 0
    model_max_count = len(model_matrix)
    start_time = time.time()

    while change_count < max_change_count:
        model_count = (model_count + 1) % model_max_count
        response = compile_verilog(verilog_code)

        if response.get("status") == "error":
            error_message = response.get("error_message") or "Unknown error"
            if len(error_message) > 1000:
                error_message = error_message[:1000]
                print("Shortened syntax response")
            gpt_messages = get_syntax_error_message(model_matrix[model_count], verilog_code, error_message, question)
            gpt_response = chat_with_llm(gpt_messages, model_matrix[model_count])
            response_verilog_code = extract_verilog_code(gpt_response)
            change_count += 1
            print(f"Change {change_count}. Model: {model_matrix[model_count]}. Elapsed: {round(time.time() - start_time, 2)}s")
            result.append(generate_change_report(change_count, "syntax", gpt_response, verilog_code, error_message, response_verilog_code))
            verilog_code = response_verilog_code
        else:
            simulation_status = "Pass"
            testbench_code = read_file(testbench_path)
            testbench_response = run_testbench(verilog_code, testbench_path)

            if testbench_response.get("status") == "success":
                result.append(generate_final_report(verilog_code, change_count, "Pass", "100", testbench_response))
                print(f"Pass testbench. Elapsed: {round(time.time() - start_time, 2)}s")
                return result

            tb_message = testbench_response.get("message", "")
            if len(tb_message) > 3000:
                tb_message = "Fail"
                print("Shortened testbench response")
            gpt_messages = get_testbench_error_message(model_matrix[model_count], verilog_code, testbench_code, tb_message, question)
            gpt_response = chat_with_llm(gpt_messages, model_matrix[model_count])
            response_verilog_code = extract_verilog_code(gpt_response)
            change_count += 1
            print(f"Change {change_count}. Model: {model_matrix[model_count]}. Elapsed: {round(time.time() - start_time, 2)}s")
            result.append(generate_change_report(change_count, "testbench", gpt_response, verilog_code, testbench_response, response_verilog_code))
            verilog_code = response_verilog_code

    result.append(generate_final_report(verilog_code, change_count, simulation_status, 0, ""))
    print(f"Max iterations reached. Elapsed: {round(time.time() - start_time, 2)}s")
    return result

def auto_gen_verilog(question_path, model_matrix, testbench_path, max_count=25):
    question = read_file(question_path)
    initial_messages = get_initial_message(model_matrix[0], question)
    verilog_code = extract_verilog_code(chat_with_llm(initial_messages, model_matrix[0]))
    return Corrected_Simulation_Code(question, verilog_code, model_matrix, testbench_path, max_count)

def create_verilog_from_file_multiple_workers(directory, result_folder, model_matrix, max_count=25, i=1):
    result_folder_path = SCRIPT_DIR.parent / "data" / result_folder
    result_folder_path.mkdir(parents=True, exist_ok=True)

    for file_path in Path(directory).rglob("design_description.txt"):
        root = file_path.parent
        file_name = root.name
        dest_folder = SCRIPT_DIR / "vlog_workspace"
        start_time = time.time()
        print(f"{file_name} start")

        for item in root.iterdir():
            if item.name == "design_description.txt":
                continue
            dest = dest_folder / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

        question_path = root / "design_description.txt"
        testbench_path = dest_folder / "testbench.v"
        if not testbench_path.exists():
            testbench_path = dest_folder / "testbench.sv"

        result = auto_gen_verilog(question_path, model_matrix, testbench_path, max_count)
        write_json_to_files(result, result_folder_path, file_name)
        print(f"Elapsed: {round(time.time() - start_time, 2)}s")

    print(f"Round {i} completed.")
