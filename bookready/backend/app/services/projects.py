from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict
from uuid import uuid4

from ..models.project import Project, ProjectCreate


class ProjectNotFoundError(KeyError):
    """Raised when a project cannot be located in the store."""


@dataclass
class ProjectStore:
    """In-memory store for project data.

    This keeps the backend routes simple while providing a single place where
    we can encapsulate update behaviour such as touching ``updated_at`` when an
    asset is attached or project details change.
    """

    _projects: Dict[str, Project] = field(default_factory=dict)

    def create(self, payload: ProjectCreate) -> Project:
        project_id = uuid4().hex
        project = Project(id=project_id, **payload.model_dump())
        self._projects[project_id] = project
        return project

    def list(self) -> list[Project]:
        return list(self._projects.values())

    def get(self, project_id: str) -> Project:
        try:
            return self._projects[project_id]
        except KeyError as exc:  # pragma: no cover - simple mapping error
            raise ProjectNotFoundError(project_id) from exc

    def update(self, project_id: str, payload: ProjectCreate) -> Project:
        existing = self.get(project_id)
        project = existing.copy(update=payload.model_dump())
        project.updated_at = datetime.utcnow()
        self._projects[project_id] = project
        return project

    def attach_asset(self, project_id: str, kind: str, key: str) -> Project:
        project = self.get(project_id)
        updates: dict[str, str] = {}
        if kind == "content":
            updates["content_key"] = key
        elif kind == "cover":
            updates["cover_key"] = key
        else:  # pragma: no cover - guarded by validation upstream
            raise ValueError(f"Unsupported asset kind: {kind}")
        updates["updated_at"] = datetime.utcnow()
        project = project.copy(update=updates)
        self._projects[project_id] = project
        return project

    def clear(self) -> None:
        self._projects.clear()


_STORE = ProjectStore()


def get_project_store() -> ProjectStore:
    return _STORE


def reset_project_store() -> None:
    _STORE.clear()
