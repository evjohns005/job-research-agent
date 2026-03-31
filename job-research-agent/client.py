import os

from flow import build_job_research_flow


def run_flow(resume_file: str, job_posting: str) -> dict:
    """
    Run the job research workflow.

    Required:
    - resume_file: Candidate's resume (PDF or text file)
    - job_posting: PDF (or text file) of the job posting
    """
    if not os.path.isfile(resume_file):
        raise FileNotFoundError(f"Resume file not found: {resume_file}")
    if not os.path.isfile(job_posting):
        raise FileNotFoundError(f"Job posting file not found: {job_posting}")

    # Initialize shared data
    shared = {"resume_file": resume_file, "job_posting": job_posting}
    print("\n=== Starting Resume Review Workflow ===")
    print(f"Resume: {resume_file}")
    print(f"Job posting: {job_posting}")

    # Run the flow
    flow = build_job_research_flow()
    flow.run(shared)

    print("\n=== Workflow Completed ===\n")
    return shared

