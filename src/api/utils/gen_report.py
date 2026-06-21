import base64
from src.api import config

def generate_final_report(verilog_code, change_count, simulation_status, testbench_success_rate, testbench_response):
    new_list = {
        "Final_verilog": verilog_code,
        "Change_verilog_count": change_count,
        "Simulation_status": simulation_status,
        "Testbench_successful_rate": testbench_success_rate,
        "Testbench_response": testbench_response
    }
    return new_list

def generate_change_report(change_count, change_type, gpt_response, verilog_code, error_message, response_verilog_code, IF_GENERATE_WAVEFORM):
    new_list = {
            "change_id": change_count,
            "change_by": change_type,
            "gpt_response": gpt_response,
            "error_veirlog_code": verilog_code,
            "error_messages": error_message,
            "new_verilog_code": response_verilog_code
    }
    if change_type == "testbench" and IF_GENERATE_WAVEFORM:
        image_path = config.SRC_DIR / "vlog_workspace" / "waveform.png"
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        new_list["image_base64"] = encoded_image

    return new_list