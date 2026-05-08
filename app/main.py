from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        description="Reusable FastAPI backend template API.",
        version=settings.app_version,
        debug=settings.debug,
    )
    application.add_exception_handler(
        AppException,
        cast(Callable[[Request, Exception], Response | Awaitable[Response]], app_exception_handler),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()
