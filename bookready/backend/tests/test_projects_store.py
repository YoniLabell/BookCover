from datetime import datetime
import pathlib
import sys

import pytest

pytest.importorskip("pydantic")

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "app"))

from models.project import ProjectCreate, ProjectSize  # type: ignore  # noqa: E402
from services.projects import ProjectStore  # type: ignore  # noqa: E402


def _sample_payload(name: str = "My Project") -> ProjectCreate:
    return ProjectCreate(
        name=name,
        size=ProjectSize(width_mm=148.0, height_mm=210.0),
        bleed_mm=3.0,
        paper_type="80gsm",
        color_space="CMYK",
    )


def test_create_and_get_project() -> None:
    store = ProjectStore()
    project = store.create(_sample_payload())

    fetched = store.get(project.id)

    assert fetched.id == project.id
    assert fetched.created_at <= datetime.utcnow()
    assert fetched.content_key is None
    assert fetched.cover_key is None


def test_update_project_replaces_fields_and_touches_timestamp() -> None:
    store = ProjectStore()
    project = store.create(_sample_payload("Initial"))

    updated = store.update(project.id, _sample_payload("Updated"))

    assert updated.name == "Updated"
    assert updated.size.width_mm == project.size.width_mm
    assert updated.updated_at >= project.updated_at


def test_attach_asset_sets_content_and_cover_keys() -> None:
    store = ProjectStore()
    project = store.create(_sample_payload())

    with_content = store.attach_asset(project.id, "content", "content-key.pdf")
    assert with_content.content_key == "content-key.pdf"

    with_cover = store.attach_asset(project.id, "cover", "cover-key.pdf")
    assert with_cover.cover_key == "cover-key.pdf"

    # Ensure the stored project reflects both keys
    fetched = store.get(project.id)
    assert fetched.content_key == "content-key.pdf"
    assert fetched.cover_key == "cover-key.pdf"
