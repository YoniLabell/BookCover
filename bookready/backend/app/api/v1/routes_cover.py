from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.security import User, get_current_user
from ...services.cover_gen import CoverTemplateRequest, generate_cover_template

router = APIRouter()


class CoverTemplatePayload(BaseModel):
    trim_width_mm: float
    trim_height_mm: float
    bleed_mm: float
    spine_mm: float
    safe_mm: float = 5.0
    barcode_width_mm: float = 15.0
    barcode_height_mm: float = 40.0
    barcode_offset_x_mm: float = 10.0
    barcode_offset_y_mm: float = 10.0
    output_path: str


@router.post("/template")
async def create_cover_template(payload: CoverTemplatePayload, user: User = Depends(get_current_user)) -> dict[str, str]:  # noqa: B008
    request = CoverTemplateRequest(
        trim_width_mm=payload.trim_width_mm,
        trim_height_mm=payload.trim_height_mm,
        bleed_mm=payload.bleed_mm,
        spine_mm=payload.spine_mm,
        safe_mm=payload.safe_mm,
        barcode_width_mm=payload.barcode_width_mm,
        barcode_height_mm=payload.barcode_height_mm,
        barcode_offset_x_mm=payload.barcode_offset_x_mm,
        barcode_offset_y_mm=payload.barcode_offset_y_mm,
    )
    try:
        pdf_path = generate_cover_template(Path(payload.output_path), request)
    except Exception as exc:  # pragma: no cover - ReportLab errors propagate
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"path": str(pdf_path)}
