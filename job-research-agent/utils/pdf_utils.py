from ocrmypdf import ocr
from pypdf import PdfReader
import os
import tempfile

_DEFAULT_MAX_PAGES = int(os.getenv("JOB_RESEARCH_MAX_PAGES", "3"))
_OCR_JOBS = int(
    os.getenv(
        "JOB_RESEARCH_OCR_JOBS",
        str(min(4, os.cpu_count() or 2)),
    )
)


def _effective_max_pages(max_pages: int | None) -> int | None:
    """
    Use the caller-provided value, otherwise fall back to the env/default.

    Set JOB_RESEARCH_MAX_PAGES=0 to disable page limiting.
    """
    if max_pages is None:
        max_pages = _DEFAULT_MAX_PAGES
    if max_pages is None or max_pages <= 0:
        return None
    return max_pages


def extract_text_from_pdf(pdf_path: str, max_pages: int | None = None) -> str:
    text_parts: list[str] = []
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        max_pages = _effective_max_pages(max_pages)
        for i, page in enumerate(reader.pages):
            if max_pages is not None and i >= max_pages:
                break
            text_parts.append(page.extract_text() or "")
    return "".join(text_parts)


def ocr_pdf_to_searchable_pdf(input_pdf_path: str, pages: str | None = None) -> str:
    """
    Run OCR on a PDF and return the path to the OCR'd PDF.

    Uses OCRmyPDF (which typically requires external dependencies like Tesseract and Ghostscript).
    """
    fd, output_pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        # Force OCR so even "empty text layer" PDFs get processed.
        ocr(
            input_pdf_path,
            output_pdf_path,
            language=["eng"],
            pages=pages,
            # Cap parallelism to avoid oversubscribing CPU on Windows.
            jobs=_OCR_JOBS,
            progress_bar=False,
            # Speed-oriented settings:
            # - skip_text avoids re-OCR'ing pages that already have text layers.
            # - optimize=0 reduces extra file-size post-processing.
            skip_text=True,
            optimize=0,
            output_type="pdf",
        )
    except Exception:
        # If OCR fails, cleanup the output file and re-raise.
        try:
            if os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)
        except OSError:
            pass
        raise
    return output_pdf_path


def parse_pdf_to_text(file_path: str, max_pages: int | None = None) -> str:
    if file_path.lower().endswith(".pdf"):
        try:
            max_pages = _effective_max_pages(max_pages)
            extracted = extract_text_from_pdf(file_path, max_pages=max_pages)
            if extracted and extracted.strip():
                return extracted
            
            print("Warning: No extractable text found in pdf; attempting OCR.")
            pages_arg = f"1-{max_pages}" if max_pages is not None else None
            ocr_pdf_path = ocr_pdf_to_searchable_pdf(file_path, pages=pages_arg)
            try:
                extracted_after_ocr = extract_text_from_pdf(ocr_pdf_path, max_pages=max_pages)
                return extracted_after_ocr
            finally:
                try:
                    if os.path.exists(ocr_pdf_path):
                        os.remove(ocr_pdf_path)
                except OSError:
                    pass
        except Exception as e:
            print(f"Error: Unable to parse the pdf provided: {e}")
            raise
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
