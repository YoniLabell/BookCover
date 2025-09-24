from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import User, get_current_user
from ...services.jobs import get_job_service
from ...workers.tasks import job_export_project

router = APIRouter()
_job_service = get_job_service()


class ExportRequest(BaseModel):
    project_id: str
    content_path: str
    cover_path: str
    report_data: dict[str, object]


class ExportJobResponse(BaseModel):
    job_id: str
    status: str


@router.post("/{project_id}", response_model=ExportJobResponse)
async def export_project(project_id: str, payload: ExportRequest, user: User = Depends(get_current_user)) -> ExportJobResponse:  # noqa: B008
    if project_id != payload.project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    try:
        job = _job_service.enqueue(
            job_export_project,
            payload.project_id,
            payload.content_path,
            payload.cover_path,
            payload.report_data,
            job_type="export",
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ExportJobResponse(job_id=job.id, status=job.status.value)
