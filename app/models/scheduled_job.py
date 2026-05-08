from datetime import datetime
from typing import Any

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.types import case_sensitive_string
from app.domains.enums import ScheduledJobStatus


class ScheduledJob(TimestampMixin, Base):
    __tablename__ = "scheduled_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(
        case_sensitive_string(128),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    cron_expression: Mapped[str] = mapped_column(String(128), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    job_type: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[ScheduledJobStatus] = mapped_column(
        String(32),
        default=ScheduledJobStatus.enabled,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    last_run_at: Mapped[datetime | None] = mapped_column(default=None)
    next_run_at: Mapped[datetime | None] = mapped_column(default=None)
    lock_ttl_seconds: Mapped[int] = mapped_column(default=60)
    max_runtime_seconds: Mapped[int] = mapped_column(default=900)
    misfire_policy: Mapped[str] = mapped_column(String(32), default="run_once")
    concurrent_policy: Mapped[str] = mapped_column(String(32), default="forbid")

    runs = relationship("ScheduledJobRun", back_populates="job")
