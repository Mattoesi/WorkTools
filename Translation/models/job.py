# app/models/job.py
from enum import Enum
from pathlib import Path
from datetime import datetime, UTC
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PARTIAL_SUCCESS = "partial_success"
    SUCCESS = "success"
    FAILED = "failed"


class TranslationJob(BaseModel):
    id: str
    document_id: str
    input_path: Path
    target_language: str
    status: JobStatus = JobStatus.QUEUED
    current_stage: str = "ingestion"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    logs: list[str] = Field(default_factory=list)
    error: str | None = None
    checkpoint_path: Path | None = None