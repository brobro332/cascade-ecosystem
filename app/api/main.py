from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Depends, BackgroundTasks
from app.worker.processor import process_job_in_background
from app.api.config import Settings, get_settings
from app.api.schemas import JobCreateRequest, JobResponse, JobStatus, TaskType
from pathlib import Path
import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    app.state.is_ready = True

    yield

    app.state.is_ready = False

app = FastAPI(lifespan=lifespan)
app.state.is_ready = True

jobs_db: dict[str, JobResponse] = {}

@app.get("/")
def read_root(settings: Settings = Depends(get_settings)):
    return {
        "service": "kube-pipeline-api", 
        "message": "Hello CKA & FastAPI!",
        "node_name": settings.node_name
    }

@app.get("/healthz")
def read_healthz():
    return {"status": "ok"}

@app.post("/jobs", status_code=201)
def create_job(
    job_req: JobCreateRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
) -> JobResponse:
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

    background_tasks.add_task(process_job_in_background, new_id, jobs_db, settings.node_name)

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

@app.post("/jobs/upload", status_code=201)
async def upload_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="업로드할 원본 파일"),
    task_type: TaskType = Form(default=TaskType.RESIZE, description="작업 종류"),
    priority: int = Form(default=3, ge=1, le=5, description="우선순위 (1~5)"),
    settings: Settings = Depends(get_settings)
) -> JobResponse:
    contents = await file.read()
    if len(contents) == 0 or not contents:
        raise HTTPException(status_code=400, detail="Empty file is not allowed")
    else:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = settings.upload_dir / file.filename
        file_path.write_bytes(contents)
        
        new_id = f"job-{uuid.uuid4().hex[:8]}"
        new_job = JobResponse(
            job_id=new_id,
            target_file=file.filename,
            task_type=task_type,
            priority=priority,
            status=JobStatus.PENDING,
            message="File uploaded and job submitted"
        )

        jobs_db[new_id] = new_job

        background_tasks.add_task(process_job_in_background, new_id, jobs_db, settings.node_name)

        return new_job

@app.get("/readyz")
def read_readyz():
    if not getattr(app.state, "is_ready", False):
        raise HTTPException(status_code=503, detail="Service not ready")
    else:
        return {"status": "ready"}