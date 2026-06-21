from pathlib import Path
import uvicorn
from fastapi import FastAPI

from src.api.routes import router as verilog_router

app = FastAPI(
    title="Verilog AutoGen API",
    version="1.0.0",
    description="Generate and simulate Verilog code via LLM"
)

app.include_router(verilog_router, prefix="/api/verilog")

if __name__ == "__main__":
    uvicorn.run("bin.run_api:app", host="0.0.0.0", port=8000, reload=True)
