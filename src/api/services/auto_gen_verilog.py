import time
from pathlib import Path

from src.api.utils.llm.gen_llm_message import get_initial_message, get_syntax_error_message, get_testbench_error_message
from src.api.utils.llm.handle_llm_response import extract_verilog_code
from src.api.utils.llm.chat_with_llm import chat_with_llm
from src.api.utils.gen_report import generate_change_report, generate_final_report
from src.api.utils.verilog.run_compile import compile_verilog
from src.api.utils.verilog.run_testbench import run_testbench
from src.api.utils.read_file import read_file
from src.api import config


def _corrected_simulation_code(question, verilog_code, model_matrix, testbench_path, max_change_count=25, if_generate_waveform=False):
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
            result.append(generate_change_report(change_count, "syntax", gpt_response, verilog_code, error_message, response_verilog_code, if_generate_waveform))
            verilog_code = response_verilog_code
        else:
            simulation_status = "Pass"
            testbench_code = read_file(testbench_path)
            testbench_response = run_testbench(verilog_code, testbench_path, if_generate_waveform)

            if testbench_response.get("status") == "success":
                result.append(generate_final_report(verilog_code, change_count, "Pass", "100", testbench_response))
                print(f"Pass testbench. Elapsed: {round(time.time() - start_time, 2)}s")
                return result

            tb_message = testbench_response.get("message", "")
            if len(tb_message) > 3000:
                tb_message = "Fail"
                print("Shortened testbench response")
            gpt_messages = get_testbench_error_message(model_matrix[model_count], verilog_code, testbench_code, tb_message, question, if_generate_waveform)
            gpt_response = chat_with_llm(gpt_messages, model_matrix[model_count])
            response_verilog_code = extract_verilog_code(gpt_response)
            change_count += 1
            print(f"Change {change_count}. Model: {model_matrix[model_count]}. Elapsed: {round(time.time() - start_time, 2)}s")
            result.append(generate_change_report(change_count, "testbench", gpt_response, verilog_code, testbench_response, response_verilog_code, if_generate_waveform))
            verilog_code = response_verilog_code

    result.append(generate_final_report(verilog_code, change_count, simulation_status, 0, ""))
    print(f"Max iterations reached. Elapsed: {round(time.time() - start_time, 2)}s")
    return result


def auto_gen_verilog(req, request_id):
    workspace = config.SRC_DIR / "vlog_workspace"
    workspace.mkdir(exist_ok=True)

    testbench_path = workspace / "testbench.v"
    with open(testbench_path, "w", encoding="utf-8") as f:
        f.write(req.testbench)

    initial_messages = get_initial_message(req.model_matrix[0], req.question)
    verilog_code = extract_verilog_code(chat_with_llm(initial_messages, req.model_matrix[0]))

    return _corrected_simulation_code(req.question, verilog_code, req.model_matrix, testbench_path, req.max_count)
