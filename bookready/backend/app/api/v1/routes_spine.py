from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.config import get_settings
from ...core.security import User, get_current_user
from ...services.spine import SpineCalculator, calculate_spine

router = APIRouter()


class SpineRequest(BaseModel):
    pages: int
    paper_type: str


class SpineResponse(BaseModel):
    spine_mm: float


class PaperTypeResponse(BaseModel):
    paper_types: dict[str, float]


@router.post("/calc", response_model=SpineResponse)
async def calc_spine(payload: SpineRequest, user: User = Depends(get_current_user)) -> SpineResponse:  # noqa: B008
    settings = get_settings()
    calculator = SpineCalculator.from_file(settings.paper_data_path)
    try:
        spine = calculator.calculate(payload.pages, payload.paper_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SpineResponse(spine_mm=spine)


@router.get("/paper-types", response_model=PaperTypeResponse)
async def list_paper_types(user: User = Depends(get_current_user)) -> PaperTypeResponse:  # noqa: B008
    settings = get_settings()
    calc = SpineCalculator.from_file(settings.paper_data_path)
    return PaperTypeResponse(paper_types=calc.list_paper_types())
