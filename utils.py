import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria

from const import ModelType

class StopOnString(StoppingCriteria):
    def __init__(self, stop_string_ids):
        self.stop_string_ids = stop_string_ids

    def __call__(self, input_ids, scores, **kwargs):
        # Flatten the generated token IDs from the first batch (assumes batch size 1)
        generated_ids = input_ids[0].tolist()
        
        # If the generated output is shorter than the stop string, keep generating
        if len(generated_ids) < len(self.stop_string_ids):
            return False
        
        # Check if the ending tokens match the stop string sequence
        
        # debug
        # print(f'comparing {generated_ids[-len(self.stop_string_ids):]} with {self.stop_string_ids}')
        
        if generated_ids[-len(self.stop_string_ids):] == self.stop_string_ids:
            return True
        return False


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_model_tools(model: ModelType):
    model = model.value
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model,
        torch_dtype=torch.float16,
        device_map=get_device(),
        trust_remote_code=True,
    ).to(get_device())
    
    return model, tokenizer
    
if __name__ == '__main__':
    print(type(get_model(ModelType.DEEPSCALE_R)))