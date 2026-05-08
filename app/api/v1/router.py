from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit_logs,
    examples,
    health,
    scheduled_jobs,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(examples.router, prefix="/examples", tags=["examples"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
api_router.include_router(scheduled_jobs.router, prefix="/scheduled-jobs", tags=["scheduled-jobs"])
