from fastapi import APIRouter
from uuid import uuid4

from src.api.models import AutoGenRequest
from src.api.services.auto_gen_verilog import auto_gen_verilog

router = APIRouter()

@router.post("/auto_gen")
def auto_gen_verilog_api(req: AutoGenRequest):
    request_id = str(uuid4())
    result = auto_gen_verilog(req, request_id=request_id)
    return result