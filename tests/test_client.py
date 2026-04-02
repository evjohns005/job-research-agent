"""Tests for client helpers (no flow / LLM)."""

from client import format_shared


def test_format_shared_extracts_expected_fields():
    shared = {
        "job_summary": {
            "company_name": "Acme Corp",
            "job_title": "Widget Engineer",
            "job_description": "Build widgets.",
        },
        "brief": "Strong fit for backend work.",
    }
    out = format_shared(shared)
    assert out == {
        "company_name": "Acme Corp",
        "job_title": "Widget Engineer",
        "job_description": "Build widgets.",
        "brief": "Strong fit for backend work.",
    }
