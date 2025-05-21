from enum import Enum
from dataclasses import dataclass

class ModelType(Enum):
    # SPECIAL
    GPT_2 = "gpt2"
    DEEPSCALE_R = "agentica-org/DeepScaleR-1.5B-Preview"
    
    # deepseek-ai
    DEEPSEEK_1_5B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    DEEPSEEK_QWEN_7B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    DEEPSEEK_LLAMA_8B = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
    DEEPSEEK_QWEN_14B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
    DEEPSEEK_LLAMA_70B = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
    
    # Qwen
    QWEN_0_5B = "Qwen/Qwen2.5-0.5B"
    QWEN_7B = "Qwen/Qwen-7B"
    
    # Mistral
    MISTRAL_24B = "mistralai/Mistral-Small-3.1-24B-Instruct-2503"
    
    # Llama
    LLAMA_3_3_70B = "meta-llama/Llama-3.3-70B-Instruct"
    

class Role(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    TOOL = "tool"
    
@dataclass
class MessageType:
    role: Role
    content: str

STOP_STRINGS = ['\n</end_of_response>\n', '\n</end_of_response>', '</end_of_response>\n', '</end_of_response>']

base_system_prompt = '''
You are a helpful assistant which can use functions in order to satisfy the user's query.
These are the functions which you have access to:
{}

Your task is to give the next function which should be called in order to satisfy the user's prompt.

User prompt: "{}"

You should give the next function which should be called.
You should provide ONLY ONE function, the one that should be called right now.
Give your answer in JSON format as follows:
```json
{
    "type": "function_call",
    "name": "function name",
    "arguments": {
        "argument name": "argument value"
    }
}
```

Please give your answer now:

<think>
What function should I call next?
'''

# base_system_prompt = f'''
#     The following are additional instructions for the application you are assisting with:
#     {'{}'}
    
#     You are a helpful assistant. You can call these functions if needed:

#     {'{}'}

#     When you want to call a function, respond only in valid JSON with two keys:
#       'name': function_name
#       'arguments': JSON object with relevant arguments
#     Surround the JSON with the <function> tag

#     Format:
#     <function>
#     {'{{ "name": "function_name", "arguments": {{ "argument_name": "argument_value" }} }}'}
#     </function>

#     If you are just answering without calling a function, answer in plain text.
    
#     Always end your responses with {STOP_STRINGS[0]}
# '''

# base_system_prompt_no_functions = f'''
# {'{}'}

# Always end your responses with {STOP_STRINGS[0]}
# '''
