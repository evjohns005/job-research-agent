import json

from pocketflow import Node

from utils.call_llm import call_llm, parse_llm_json
from utils.pdf_utils import parse_pdf_to_text

class ParseJobNode(Node):
    def prep(self, shared):
        return shared['job_posting'], shared['resume_file']

    def exec(self, inputs):
        job_posting_path, resume_file = inputs
        job_posting_text = parse_pdf_to_text(job_posting_path)
        resume_text = parse_pdf_to_text(resume_file)

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

        job_summary = parse_llm_json(job_parsing_prompt)
        
        return job_summary, resume_text


    def post(self, shared, prep_res, exec_res):
        shared['job_summary'] = exec_res[0]
        shared['resume_text'] = exec_res[1]
        return "default"


class ResearchNode(Node):
    def prep(self, shared):
        return shared['job_summary'], shared['resume_text']

    def exec(self, inputs):
        job_summary, resume_text = inputs

        research_prompt = f"""
You are a helpful assistant that researches companies and roles.
You will be given a company name and a job title and you will need to research the company and the role.
The company name is {job_summary['company_name']} and the job title is {job_summary['job_title']}.
Job description: {job_summary['job_description']}
Job requirements: {job_summary['job_requirements']}
The research should be based on the job posting and the company information.

Provided resume: {resume_text}

The output should be a JSON object with the following keys:
- is_good_fit: boolean
- fit_score: a score from 1-10
- matched_skills: list of skills from the resume that match the job
- missing_skills: list of required skills not found in the resume
- summary: brief explanation of the fit assessment

Given the job posting and the resume, determine if the candidate is a good fit for the role.
Return only a valid JSON object.
"""
        research_summary = parse_llm_json(research_prompt)
        return research_summary

    
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
- questions_to_ask: a list of questions to ask the interviewer

Return only a valid JSON object.
"""
        synthesis_summary = parse_llm_json(synthesis_prompt)
        return synthesis_summary

    def post(self, shared, prep_res, exec_res):
        shared['brief'] = exec_res
        return "default"
        
        
        