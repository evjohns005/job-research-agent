"""Tests for PDF / file text extraction helpers."""

import os
import tempfile

from pypdf import PdfWriter

from utils.pdf_utils import _effective_max_pages, extract_text_from_pdf, parse_pdf_to_text


def test_effective_max_pages_explicit_positive():
    assert _effective_max_pages(5) == 5


def test_effective_max_pages_zero_means_no_limit():
    assert _effective_max_pages(0) is None


def test_effective_max_pages_negative_means_no_limit():
    assert _effective_max_pages(-1) is None


def test_extract_text_from_pdf_respects_max_pages(tmp_path):
    pdf_path = tmp_path / "two_pages.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)

    # Blank pages yield empty strings; we only assert the call completes and
    # max_pages=1 does not raise (limits iteration to the first page).
    text = extract_text_from_pdf(str(pdf_path), max_pages=1)
    assert isinstance(text, str)


def test_parse_pdf_to_text_reads_plain_text_file():
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write("Hello job posting")
        path = f.name
    try:
        assert parse_pdf_to_text(path) == "Hello job posting"
    finally:
        os.unlink(path)
