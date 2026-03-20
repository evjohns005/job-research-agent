import json

from pocketflow import Node
from pypdf import PdfReader

from utils.call_llm import call_llm

class ParseJobNode(Node):
    def prep(self, shared):
        return shared['job_posting']

    def parse_job_posting(self, job_posting):
        if job_posting.endswith(".pdf"):
            try:
                job_posting_text_parts: list[str] = []
                with open(job_posting, "rb") as file:
                    reader = PdfReader(file)

                    for page in reader.pages:
                        page_text = page.extract_text() or ""
                        job_posting_text_parts.append(page_text)

                return "".join(job_posting_text_parts)
            except Exception as e:
                print(f"Error: Unable to parse the job_posting provided: {e}")
                raise
        else:
            with open(job_posting, 'r') as file:
                job_posting = file.read()

            return job_posting

    def exec(self, inputs):
        job_parsing_prompt = f"""
        You are a helpful assistant that parses job postings.
        You will be given a job posting and you will need to parse it into a structured format.

        The job posting is: {self.parse_job_posting(inputs)}

        The output should be a JSON object with the following keys:
        - company_name: the name of the company
        - job_title: the title of the job
        - job_description: a brief description of the job
        - job_requirements: the requirements for the job
        - job_responsibilities: the responsibilities for the job

        Do not make up any information, only use the information provided in the job posting.
        Return only a valid JSON object.
        """
        try:
            job_posting_text = self.parse_job_posting(inputs)
            if not job_posting_text or not job_posting_text.strip():
                raise ValueError(
                    "No extractable text found in `job_posting.pdf` (pypdf returned empty text for all pages). "
                    "This PDF is likely scanned/image-only. Please provide a text-based PDF or add an OCR step "
                    "(e.g., Tesseract) before parsing."
                )

            # Embed the extracted text into the prompt after validation.
            job_parsing_prompt = f"""
        You are a helpful assistant that parses job postings.
        You will be given a job posting and you will need to parse it into a structured format.

        The job posting is: {job_posting_text}

        The output should be a JSON object with the following keys:
        - company_name: the name of the company
        - job_title: the title of the job
        - job_description: a brief description of the job
        - job_requirements: the requirements for the job
        - job_responsibilities: the responsibilities for the job

        Do not make up any information, only use the information provided in the job posting.
        Return only a valid JSON object.
        """

            job_summary = json.loads(call_llm(job_parsing_prompt))
            
            return job_summary
        except json.JSONDecodeError:
            print("Error: decoding the json file due to an improper format")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    def post(self, shared, prep_res, exec_res):
        shared['job_summary'] = exec_res
        return "default"


class ResearchNode(Node):
    def prep(self, shared):
        return shared['job_summary'], shared['resume_file']

    def parse_resume(self, resume_file):
        try:
            resume_text_parts: list[str] = []
            with open(resume_file, "rb") as file:
                reader = PdfReader(file)

                for page in reader.pages:
                    resume_text_parts.append(page.extract_text() or "")
            
            return "".join(resume_text_parts)
        except Exception as e:
            print(f"Error: Unable to parse the resume provided: {e}")
            raise


    def exec(self, inputs):
        job_summary, resume_file = inputs

        research_prompt = f"""
        You are a helpful assistant that researches companies and roles.
        You will be given a company name and a job title and you will need to research the company and the role.
        The company name is {job_summary['company_name']} and the job title is {job_summary['job_title']}.
        The research should be based on the job posting and the company information.

        Provided resume: {self.parse_resume(resume_file)}
        Given the job posting and the resume, determine if the candidate is a good fit for the role.
        Return only a valid JSON object.
        """
        try:
            research_summary = json.loads(call_llm(research_prompt))
            return research_summary
        except json.JSONDecodeError:
            print(f"Error decoding the json file due to an improper format")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    
    def post(self, shared, prep_res, exec_res):
        shared['research'] = exec_res
        return "default"


class SynthesisNode(Node):
    def prep(self, shared):
        return shared['job_summary'], shared['research']

    def exec(self, inputs):
        job_summary, research = inputs
        synthesis_prompt = f"""
        You are a helpful assistant that synthesizes research.
        You will be given a job summary and a research summary and you will need to synthesize the research into a fit summary and a talking points.
        The job summary is {job_summary} and the research summary is {research}.
        The synthesis should be based on the job summary and the research summary.
        The synthesis should be in a structured format.

        The output should be a JSON object with the following keys:
        - fit_summary: a summary of the fit of the candidate for the role
        - key_strengths: a list of the candidate's key strengths
        - areas_for_improvement: a list of the candidate's areas for improvement
        - talking_points: a list of talking points to use in the interview
        - questions_to_ask: a list of questions to ask the candidate

        Return only a valid JSON object.
        """
        try:
            synthesis_summary = json.loads(call_llm(synthesis_prompt))
            return synthesis_summary
        except json.JSONDecodeError:
            print(f"Error decoding the json file due to an improper format")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def post(self, shared, prep_res, exec_res):
        shared['brief'] = exec_res
        return "default"
        
        
        