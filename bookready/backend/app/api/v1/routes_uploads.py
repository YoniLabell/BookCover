from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.security import User, get_current_user
from ...models.project import Project
from ...services.antivirus import get_antivirus_service
from ...services.projects import ProjectNotFoundError, get_project_store
from ...services.storage import StorageService

router = APIRouter()


class PresignRequest(BaseModel):
    project_id: str
    kind: Literal["content", "cover"]
    filename: str
    content_type: str
    content_length: int = Field(..., gt=0)


class PresignResponse(BaseModel):
    url: str
    fields: dict[str, str]
    key: str


class UploadComplete(BaseModel):
    project_id: str
    kind: Literal["content", "cover"]
    key: str


class UploadCompleteResponse(BaseModel):
    status: Literal["stored"]
    key: str
    project: Project


_storage = StorageService()
_antivirus = get_antivirus_service()
_projects = get_project_store()


@router.post("/presign", response_model=PresignResponse)
async def presign_upload(payload: PresignRequest, user: User = Depends(get_current_user)) -> PresignResponse:  # noqa: B008
    key = _storage.generate_key(payload.project_id, payload.kind, payload.filename)
    post = _storage.presign_post(key, payload.content_type, payload.content_length)
    return PresignResponse(url=post.url, fields={k: str(v) for k, v in post.fields.items()}, key=post.key)


@router.post("/complete", response_model=UploadCompleteResponse)
async def complete_upload(payload: UploadComplete, user: User = Depends(get_current_user)) -> UploadCompleteResponse:  # noqa: B
    try:
        project = _projects.attach_asset(payload.project_id, payload.kind, payload.key)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    return UploadCompleteResponse(status="stored", key=payload.key, project=project)


@router.get("/antivirus")
async def antivirus_status(user: User = Depends(get_current_user)) -> dict[str, bool]:  # noqa: B008
    return {"healthy": _antivirus.ping()}
