# Job Research Agent

A multi-agent system built with PocketFlow and LLM that analyzes job posting and generates tailored research briefs.

## Architecture:
`ParseJobNode -> ResearchNode -> SynthesisNode` </br>
Shared store passes context between nodes.

## Why PocketFlow?
Minimal 100-line frame work - no abstraction overhead, full visibility into agent execution flow.

## Interfaces
- **CLI**: `python app.py <resume.pdf> <job_posting.pdf|job_posting.txt>`
- **API**: FastAPI app with `POST /job-research` (multipart upload)

## OCR behavior (scanned PDFs)
This project first attempts to extract text from PDFs using `pypdf`. If **no extractable text** is found (common with scanned/image-only PDFs), it falls back to **OCR**:

- **Decision**: prefer a robust OCR approach by using **OCRmyPDF** to generate a temporary *searchable PDF*, then re-extract text from that output.
- **Where**: implemented in `job-research-agent/nodes.py` for both job postings and resumes.
- **Notes**:
  - OCR can be slow on multi-page/high-DPI PDFs.
  - OCR requires **system dependencies** (below). Installing `ocrmypdf` via Poetry does not install these OS-level tools.

## Dependencies
### Python dependencies (installed via Poetry)
```bash
poetry install
```

### System dependencies (required for OCR)
OCR is optional at runtime, but **required** for scanned/image-only PDFs.

- **Tesseract OCR** (required): `tesseract.exe` must be installed and available on PATH
- **Ghostscript** (usually required by OCRmyPDF): `gswin64c.exe` (64-bit) must be installed and available on PATH

PowerShell checks:
```powershell
where.exe tesseract
tesseract --version

where.exe gswin64c
gswin64c --version
```

Optional (improves output size/optimization; not required):
- **jbig2**: enables JBIG2 compression optimization
- **pngquant**: enables PNG optimization

## How to run
### CLI
```bash
poetry install
poetry run python app.py path/to/resume.pdf path/to/job_posting.pdf
```

### FastAPI
```bash
poetry run uvicorn app:app --reload
```

`POST /job-research` (multipart form):
```bash
curl -X POST "http://127.0.0.1:8000/job-research" `
  -F "resume_file=@path/to/resume.pdf;type=application/pdf" `
  -F "job_posting=@path/to/job_posting.pdf;type=application/pdf"
```

### Troubleshooting
- **`/docs` not reachable**: if the server prints `http://0.0.0.0:8080`, open `http://127.0.0.1:8080/docs` (or `http://localhost:8080/docs`) in your browser.
- **`tesseract not found on PATH`**: install Tesseract and reopen your terminal (PATH updates require a new shell).
- **Ghostscript warnings**: OCRmyPDF may warn about certain Ghostscript versions; upgrading Ghostscript can help.