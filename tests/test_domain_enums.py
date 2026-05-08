from app.domains.enums import (
    ScheduledJobRunStatus,
    ScheduledJobStatus,
    TaskStatus,
)


def test_task_status_values_are_stable() -> None:
    assert [status.value for status in TaskStatus] == [
        "pending",
        "running",
        "succeeded",
        "failed",
        "canceled",
    ]


def test_scheduled_job_status_values_are_stable() -> None:
    assert [status.value for status in ScheduledJobStatus] == [
        "enabled",
        "disabled",
        "archived",
    ]


def test_scheduled_job_run_status_values_are_stable() -> None:
    assert [status.value for status in ScheduledJobRunStatus] == [
        "pending",
        "running",
        "succeeded",
        "failed",
        "canceled",
    ]
