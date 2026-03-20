from pocketflow import Flow
from nodes import ParseJobNode, ResearchNode, SynthesisNode

def build_job_research_flow():
    """
    Create and configure the job research workflow
    """
    # Create node instances
    parse = ParseJobNode()
    research = ResearchNode()
    synthesis = SynthesisNode()

    # Connect nodes in sequences
    parse >> research >> synthesis

    job_research_flow = Flow(start=parse)

    return job_research_flow