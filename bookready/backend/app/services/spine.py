from __future__ import annotations

import json
from math import ceil
from pathlib import Path
from typing import Dict

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "paper_thickness.json"


class SpineCalculator:
    def __init__(self, table: Dict[str, float]):
        self.table = table

    @classmethod
    def from_file(cls, path: Path) -> "SpineCalculator":
        data = json.loads(path.read_text())
        return cls({k: float(v) for k, v in data.items()})

    def calculate(self, pages: int, paper_type: str) -> float:
        if pages <= 0:
            raise ValueError("Pages must be positive")
        try:
            thickness = self.table[paper_type]
        except KeyError as exc:
            raise ValueError(f"Unknown paper type: {paper_type}") from exc
        sheets = ceil(pages / 2)
        return round(sheets * thickness, 3)

    def list_paper_types(self) -> Dict[str, float]:
        return dict(self.table)


def calculate_spine(pages: int, paper_type: str) -> float:
    calculator = SpineCalculator.from_file(DATA_PATH)
    return calculator.calculate(pages, paper_type)
