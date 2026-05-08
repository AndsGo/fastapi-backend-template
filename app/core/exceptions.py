from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
            details={"id": resource_id},
        )


class ConflictError(AppException):
    def __init__(self, resource: str, message: str) -> None:
        super().__init__(
            code=f"{resource.upper()}_CONFLICT",
            message=message,
            status_code=409,
        )


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )
