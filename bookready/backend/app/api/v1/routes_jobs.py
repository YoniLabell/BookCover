from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ...core.security import User, get_current_user
from ...services.jobs import get_job_service

router = APIRouter()
_job_service = get_job_service()


@router.get("/{job_id}")
async def get_job(job_id: str, user: User = Depends(get_current_user)) -> dict[str, object]:  # noqa: B008
    try:
        job = _job_service.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return job.dict()
