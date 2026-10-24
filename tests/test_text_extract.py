from pathlib import Path

import pytest

from utils.text_extract import extract_text

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"


def test_docx_extraction():
    f = SAMPLES / "aarav_sharma.docx"
    text = extract_text(f.name, f.read_bytes())
    assert "Aarav Sharma" in text
    assert "PostgreSQL" in text


def test_unsupported_type_raises():
    with pytest.raises(ValueError):
        extract_text("resume.txt", b"hello")


def test_pdf_extraction():
    fitz = pytest.importorskip("fitz")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Jane Doe Python Developer")
    data = doc.tobytes()
    assert "Jane Doe" in extract_text("jane.pdf", data)
