from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import (
    routes_auth,
    routes_cover,
    routes_export,
    routes_fix,
    routes_jobs,
    routes_projects,
    routes_proof,
    routes_spine,
    routes_uploads,
    routes_validate,
)
from .core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(routes_projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(routes_uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(routes_validate.router, prefix="/api/v1/validate", tags=["validation"])
app.include_router(routes_fix.router, prefix="/api/v1/fix", tags=["fix"])
app.include_router(routes_spine.router, prefix="/api/v1/spine", tags=["spine"])
app.include_router(routes_cover.router, prefix="/api/v1/cover", tags=["cover"])
app.include_router(routes_proof.router, prefix="/api/v1/proof", tags=["proof"])
app.include_router(routes_export.router, prefix="/api/v1/export", tags=["export"])
app.include_router(routes_jobs.router, prefix="/api/v1/jobs", tags=["jobs"])


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}
