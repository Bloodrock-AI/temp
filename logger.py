class Logger:
    def __init__(self, name):
        self.mistake_counters = {
            "type_1": 0,
            "type_2": 0,
            "type_3": 0,
            "function_hallucination": 0,
            "parameter_hallucination": 0,
            "generated_tokens": 0,
        }
    
    def reset(self):
        self.mistake_counters = {
            "type_1": 0,
            "type_2": 0,
            "type_3": 0,
            "function_hallucination": 0,
            "parameter_hallucination": 0,
            "generated_tokens": 0,
        }
        
# singleton instance
logger = Logger("baseline_agent_logger")