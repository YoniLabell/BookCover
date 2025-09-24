import sys, pathlib
base = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(base / 'app'))
sys.path.append(str(base / 'tests'))
from services.validators import fonts_embedded
from test_page_size import make_pdf, PT_PER_MM


def test_fonts_not_embedded(tmp_path):
    pdf = tmp_path / 'fonts.pdf'
    make_pdf(pdf, 100 * PT_PER_MM, 100 * PT_PER_MM)
    assert fonts_embedded(str(pdf)) is False
