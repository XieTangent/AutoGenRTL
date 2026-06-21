import os
import time
import signal
from pathlib import Path
from utils import create_verilog_from_file_multiple_workers
import utils

def handle_exit(signum, frame):
    global end_time
    end_time = time.time()
    print(f"Total time: {end_time - start_time} seconds")
    print("Now time: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("All done!")
    exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    utils.IF_GENERATE_WAVEFORM = True # 是否生成時序圖迭代
    utils.IF_GENERATE_WAVEFORM_JSON = True # 是否根據時序圖 json 迭代
    max_count = 15                    # 最大可迭代次數
    verilog_tests_name = "test_set"   # data/ 中要测试的文件夹名称
    result_name = "test_wavefrom_result"       # 要生成的 result 名称 (若名称相同会在同目录继续生成 result2)
    model_matrix = [
        "o1-mini" ,          # 你要使用的LLM
        "o1"
    ]
    # 可使用 LLM
    # MODEL_FORMATS = {
    #     "openai": [
    #         "gpt-4",
    #         "o1-mini",
    #         "gpt-4o-mini",
    #         "gpt-4o",
    #         "gpt-3.5-turbo",
    #         "o3-mini"
    #     ],
    #     "llamma": [
    #         "llamma"
    #     ],
    #     "finetune_llamma": [
    #         "finetune_llamma"
    #     ],
    #     "grok": [
    #         "grok-3-mini-beta",
    #     ]
    # }
    SCRIPT_PATH = Path(__file__).resolve().parent
    DATA_PATH = SCRIPT_PATH.parent / "data"
    PROBLEM_PATH = DATA_PATH / verilog_tests_name

    start_time = time.time()
    for i in range(1, 2):
        create_verilog_from_file_multiple_workers(PROBLEM_PATH, result_name, model_matrix ,max_count,i)
        # if_generate_waveform
    
    end_time = time.time()
    print(f"Total time: {end_time - start_time} seconds")
    print("Now time: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print("All done!")
