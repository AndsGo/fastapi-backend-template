import pytest

from app.jobs.registry import (
    JobContext,
    JobRegistry,
    JobResult,
    JobRouter,
    UnknownJobTypeError,
)


def test_registry_calls_registered_handler() -> None:
    registry = JobRegistry()
    context = JobContext(
        job_id=1,
        run_id=10,
        job_type="example.sync",
        payload={"limit": 2},
        triggered_by="scheduler",
        worker_id="worker-1",
        db=object(),
        redis=object(),
    )

    def handler(received_context: JobContext) -> JobResult:
        assert received_context.job_type == "example.sync"
        return JobResult(processed_count=2, succeeded_count=2, failed_count=0)

    registry.register("example.sync", handler)

    result = registry.execute(context)

    assert result.status == "succeeded"
    assert result.processed_count == 2
    assert result.details == {}


def test_register_duplicate_job_type_raises_value_error() -> None:
    registry = JobRegistry()

    def handler(context: JobContext) -> JobResult:
        return JobResult(details={"job_type": context.job_type})

    registry.register("example.sync", handler)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("example.sync", handler)


def test_get_unknown_job_type_raises_unknown_job_type_error() -> None:
    registry = JobRegistry()
    missing_job_type = "missing.job"

    with pytest.raises(UnknownJobTypeError, match=missing_job_type) as exc_info:
        registry.get(missing_job_type)

    assert exc_info.value.job_type == missing_job_type


def test_registry_includes_router_handlers() -> None:
    router = JobRouter()

    @router.handler("example.sync")
    def sync_example(context: JobContext) -> JobResult:
        return JobResult(processed_count=int(context.payload["limit"]))

    registry = JobRegistry()
    registry.include_router(router)
    context = JobContext(
        job_id=1,
        run_id=10,
        job_type="example.sync",
        payload={"limit": 3},
        triggered_by="scheduler",
        worker_id="worker-1",
        db=object(),
        redis=object(),
    )

    result = registry.execute(context)

    assert result.processed_count == 3


def test_router_handler_rejects_invalid_handler_signature() -> None:
    router = JobRouter()

    with pytest.raises(TypeError, match="must accept exactly one JobContext argument"):

        @router.handler("invalid.job")
        def invalid() -> JobResult:
            return JobResult()


def test_router_handler_rejects_non_job_result_return_annotation() -> None:
    router = JobRouter()

    with pytest.raises(TypeError, match="must return JobResult"):

        @router.handler("invalid.job")
        def invalid(context: JobContext) -> dict[str, object]:
            return {}


def test_router_handler_accepts_deferred_annotations() -> None:
    router = JobRouter()

    def sync_example(context):
        return JobResult(processed_count=int(context.payload["limit"]))

    sync_example.__annotations__ = {
        "context": "JobContext",
        "return": "JobResult",
    }

    router.handler("example.sync")(sync_example)

    assert "example.sync" in router.handlers


def test_include_router_rejects_duplicate_job_type() -> None:
    first = JobRouter()
    second = JobRouter()

    @first.handler("example.sync")
    def sync_example(context: JobContext) -> JobResult:
        return JobResult()

    @second.handler("example.sync")
    def sync_example_again(context: JobContext) -> JobResult:
        return JobResult()

    registry = JobRegistry()
    registry.include_router(first)

    with pytest.raises(ValueError, match="already registered"):
        registry.include_router(second)
