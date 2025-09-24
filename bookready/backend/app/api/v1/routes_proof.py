from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ...core.security import User, get_current_user
from ...services.proofs import get_proof_service

router = APIRouter()
_proofs = get_proof_service()


@router.get("/content/{project_id}")
async def get_content_proof(project_id: str, pdf_path: str, user: User = Depends(get_current_user)) -> dict[str, object]:  # noqa: B008
    try:
        images = _proofs.proof_content(Path(pdf_path))
    except Exception as exc:  # pragma: no cover - external binary errors propagate
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"project_id": project_id, "images": images}


@router.get("/cover/{project_id}")
async def get_cover_proof(project_id: str, pdf_path: str, user: User = Depends(get_current_user)) -> dict[str, object]:  # noqa: B008
    try:
        image = _proofs.proof_cover(Path(pdf_path))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"project_id": project_id, "image": image}
