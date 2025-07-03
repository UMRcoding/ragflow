import base64

from core.logger import logger
from fastapi import Request
from models.enums import ResultStatus
from models.schemas import CodeExecutionRequest, CodeExecutionResult
from services.execution import execute_code
from services.limiter import limiter
from services.security import analyze_code_security
from core.container import _CONTAINER_EXECUTION_SEMAPHORES

async def healthz_handler():
    return {"status": "ok"}

@limiter.limit("5/second")
async def run_code_handler(req: CodeExecutionRequest, request: Request):
    logger.info("🟢 Received /run request")

    async with _CONTAINER_EXECUTION_SEMAPHORES[req.language]:
        code = base64.b64decode(req.code_b64).decode("utf-8")
        is_safe, issues = analyze_code_security(code, language=req.language)
        if not is_safe:
            issue_details = "\n".join([f"Line {lineno}: {issue}" for issue, lineno in issues])
            return CodeExecutionResult(status=ResultStatus.PROGRAM_RUNNER_ERROR, stdout="", stderr=issue_details, exit_code=-999, detail="Code is unsafe")

        try:
            return await execute_code(req)
        except Exception as e:
            return CodeExecutionResult(status=ResultStatus.PROGRAM_RUNNER_ERROR, stdout="", stderr=str(e), exit_code=-999, detail="unhandled_exception")
