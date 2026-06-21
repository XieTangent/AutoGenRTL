import re

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
        re.compile(r'(module\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\);.*?endmodule)', re.DOTALL)  # 直接匹配 module 結構
    ]
    
    for pattern in patterns:
        matches = pattern.findall(response)
        if matches:
            return matches[0].strip()
    
    print(f"Fail to extract verilog\nThis is response : \n{response}")
    return f"Fail to extract verilog. gpt response: {response}"