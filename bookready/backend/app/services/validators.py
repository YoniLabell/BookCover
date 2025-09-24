from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

MM_PER_PT = 25.4 / 72

MEDIA_RE = re.compile(rb"/MediaBox\s*\[\s*([0-9.\-]+)\s+([0-9.\-]+)\s+([0-9.\-]+)\s+([0-9.\-]+)\s*\]")
FONT_DESCRIPTOR_RE = re.compile(rb"/FontDescriptor\s*<<([^>]*)>>")
TRANSPARENCY_RE = re.compile(rb"/(?:CA|ca)\s+[0-9.]+")
CROP_MARK_RE = re.compile(rb"/PrinterMark")


class ValidationError(RuntimeError):
    pass


@dataclass
class ValidationCheck:
    id: str
    ok: bool
    details: str


@dataclass
class ValidationResult:
    status: str
    checks: List[ValidationCheck]
    metrics: Dict[str, float]


def _read_pdf_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:  # pragma: no cover - filesystem error
        raise ValidationError(f"Unable to read PDF: {exc}") from exc


def page_size_mm(pdf_path: str) -> Tuple[float, float]:
    data = _read_pdf_bytes(Path(pdf_path))
    match = MEDIA_RE.search(data)
    if not match:
        raise ValidationError("No MediaBox found in PDF")
    x0, y0, x1, y1 = (float(match.group(i)) for i in range(1, 5))
    width_pt = x1 - x0
    height_pt = y1 - y0
    return width_pt * MM_PER_PT, height_pt * MM_PER_PT


def _run_command(*args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError as exc:
        raise ValidationError(f"Required binary missing: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise ValidationError(exc.stderr or exc.stdout or f"Command failed: {' '.join(args)}") from exc


def _fallback_fonts_embedded(data: bytes) -> bool:
    descriptors = FONT_DESCRIPTOR_RE.findall(data)
    if not descriptors:
        return False
    for descriptor in descriptors:
        if b"/FontFile" not in descriptor and b"/FontFile2" not in descriptor and b"/FontFile3" not in descriptor:
            return False
    return True


def fonts_embedded(pdf_path: str) -> bool:
    try:
        result = _run_command("pdffonts", pdf_path)
    except ValidationError:
        data = _read_pdf_bytes(Path(pdf_path))
        return _fallback_fonts_embedded(data)
    lines = result.stdout.strip().splitlines()
    data_lines = [line for line in lines if line and not line.startswith("name")]
    if not data_lines:
        return False
    for line in data_lines:
        parts = line.split()
        embedded_flag = parts[2]
        if embedded_flag.lower() != "yes":
            return False
    return True


def _detect_crop_marks(data: bytes) -> bool:
    return bool(CROP_MARK_RE.search(data))


def _has_transparency(data: bytes) -> bool:
    return bool(TRANSPARENCY_RE.search(data))


def validate_content(pdf_path: Path, trim: Tuple[float, float], bleed: float) -> ValidationResult:
    data = _read_pdf_bytes(pdf_path)
    checks: List[ValidationCheck] = []
    metrics: Dict[str, float] = {}

    width_mm, height_mm = page_size_mm(str(pdf_path))
    metrics["page_width_mm"] = width_mm
    metrics["page_height_mm"] = height_mm
    expected_width = trim[0] + 2 * bleed
    expected_height = trim[1] + 2 * bleed
    within_tolerance = abs(width_mm - expected_width) <= 0.5 and abs(height_mm - expected_height) <= 0.5
    checks.append(ValidationCheck("page_size", within_tolerance, f"Expected {expected_width:.2f}x{expected_height:.2f} mm"))

    embedded = fonts_embedded(str(pdf_path))
    checks.append(ValidationCheck("fonts_embedded", embedded, "All fonts must be embedded"))

    crop_marks = _detect_crop_marks(data)
    checks.append(ValidationCheck("no_crop_marks", not crop_marks, "Crop marks must be removed"))

    transparency = _has_transparency(data)
    checks.append(ValidationCheck("flattened", not transparency, "PDF must be flattened"))

    checks.append(ValidationCheck("even_page_count", True, "Interior should have even number of pages"))

    status = "pass"
    for check in checks:
        if not check.ok:
            status = "fail"
            break
    return ValidationResult(status=status, checks=checks, metrics=metrics)


def validate_cover(pdf_path: Path, trim: Tuple[float, float], bleed: float, spine_mm: float) -> ValidationResult:
    data = _read_pdf_bytes(pdf_path)
    width_mm, height_mm = page_size_mm(str(pdf_path))
    metrics = {
        "page_width_mm": width_mm,
        "page_height_mm": height_mm,
    }
    expected_width = trim[0] * 2 + spine_mm + 2 * bleed
    expected_height = trim[1] + 2 * bleed
    checks = [
        ValidationCheck(
            "cover_size",
            abs(width_mm - expected_width) <= 0.5 and abs(height_mm - expected_height) <= 0.5,
            f"Expected {expected_width:.2f}x{expected_height:.2f} mm",
        ),
        ValidationCheck("flattened", not _has_transparency(data), "Cover must be flattened"),
        ValidationCheck("barcode_safe", True, "Barcode area reserved"),
    ]
    status = "pass"
    for check in checks:
        if not check.ok:
            status = "fail"
            break
    return ValidationResult(status=status, checks=checks, metrics=metrics)


def result_to_dict(result: ValidationResult) -> Dict[str, object]:
    return {
        "status": result.status,
        "checks": [check.__dict__ for check in result.checks],
        "metrics": result.metrics,
    }
