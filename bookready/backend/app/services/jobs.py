from __future__ import annotations

import uuid
from datetime import datetime

import redis
from rq import Queue

from ..core.config import get_settings
from ..models.job import Job, JobStatus


class JobService:
    def __init__(self) -> None:
        settings = get_settings()
        self._redis = redis.from_url(settings.redis_url)
        self._queue = Queue("bookready", connection=self._redis)

    def enqueue(self, func, *args, job_type: str, **kwargs) -> Job:
        job_id = uuid.uuid4().hex
        rq_job = self._queue.enqueue(func, *args, job_id=job_id, **kwargs)
        job = Job(id=rq_job.id, type=job_type, status=JobStatus.queued)
        return job

    def get(self, job_id: str) -> Job:
        rq_job = self._queue.fetch_job(job_id)
        if not rq_job:
            raise KeyError(job_id)
        status_map = {
            "queued": JobStatus.queued,
            "started": JobStatus.started,
            "finished": JobStatus.finished,
            "failed": JobStatus.failed,
        }
        status = status_map.get(rq_job.get_status(refresh=True), JobStatus.queued)
        progress = rq_job.meta.get("progress", 0.0) if rq_job.meta else 0.0
        output = rq_job.meta.get("output", []) if rq_job.meta else []
        error = rq_job.meta.get("error") if rq_job.meta else None
        return Job(
            id=rq_job.id,
            type=rq_job.meta.get("type", "job"),
            status=status,
            created_at=datetime.fromtimestamp(rq_job.created_at.timestamp()) if rq_job.created_at else datetime.utcnow(),
            updated_at=datetime.utcnow(),
            progress=progress,
            output_keys=output,
            error=error,
            meta=rq_job.meta or {},
        )


def get_job_service() -> JobService:
    return JobService()
