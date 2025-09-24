import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / 'app'))
from services.validators import page_size_mm

PT_PER_MM = 72 / 25.4


def make_pdf(path, width_pt, height_pt):
    content = b"BT /F1 12 Tf 72 720 Td (Hello) Tj ET"
    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    page = f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 {width_pt} {height_pt}] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n".encode()
    objects.append(page)
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica /FontDescriptor 6 0 R >> endobj\n")
    stream = f"5 0 obj << /Length {len(content)} >> stream\n".encode() + content + b"\nendstream endobj\n"
    objects.append(stream)
    objects.append(b"6 0 obj << /Type /FontDescriptor >> endobj\n")
    xref_positions = []
    offset = len(b"%PDF-1.4\n")
    for obj in objects:
        xref_positions.append(offset)
        offset += len(obj)
    xref_start = offset
    xref = [b"xref\n0 7\n0000000000 65535 f \n"]
    for pos in xref_positions:
        xref.append(f"{pos:010d} 00000 n \n".encode())
    trailer = b"trailer << /Size 7 /Root 1 0 R >>\nstartxref\n" + str(xref_start).encode() + b"\n%%EOF"
    with open(path, "wb") as f:
        f.write(b"%PDF-1.4\n")
        for obj in objects:
            f.write(obj)
        f.write(b"".join(xref))
        f.write(trailer)


def test_page_size(tmp_path):
    pdf = tmp_path / "test.pdf"
    width_mm = 148 + 6.4
    height_mm = 210 + 6.4
    make_pdf(pdf, width_mm * PT_PER_MM, height_mm * PT_PER_MM)
    w, h = page_size_mm(str(pdf))
    assert abs(w - width_mm) < 0.1
    assert abs(h - height_mm) < 0.1
