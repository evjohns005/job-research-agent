"""Tests for FastAPI app behavior (upload validation, happy path with mocks)."""

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app, _is_pdf


class _FakeUpload:
    def __init__(self, filename: str | None, content_type: str | None):
        self.filename = filename
        self.content_type = content_type


@pytest.mark.parametrize(
    "filename,content_type,expected",
    [
        ("cv.pdf", "application/pdf", True),
        ("CV.PDF", None, True),
        ("notes.txt", "text/plain", False),
        ("notes.pdf", "text/plain", True),
    ],
)
def test_is_pdf(filename, content_type, expected):
    upload = _FakeUpload(filename, content_type)
    assert _is_pdf(upload) is expected


def test_job_research_rejects_non_pdf_resume():
    client = TestClient(app)
    files = {
        "resume_file": ("resume.txt", BytesIO(b"hello"), "text/plain"),
        "job_posting": ("job.pdf", BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    response = client.post("/job-research", files=files)
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@patch("app.run_flow")
def test_job_research_success_returns_flow_payload_with_filenames(mock_run_flow):
    mock_run_flow.return_value = {
        "company_name": "Acme",
        "job_title": "Engineer",
        "job_description": "Do work.",
        "brief": "Summary.",
    }
    client = TestClient(app)
    files = {
        "resume_file": ("my_resume.pdf", BytesIO(b"%PDF-1.4\n"), "application/pdf"),
        "job_posting": ("posting.pdf", BytesIO(b"%PDF-1.4\n"), "application/pdf"),
    }
    response = client.post("/job-research", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["company_name"] == "Acme"
    assert body["resume_file"] == "my_resume.pdf"
    assert body["job_posting"] == "posting.pdf"
    mock_run_flow.assert_called_once()
