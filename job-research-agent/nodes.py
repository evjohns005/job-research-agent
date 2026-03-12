from pocketflow import Node

class ParseJobNode(Node):
    def exec(self, _):
        # receive job text from shared store
        # returns structured summary of role/requirements
        pass
    
    def post(self, shared, prep_res, exec_res):
        shared['job_summary'] = exec_res
        return "default"


class ResearchNode(Node):
    def prep(self, shared):
        return shared['job_summary'], shared['research']

    def exec(self, inputs):
        # call LLM to research company + role fit
        # returns research notes
        pass
    
    def post(self, shared, prep_res, exec_res):
        shared['research'] = exec_res
        return "default"


class SynthesisNode(Node):
    def prep(self, shared):
        return shared['job_summary'], shared['research']

    def exec(self, inputs):
        # call LLM to generate:
        # 1. fit summary
        # 2. talking points
        # 3. question to ask
        # returns synthesis notes
        pass
    
    def post(self, shared, prep_res, exec_res):
        shared['brief'] = exec_res
        return "default"
        
        
        