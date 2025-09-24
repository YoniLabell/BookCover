from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    started = "started"
    finished = "finished"
    failed = "failed"


class Job(BaseModel):
    id: str
    type: str
    status: JobStatus = JobStatus.queued
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    progress: float = 0.0
    output_keys: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    meta: dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True
