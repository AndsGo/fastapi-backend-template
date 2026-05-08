from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domains.enums import ScheduledJobRunStatus


class ScheduledJobRun(TimestampMixin, Base):
    __tablename__ = "scheduled_job_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("scheduled_jobs.id"), nullable=False)
    status: Mapped[ScheduledJobRunStatus] = mapped_column(
        String(32),
        default=ScheduledJobRunStatus.pending,
    )
    started_at: Mapped[datetime | None] = mapped_column(default=None)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)
    duration_ms: Mapped[int | None] = mapped_column(default=None)
    triggered_by: Mapped[str] = mapped_column(String(128), default="system")
    trigger_info: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=None)
    worker_id: Mapped[str | None] = mapped_column(String(128), default=None)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    job = relationship("ScheduledJob", back_populates="runs")
