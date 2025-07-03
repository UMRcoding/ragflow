from fastapi import Request
from fastapi.responses import JSONResponse
from models.enums import ResultStatus
from models.schemas import CodeExecutionResult
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, RateLimitExceeded):
        return JSONResponse(
            content=CodeExecutionResult(
                status=ResultStatus.PROGRAM_RUNNER_ERROR,
                stdout="",
                stderr="Too many requests, please try again later",
                exit_code=-429,
                detail="Too many requests, please try again later",
            ).model_dump(),
        )
    raise exc
