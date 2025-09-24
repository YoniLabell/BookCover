from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import User, get_current_user
from ...services.jobs import get_job_service
from ...workers.tasks import job_fix_content

router = APIRouter()


class FixContentRequest(BaseModel):
    project_id: str
    source_key: str
    icc_profile: str | None = None


class JobResponse(BaseModel):
    job_id: str
    status: str


_job_service = get_job_service()


@router.post("/content", response_model=JobResponse)
async def queue_fix_content(payload: FixContentRequest, user: User = Depends(get_current_user)) -> JobResponse:  # noqa: B008
    try:
        job = _job_service.enqueue(job_fix_content, payload.project_id, payload.source_key, payload.icc_profile, job_type="fix")
    except Exception as exc:  # pragma: no cover - redis errors propagate
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return JobResponse(job_id=job.id, status=job.status.value)
