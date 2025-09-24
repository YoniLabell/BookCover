from __future__ import annotations

from pathlib import Path
from typing import Literal, Tuple

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import User, get_current_user
from ...services.validators import ValidationError, result_to_dict, validate_content, validate_cover

router = APIRouter()


class ContentValidationRequest(BaseModel):
    pdf_path: str
    trim: Tuple[float, float]
    bleed_mm: float = 0.0


class CoverValidationRequest(BaseModel):
    pdf_path: str
    trim: Tuple[float, float]
    bleed_mm: float
    spine_mm: float


@router.post("/content")
async def validate_content_pdf(payload: ContentValidationRequest, user: User = Depends(get_current_user)) -> dict[str, object]:  # noqa: B008
    try:
        result = validate_content(Path(payload.pdf_path), payload.trim, payload.bleed_mm)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result_to_dict(result)


@router.post("/cover")
async def validate_cover_pdf(payload: CoverValidationRequest, user: User = Depends(get_current_user)) -> dict[str, object]:  # noqa: B008
    try:
        result = validate_cover(Path(payload.pdf_path), payload.trim, payload.bleed_mm, payload.spine_mm)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result_to_dict(result)
