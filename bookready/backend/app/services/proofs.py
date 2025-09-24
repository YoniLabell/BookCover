from __future__ import annotations

import base64
import io
import subprocess
from pathlib import Path
from typing import List

from PIL import Image

from ..core.config import get_settings


class ProofService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _render_pdf(self, pdf_path: Path, output_dir: Path, single_page: bool = False) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_template = output_dir / "page"
        args = [
            "pdftoppm",
            "-png",
            str(pdf_path),
            str(output_template),
        ]
        try:
            subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as exc:
            raise RuntimeError("pdftoppm binary not installed") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(exc.stderr.decode("utf-8", errors="ignore")) from exc
        images = sorted(output_dir.glob("page-*.png"))
        if single_page and images:
            return [images[0]]
        return images

    def proof_content(self, pdf_path: Path) -> List[str]:
        output_dir = self.settings.media_root / "proofs" / pdf_path.stem
        images = self._render_pdf(pdf_path, output_dir, single_page=False)
        return [self._encode_image(image) for image in images]

    def proof_cover(self, pdf_path: Path) -> str:
        output_dir = self.settings.media_root / "proofs" / (pdf_path.stem + "_cover")
        images = self._render_pdf(pdf_path, output_dir, single_page=True)
        if not images:
            raise RuntimeError("Failed to render cover preview")
        return self._encode_image(images[0])

    @staticmethod
    def _encode_image(path: Path) -> str:
        with Image.open(path) as img:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")


def get_proof_service() -> ProofService:
    return ProofService()
