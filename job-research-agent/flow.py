from pocketflow import Flow
from nodes import ParseJobNode, ResearchNode, SynthesisNode

def build_flow():
    parse = ParseJobNode()
    research = ResearchNode()
    synthesis = SynthesisNode()

    parse >> research >> synthesis

    return Flow(start=parse)