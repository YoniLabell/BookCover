from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfgen import canvas

MM_TO_PT = 72 / 25.4


@dataclass
class CoverTemplateRequest:
    trim_width_mm: float
    trim_height_mm: float
    bleed_mm: float
    spine_mm: float
    safe_mm: float
    barcode_width_mm: float
    barcode_height_mm: float
    barcode_offset_x_mm: float
    barcode_offset_y_mm: float


def _draw_guides(
    c: canvas.Canvas,
    width_pt: float,
    height_pt: float,
    trim_width_pt: float,
    trim_height_pt: float,
    bleed_pt: float,
    spine_pt: float,
    safe_pt: float,
    barcode: dict[str, float],
) -> None:
    c.setStrokeColor(colors.red)
    c.setLineWidth(0.5)
    # Trim guides
    c.rect(bleed_pt, bleed_pt, trim_width_pt, trim_height_pt)
    c.rect(width_pt - bleed_pt - trim_width_pt, bleed_pt, trim_width_pt, trim_height_pt)
    # Bleed area
    c.setStrokeColor(colors.blue)
    c.rect(0, 0, width_pt, height_pt)
    # Safe area
    c.setStrokeColor(colors.green)
    c.rect(bleed_pt + safe_pt, bleed_pt + safe_pt, trim_width_pt - 2 * safe_pt, trim_height_pt - 2 * safe_pt)
    c.rect(
        width_pt - bleed_pt - trim_width_pt + safe_pt,
        bleed_pt + safe_pt,
        trim_width_pt - 2 * safe_pt,
        trim_height_pt - 2 * safe_pt,
    )
    # Spine guides
    spine_left = bleed_pt + trim_width_pt
    c.setStrokeColor(colors.purple)
    c.line(spine_left, bleed_pt, spine_left, height_pt - bleed_pt)
    c.line(spine_left + spine_pt, bleed_pt, spine_left + spine_pt, height_pt - bleed_pt)
    # Barcode safe zone
    c.setStrokeColor(colors.orange)
    c.rect(barcode["x"], barcode["y"], barcode["width"], barcode["height"], fill=0)


def generate_cover_template(output_path: Path, request: CoverTemplateRequest) -> Path:
    trim_width_pt = request.trim_width_mm * MM_TO_PT
    trim_height_pt = request.trim_height_mm * MM_TO_PT
    bleed_pt = request.bleed_mm * MM_TO_PT
    spine_pt = request.spine_mm * MM_TO_PT
    safe_pt = request.safe_mm * MM_TO_PT

    width_pt = trim_width_pt * 2 + spine_pt + 2 * bleed_pt
    height_pt = trim_height_pt + 2 * bleed_pt

    barcode = {
        "width": request.barcode_width_mm * MM_TO_PT,
        "height": request.barcode_height_mm * MM_TO_PT,
        "x": bleed_pt + request.barcode_offset_x_mm * MM_TO_PT,
        "y": bleed_pt + request.barcode_offset_y_mm * MM_TO_PT,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=(width_pt, height_pt))
    _draw_guides(c, width_pt, height_pt, trim_width_pt, trim_height_pt, bleed_pt, spine_pt, safe_pt, barcode)
    c.showPage()
    c.save()
    return output_path
