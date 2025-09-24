from __future__ import annotations

import json
from pathlib import Path

from ..core.config import get_settings
from ..services.pdf_fix import fix_content
from ..services.report import ReportService


def job_fix_content(project_id: str, source_key: str, icc_profile: str | None = None) -> str:
    profile_path = Path(icc_profile) if icc_profile else None
    output_path = fix_content(project_id, source_key, profile_path)
    return str(output_path)


def job_export_project(project_id: str, content_path: str, cover_path: str, report_data: dict[str, object]) -> dict[str, str]:
    settings = get_settings()
    export_dir = settings.media_root / project_id / "export"
    export_dir.mkdir(parents=True, exist_ok=True)
    output_content = export_dir / "content.pdf"
    output_cover = export_dir / "cover.pdf"
    output_report = export_dir / "report.json"
    Path(content_path).replace(output_content)
    Path(cover_path).replace(output_cover)
    output_report.write_text(json.dumps(report_data, indent=2))
    report_service = ReportService()
    report_pdf = report_service.save_pdf(project_id, "BookReady Report", {})
    return {
        "content": str(output_content),
        "cover": str(output_cover),
        "report_json": str(output_report),
        "report_pdf": str(report_pdf),
    }
