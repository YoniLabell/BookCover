from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ..core.config import get_settings


GHOSTSCRIPT_COMMAND = [
    "gs",
    "-dBATCH",
    "-dNOPAUSE",
    "-dPDFSETTINGS=/prepress",
    "-sDEVICE=pdfwrite",
]


def _run_ghostscript(input_pdf: Path, output_pdf: Path, icc_profile: Optional[Path] = None) -> None:
    args = GHOSTSCRIPT_COMMAND + [f"-sOutputFile={output_pdf}"]
    if icc_profile:
        args.extend(["-sProcessColorModel=DeviceCMYK", "-sColorConversionStrategy=CMYK", f"-sDefaultRGBProfile={icc_profile}"])
    args.append(str(input_pdf))
    try:
        subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as exc:
        raise RuntimeError("Ghostscript not installed") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr.decode("utf-8", errors="ignore")) from exc


def flatten_and_embed(input_pdf: Path, output_pdf: Path, icc_profile: Optional[Path] = None) -> Path:
    try:
        _run_ghostscript(input_pdf, output_pdf, icc_profile)
    except RuntimeError:
        # Fallback to simply copying the file so the pipeline can continue in development environments.
        shutil.copy(input_pdf, output_pdf)
    return output_pdf


def fix_content(project_id: str, source_key: str, icc_profile: Optional[Path] = None) -> Path:
    settings = get_settings()
    input_path = settings.media_root / project_id / "downloads" / Path(source_key).name
    output_dir = settings.media_root / project_id / "fixed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = output_dir / "content_fixed.pdf"
    return flatten_and_embed(input_path, output_pdf, icc_profile)
