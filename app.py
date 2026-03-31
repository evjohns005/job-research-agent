import argparse
import os
import sys
import tempfile
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

_MODULE_DIR = os.path.join(os.path.dirname(__file__), "job-research-agent")
if _MODULE_DIR not in sys.path:
    sys.path.insert(0, _MODULE_DIR)

from client import run_flow  # noqa: E402


app = FastAPI(title="Job Research Agent")


def _is_pdf(upload: UploadFile) -> bool:
    content_type_ok = upload.content_type == "application/pdf"
    filename_ok = (upload.filename or "").lower().endswith(".pdf")
    return content_type_ok or filename_ok


async def _save_upload_to_temp_pdf(upload: UploadFile) -> str:
    # Nodes expect file paths, so we persist uploads to a temp PDF on disk.
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp.write(await upload.read())
    finally:
        tmp.close()
    return tmp.name


@app.post("/job-research")
async def run_research_job(
    resume_file: UploadFile = File(...),
    job_posting: UploadFile = File(...),
) -> Dict[str, Any]:
    if not _is_pdf(resume_file) or not _is_pdf(job_posting):
        raise HTTPException(status_code=400, detail="Both files must be PDFs.")

    tmp_resume: Optional[str] = None
    tmp_job_posting: Optional[str] = None

    try:
        tmp_resume = await _save_upload_to_temp_pdf(resume_file)
        tmp_job_posting = await _save_upload_to_temp_pdf(job_posting)

        # PocketFlow + LLM calls are blocking; run in a worker thread.
        shared = await run_in_threadpool(run_flow, tmp_resume, tmp_job_posting)
        # `run_flow()` uses temp file paths; return the original upload names instead.
        shared["resume_file"] = resume_file.filename
        shared["job_posting"] = job_posting.filename
        return shared
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    finally:
        for p in (tmp_resume, tmp_job_posting):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
