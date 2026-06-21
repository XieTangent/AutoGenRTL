import json
import os

def statistical_data(directory, i):
    test_number = 0 
    simulation_pass_count = 0
    no_change_simulation_pass_count = 0
    testbench_pass_count = 0
    no_change_testbench_pass_count = 0                  # 沒有迭代就通過
    one_change_testbench_pass_count = 0                 # 1次內通過
    five_change_testbench_pass_count = 0                # 5次內通過
    ten_change_testbench_pass_count = 0                 # 10次內通過
    fifteen_change_testbench_pass_count = 0             # 15次內通過
    twenty_change_testbench_pass_count = 0              # 20次內通過
    twentyfive_change_testbench_pass_count = 0          # 25次內通過

    total_iteration = 0
    total_test_number = 0
    total_simulation_pass_count = 0
    total_no_change_simulation_pass_count = 0
    total_testbench_pass_count = 0
    total_no_change_testbench_pass_count = 0            # 沒有迭代就通過
    total_one_change_testbench_pass_count = 0           # 1次內通過
    total_five_change_testbench_pass_count = 0          # 5次內通過
    total_ten_change_testbench_pass_count = 0           # 10次內通過
    total_fifteen_change_testbench_pass_count = 0       # 15次內通過
    total_twenty_change_testbench_pass_count = 0        # 20次內通過
    total_twentyfive_change_testbench_pass_count = 0    # 25次內通過
    

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    directory = os.path.join(base_dir, directory)
    
    prev_difficulty = None
    prev_type = None

    with open(f"{directory}.txt", "w") as file:
        pass

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == f"result{i}.json":
                result_path = os.path.join(root, file)

                with open(result_path, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)

                directory_name = os.path.basename(root)
                path_parts = root.replace(directory, "").strip(os.sep).split(os.sep)

                if not path_parts or len(path_parts) == 0:
                    print(f"path_parts is empty or does not exist: {path_parts}")
                    continue

                # 自動判斷 type/difficulty（如果不足就給 General）
                if len(path_parts) >= 3:
                    type = path_parts[0]
                    difficulty = path_parts[1]
                else:
                    type = "General"
                    difficulty = "General"

                with open(f"{directory}.txt", "a", encoding='utf-8') as file:
                    if type != prev_type or difficulty != prev_difficulty:
                        if prev_type is not None and prev_difficulty is not None:
                            print(
                                f"\nNumber of test in result{i}: {test_number}\n"
                                f"Number of simulation right in result{i}: {simulation_pass_count}\n"
                                f"Number of simulation right and no change in result{i}: {no_change_simulation_pass_count}\n"
                                f"Number of testbench right in result{i}: {testbench_pass_count}\n"
                                f"Number of testbench right and no change in result{i}: {no_change_testbench_pass_count}\n"
                                f"Number of testbench right and one change in result{i}: {one_change_testbench_pass_count}\n"
                                f"Number of testbench right and five change in result{i}: {five_change_testbench_pass_count}\n"
                                f"Number of testbench right and ten change in result{i}: {ten_change_testbench_pass_count}\n"
                                f"Number of testbench right and fifteen change in result{i}: {fifteen_change_testbench_pass_count}\n"
                                f"Number of testbench right and twenty change in result{i}: {twenty_change_testbench_pass_count}\n"
                                f"Number of testbench right and twentyfive change in result{i}: {twentyfive_change_testbench_pass_count}\n"
                                "\n"
                                "#----------------------------------------------------------------#\n"
                                "\n"
                            )

                            file.write(
                                f"\nNumber of test in result{i}: {test_number}\n"
                                f"Number of simulation right in result{i}: {simulation_pass_count}\n"
                                f"Number of simulation right and no change in result{i}: {no_change_simulation_pass_count}\n"
                                f"Number of testbench right in result{i}: {testbench_pass_count}\n"
                                f"Number of testbench right and no change in result{i}: {no_change_testbench_pass_count}\n"
                                f"Number of testbench right and one change in result{i}: {one_change_testbench_pass_count}\n"
                                f"Number of testbench right and five change in result{i}: {five_change_testbench_pass_count}\n"
                                f"Number of testbench right and ten change in result{i}: {ten_change_testbench_pass_count}\n"
                                f"Number of testbench right and fifteen change in result{i}: {fifteen_change_testbench_pass_count}\n"
                                f"Number of testbench right and twenty change in result{i}: {twenty_change_testbench_pass_count}\n"
                                f"Number of testbench right and twentyfive change in result{i}: {twentyfive_change_testbench_pass_count}\n"
                                "\n"
                                "#----------------------------------------------------------------#\n"
                                "\n"
                            )

                            # reset
                            test_number = 0
                            simulation_pass_count = no_change_simulation_pass_count = 0
                            testbench_pass_count = no_change_testbench_pass_count = 0

                        prev_type = type
                        prev_difficulty = difficulty
                        print(f"Type: {type}, Difficulty: {difficulty}")
                        file.write(f"Type: {type}, Difficulty: {difficulty}\n\n")
                        
                    total_test_number += 1
                    test_number += 1

                    flag = 0
                    for item in result_data:
                        if "change_id" in item:
                            total_iteration += 1
                            if item["change_id"] == 1:
                                if item["change_by"] == "syntax":
                                    flag = 1
                                elif item["change_by"] == "testbench":
                                    total_no_change_simulation_pass_count += 1
                                    no_change_simulation_pass_count += 1
                                    flag = 1

                        if "Final_verilog" in item:                                 #舊題目用Final_veirlog
                            total_iteration += 1
                            if item["Simulation_status"] == "Pass":
                                total_simulation_pass_count += 1
                                simulation_pass_count += 1
                                if flag == 0:
                                    total_no_change_simulation_pass_count += 1
                                    no_change_simulation_pass_count += 1
                            if item["Testbench_successful_rate"] == 100.0 or item["Testbench_successful_rate"] == "100":          #舊題目用Testbench_sucessful_rate
                                total_testbench_pass_count += 1
                                testbench_pass_count += 1
                                print(f"{directory_name:<35}: Pass Change times: {item['Change_verilog_count']:>5}")
                                file.write(f"{directory_name:<35}: Pass Change times: {item['Change_verilog_count']:>5}\n")
                                if item["Change_verilog_count"] == 0:
                                    total_no_change_testbench_pass_count += 1
                                    no_change_testbench_pass_count += 1
                                if item["Change_verilog_count"] <= 1:
                                    total_one_change_testbench_pass_count += 1
                                    one_change_testbench_pass_count += 1
                                if item["Change_verilog_count"] <= 5:
                                    five_change_testbench_pass_count += 1
                                    total_five_change_testbench_pass_count += 1
                                if item["Change_verilog_count"] <= 10:
                                    ten_change_testbench_pass_count += 1
                                    total_ten_change_testbench_pass_count += 1
                                if item["Change_verilog_count"] <= 15:
                                    fifteen_change_testbench_pass_count += 1
                                    total_fifteen_change_testbench_pass_count += 1
                                if item["Change_verilog_count"] <= 20:
                                    twenty_change_testbench_pass_count += 1
                                    total_twenty_change_testbench_pass_count += 1
                                if item["Change_verilog_count"] <= 25:
                                    twentyfive_change_testbench_pass_count += 1
                                    total_twentyfive_change_testbench_pass_count += 1    
                            else:
                                print(f"{directory_name:<35}: Fail Change times: {item['Change_verilog_count']:>5}")
                                file.write(f"{directory_name:<35}: Fail Change times: {item['Change_verilog_count']:>5}\n")
    if type != "General" and difficulty != "General":
        print(
            f"\nNumber of test in result{i}: {test_number}\n"
            f"Number of simulation right in result{i}: {simulation_pass_count}\n"
            f"Number of simulation right and no change in result{i}: {no_change_simulation_pass_count}\n"
            f"Number of testbench right in result{i}: {testbench_pass_count}\n"
            f"Number of testbench right and no change in result{i}: {no_change_testbench_pass_count}\n"
            f"Number of testbench right and one change in result{i}: {one_change_testbench_pass_count}\n"
            f"Number of testbench right and five change in result{i}: {five_change_testbench_pass_count}\n"
            f"Number of testbench right and ten change in result{i}: {ten_change_testbench_pass_count}\n"
            f"Number of testbench right and fifteen change in result{i}: {fifteen_change_testbench_pass_count}\n"
            f"Number of testbench right and twenty change in result{i}: {twenty_change_testbench_pass_count}\n"
            f"Number of testbench right and twentyfive change in result{i}: {twentyfive_change_testbench_pass_count}\n"
            "\n"
            "#----------------------------------------------------------------#\n"
            "\n"
        )
        with open(f"{directory}.txt", "a") as file:
            file.write(
                f"\nNumber of test in result{i}: {test_number}\n"
                f"Number of simulation right in result{i}: {simulation_pass_count}\n"
                f"Number of simulation right and no change in result{i}: {no_change_simulation_pass_count}\n"
                f"Number of testbench right in result{i}: {testbench_pass_count}\n"
                f"Number of testbench right and no change in result{i}: {no_change_testbench_pass_count}\n"
                f"Number of testbench right and one change in result{i}: {one_change_testbench_pass_count}\n"
                f"Number of testbench right and five change in result{i}: {five_change_testbench_pass_count}\n"
                f"Number of testbench right and ten change in result{i}: {ten_change_testbench_pass_count}\n"
                f"Number of testbench right and fifteen change in result{i}: {fifteen_change_testbench_pass_count}\n"
                f"Number of testbench right and twenty change in result{i}: {twenty_change_testbench_pass_count}\n"
                f"Number of testbench right and twentyfive change in result{i}: {twentyfive_change_testbench_pass_count}\n"
                "\n"
                "#----------------------------------------------------------------#\n"
                "\n"
            )
    print(
        f"\nNumber of test in result{i}: {total_test_number}\n"
        f"Number of simulation right in result{i}: {total_simulation_pass_count}\n"
        f"Number of simulation right and no change in result{i}: {total_no_change_simulation_pass_count}\n"
        f"Number of testbench right in result{i}: {total_testbench_pass_count}\n"
        f"Number of testbench right and no change in result{i}: {total_no_change_testbench_pass_count}\n"
        f"Number of testbench right and one change in result{i}: {total_one_change_testbench_pass_count}\n"
        f"Number of testbench right and five change in result{i}: {total_five_change_testbench_pass_count}\n"
        f"Number of testbench right and ten change in result{i}: {total_ten_change_testbench_pass_count}\n"
        f"Number of testbench right and fifteen change in result{i}: {total_fifteen_change_testbench_pass_count}\n"
        f"Number of testbench right and twenty change in result{i}: {total_twenty_change_testbench_pass_count}\n"
        f"Number of testbench right and twentyfive change in result{i}: {total_twentyfive_change_testbench_pass_count}\n"
        f"Number of iteration in result{i}: {total_iteration}\n"
    )
    with open(f"{directory}.txt", "a") as file:
        file.write(
            f"\nNumber of test in result{i}: {total_test_number}\n"
            f"Number of simulation right in result{i}: {total_simulation_pass_count}\n"
            f"Number of simulation right and no change in result{i}: {total_no_change_simulation_pass_count}\n"
            f"Number of testbench right in result{i}: {total_testbench_pass_count}\n"
            f"Number of testbench right and no change in result{i}: {total_no_change_testbench_pass_count}\n"
            f"Number of testbench right and one change in result{i}: {total_one_change_testbench_pass_count}\n"
            f"Number of testbench right and five change in result{i}: {total_five_change_testbench_pass_count}\n"
            f"Number of testbench right and ten change in result{i}: {total_ten_change_testbench_pass_count}\n"
            f"Number of testbench right and fifteen change in result{i}: {total_fifteen_change_testbench_pass_count}\n"
            f"Number of testbench right and twenty change in result{i}: {total_twenty_change_testbench_pass_count}\n"
            f"Number of testbench right and twentyfive change in result{i}: {total_twentyfive_change_testbench_pass_count}\n"
            f"Number of iteration in result{i}: {total_iteration}"
        )

if __name__ == "__main__":
    for i in range(1, 2):
        statistical_data("266_o1_wave_result", i)
