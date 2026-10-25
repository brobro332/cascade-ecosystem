import platform
from app.api.schemas import JobResponse, JobStatus

def process_job_in_background(
    job_id: str,
    jobs_db: dict[str, JobResponse],
    node_name: str = "local-dev-node",
) -> None:
    """백그라운드에서 작업을 처리하고 상태를 COMPLETED로 변경하는 워커 함수"""
    if job_id not in jobs_db:
        return

    job = jobs_db[job_id]
    arch = platform.machine() 

    jobs_db[job_id] = job.model_copy(
        update={
            "status": JobStatus.COMPLETED,
            "message": f"Processed [{job.task_type.value}] on {node_name} ({arch})",
        }
    )
