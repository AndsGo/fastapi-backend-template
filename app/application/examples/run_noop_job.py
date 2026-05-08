from app.jobs.registry import JobContext, JobResult


class RunNoopJobUseCase:
    def execute(self, context: JobContext) -> JobResult:
        return JobResult(
            processed_count=1,
            succeeded_count=1,
            failed_count=0,
            details={
                "job_type": context.job_type,
                "run_id": context.run_id,
            },
        )
