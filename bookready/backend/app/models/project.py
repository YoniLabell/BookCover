from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectSize(BaseModel):
    width_mm: float
    height_mm: float


class ProjectCreate(BaseModel):
    name: str
    size: ProjectSize
    bleed_mm: float = 0.0
    paper_type: str = "80gsm"
    color_space: str = "CMYK"


class Project(ProjectCreate):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    content_key: Optional[str] = None
    cover_key: Optional[str] = None

    class Config:
        orm_mode = True
