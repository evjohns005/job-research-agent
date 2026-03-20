import argparse
import os

from flow import build_job_research_flow
from config import job_posting, resume_file


def run_flow(resume_file: str, job_posting: str) -> dict:
    """
    Run the job research workflow.

    Required:
    - resume_file: Candidate's resume (PDF)
    - job_posting: PDF of the job posting
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the job research workflow for a resume + job posting PDFs."
    )
    parser.add_argument("resume_file", help="Candidate resume PDF path")
    parser.add_argument("job_posting", help="Job posting PDF path")
    args = parser.parse_args()

    try:
        shared = run_flow(args.resume_file, args.job_posting)
    except PermissionError as e:
        print(f"Error: Permission denied. {e}")
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    # Print a lightweight result preview if present.
    brief = shared.get("brief")
    if brief is not None:
        print("=== Output Preview ===")
        print(brief)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
