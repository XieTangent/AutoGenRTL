# src/verilog_api/models.py

from pydantic import BaseModel
from typing import List, Optional

class AutoGenRequest(BaseModel):
    question: str
    model_matrix: List[str]
    testbench: str
    max_count: int = 25
    # generate_waveform: Optional[bool] = False
    # generate_waveform_json: Optional[bool] = False
