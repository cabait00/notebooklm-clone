import fitz
import pytest

from app.services.extraction import extract_text


def test_extract_txt(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Hello from a text file.", encoding="utf-8")
    assert extract_text(f, "txt") == "Hello from a text file."


def test_extract_md(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("# Heading\n\nSome markdown content.", encoding="utf-8")
    result = extract_text(f, "md")
    assert "Heading" in result
    assert "markdown content" in result


def test_extract_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello from a PDF file.")
    doc.save(str(pdf_path))
    doc.close()

    result = extract_text(pdf_path, "pdf")
    assert "Hello from a PDF file." in result


def test_extract_unsupported_type_raises(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("col1,col2\n1,2", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(f, "csv")
