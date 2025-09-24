from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors

from ..core.config import get_settings
from .validators import ValidationCheck


class ReportService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def save_json(self, project_id: str, data: Dict[str, object]) -> Path:
        project_dir = self.settings.report_media_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        json_path = project_dir / "report.json"
        json_path.write_text(json.dumps(data, indent=2))
        return json_path

    def save_pdf(self, project_id: str, title: str, sections: Dict[str, List[ValidationCheck]]) -> Path:
        project_dir = self.settings.report_media_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = project_dir / "report.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
        for section, checks in sections.items():
            story.append(Paragraph(section, styles["Heading2"]))
            data = [["Check", "Result", "Details"]]
            for check in checks:
                result = "PASS" if check.ok else "FAIL"
                data.append([check.id, result, check.details])
            table = Table(data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("TEXTCOLOR", (1, 1), (1, -1), colors.green),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 12))
        doc.build(story)
        return pdf_path


def get_report_service() -> ReportService:
    return ReportService()
