from app.jobs.handlers.example import noop
from app.jobs.registry import JobContext


def test_example_noop_job_returns_success_result() -> None:
    context = JobContext(
        job_id=1,
        run_id=10,
        job_type="example.noop",
        payload={},
        triggered_by="manual",
        worker_id="worker-1",
        db=object(),
        redis=object(),
    )

    result = noop(context)

    assert result.status == "succeeded"
    assert result.processed_count == 1
    assert result.succeeded_count == 1
    assert result.failed_count == 0
    assert result.details == {"job_type": "example.noop", "run_id": 10}
