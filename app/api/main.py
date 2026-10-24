from fastapi import FastAPI
from app.api.schemas import JobCreateRequest, JobResponse, JobStatus
import uuid

app = FastAPI()

@app.get("/")
def read_root():
    return {"service": "kube-pipeline-api", "message": "Hello CKA & FastAPI!"}

@app.get("/healthz")
def read_healthz():
    return {"status": "ok"}

@app.post("/jobs", status_code=201)
def create_job(job_req: JobCreateRequest) -> JobResponse:
    new_id = f"job-{uuid.uuid4().hex[:8]}"

    return JobResponse(
        job_id=new_id,
        task_type=job_req.task_type,
        target_file=job_req.target_file,
        priority=job_req.priority,
        status=JobStatus.PENDING,
        message="Job submitted successfully"
    )