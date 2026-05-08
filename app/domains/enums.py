from enum import StrEnum


class TaskStatus(StrEnum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"


class ScheduledJobStatus(StrEnum):
    enabled = "enabled"
    disabled = "disabled"
    archived = "archived"


class ScheduledJobRunStatus(StrEnum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"
