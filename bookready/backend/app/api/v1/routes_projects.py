from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ...core.security import User, get_current_user
from ...models.project import Project, ProjectCreate
from ...services.projects import (
    ProjectNotFoundError,
    get_project_store,
)

router = APIRouter()

_store = get_project_store()


@router.post("/", response_model=Project)
async def create_project(payload: ProjectCreate, user: User = Depends(get_current_user)) -> Project:  # noqa: B008
    return _store.create(payload)


@router.get("/", response_model=list[Project])
async def list_projects(user: User = Depends(get_current_user)) -> list[Project]:  # noqa: B008
    return _store.list()


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, user: User = Depends(get_current_user)) -> Project:  # noqa: B008
    try:
        return _store.get(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, payload: ProjectCreate, user: User = Depends(get_current_user)) -> Project:  # noqa: B008
    try:
        return _store.update(project_id, payload)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
