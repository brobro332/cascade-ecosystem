from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel, Field

class TaskType(str, Enum):
    RESIZE = "resize"
    WATERMARK = "watermark"
    SUMMARY = "summary"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobCreateRequest(BaseModel):
    task_type: TaskType
    target_file: str = Field(..., min_length=1, description="처리 대상 파일명")
    priority: int = Field(default=3, ge=1, le=5, description="우선순위 (1~5, 기본값 3)")

class JobResponse(BaseModel):
    job_id: str
    task_type: TaskType
    target_file: str
    priority: int
    status: JobStatus
    message: str