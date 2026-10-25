from fastapi import FastAPI, HTTPException, Query
from app.api.schemas import JobCreateRequest, JobResponse, JobStatus
import uuid

app = FastAPI()
jobs_db: dict[str, JobResponse] = {}

@app.get("/")
def read_root():
    return {"service": "kube-pipeline-api", "message": "Hello CKA & FastAPI!"}

@app.get("/healthz")
def read_healthz():
    return {"status": "ok"}

@app.post("/jobs", status_code=201)
def create_job(job_req: JobCreateRequest) -> JobResponse:
    new_id = f"job-{uuid.uuid4().hex[:8]}"
    new_job = JobResponse(
        job_id=new_id,
        task_type=job_req.task_type,
        target_file=job_req.target_file,
        priority=job_req.priority,
        status=JobStatus.PENDING,
        message="Job submitted successfully"
    )
    jobs_db[new_id] = new_job

    return new_job

@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> JobResponse:
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return jobs_db[job_id]

@app.get("/jobs")
def list_jobs(
    status: JobStatus | None = None,
    limit: int = Query(default=10, ge=1, le=50, description="최대 조회 개수 (1~50)")
) -> list[JobResponse]:
    jobs = list(jobs_db.values())
   
    if status is not None:
        filtered_jobs = [x for x in jobs if x.status == status]
    else:
        filtered_jobs = jobs

    return filtered_jobs[:limit]