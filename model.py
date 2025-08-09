import re
import json
from llm_tool import tool

from const import (
    ModelType,
)
from utils import (
    get_device,
    get_model_tools,
)

from typing import Optional

class Model:
    '''
    Wraps a model from hugging face.
    '''
    
    def __init__(
        self,
        model: ModelType,
        # config
        max_output_length: int = 1000,
        num_beams=1,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    ):
        self._model, self.tokenizer = get_model_tools(model)
        
        self.config = {
            "max_length": max_output_length,
            "num_beams": num_beams,
            "do_sample": do_sample,
            "temperature": temperature,
            "top_p": top_p,
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        
        self.last_generated_tokens: Optional[int] = None
    
    def prompt(self, prompt: str) -> str:
        
        # tokenize input
        input_tensors = self.tokenizer(prompt, return_tensors="pt").to(get_device())
        prompt_len = input_tensors["input_ids"].shape[-1]
        
        output_tokens = self._model.generate(
            **input_tensors,
            **self.config,
        )
        
        # measure output tokens
        self.last_generated_tokens = output_tokens.shape[-1] - prompt_len
        
        # decode output
        output = self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        output = output[0, input_tensors.shape[-1]:]
        print(f"Output: {output}")
        
        return output

    def prompt_v2(self, messages: List[Dict[str, str]]) -> str:
        input_tensors = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self._model.device)
        prompt_len = input_tensors["input_ids"].shape[-1]

        with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id,
        )

        # Strip the prompt portion and decode only the newly generated tokens
        gen_tokens = outputs[0, input_tensors.shape[-1]:]
        output = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()
        return output


@tool()
def get_weather(city: str) -> int:
    '''
    Get the weather of a city.
    
    :param city: the city to get the weather from
    
    :return: the weather of the city in celsius
    '''
    return 24

if __name__ == '__main__':
    model = Model(
        model = ModelType.DEEPSEEK_1_5B,
        max_output_length=1000,
    )
    print(model.prompt("User: Hello!\n\nAssistant:"))
