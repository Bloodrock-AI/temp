import os
import re
import sys
import ast
import json
import time
from datetime import datetime
import uuid

from ollama import ChatResponse, chat

from llm_tool import tool

from worlds import Automation, Communication, Configurations, CRUD, DesktopManager, EventsScheduler, FileManagement, LegalCompliance, Computations, Navigation, Transactions, Validation, WebBrowsing, Writing
from logger import logger

from evaluate import load_world, evaluate_world
from bfcl import evaluate_bfcl

from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union

TYPE_MAP = {"int": "integer", "str": "string", "bool": "boolean"}

@dataclass
class FunctionCalled:
    name: str
    arguments: Dict[str, Any]
    response: Any

tests = {
    "automation": Automation(),
    "communication": Communication(),
    "configurations": Configurations(),
    "crud": CRUD(),
    "desktop_manager": DesktopManager(),
    "events_scheduler": EventsScheduler(),
    "file_management": FileManagement(),
    "legal_compliance": LegalCompliance(),
    "computations": Computations(),
    "navigation": Navigation(),
    "transactions": Transactions(),
    "validation": Validation(),
    "web_browsing": WebBrowsing(),
    "writing": Writing(),
}

tests = {
    "automation": Automation(),
}

def load_prompt_dataset(dataset_file: str) -> List[Dict]:
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)

    # create dictionary to map prompt ids to prompts
    prompt_dict = {
        prompt['prompt_id']: prompt for prompt in dataset
    }
    
    eval_dict = {
        prompt['prompt_id']: load_world(prompt) for prompt in dataset
    }
    return prompt_dict, eval_dict


class ToolCall:
    def __init__(self, id, name, arguments, tool_type):
        """
        Represents a single tool call.
        
        Args:
            id (str): An identifier for the tool call.
            name (str): The name of the tool.
            arguments (str): A string (or JSON) representation of the arguments.
            tool_type (str): The type of tool, e.g., "function".
        """
        self.id = id
        self.name = name
        self.arguments = arguments
        self.tool_type = tool_type

    def __str__(self):
        return f"ToolCall(id={self.id}, name={self.name}, arguments={self.arguments}, type={self.tool_type})"

    def to_dict(self) -> dict:
        return {
            "type": "ToolCall",
            "id": self.id,
            "name": self.name,
            "arguments": self.arguments,
            "tool_type": self.tool_type
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


# Replaced with ollama below::: client = InferenceClient(provider="auto")
class OllamaClient:

    def __init__(self, model="qwen3:0.6b", temperature=0.1, num_predict=-1, **kwargs):
        """
        Initialize the Ollama client.

        Args:
            model (str): The model name.
            **kwargs: Additional parameters.
        """
        self.model = model # you can overwrite following get_next_function
        self.temperature = temperature
        self.params = kwargs
        self.client_class = "OllamaClient"

        self.num_predict = num_predict
        self.num_ctx = self.get_num_ctx(model) 


    def get_next_functions(self, model, messages_history, tool_definitions=None):
        """
        Send the conversation history (and tools, if provided) to 
        Ollama's API (running locally) and return the response.

        Args:
            messages (list): Conversation history.
            tools (list, optional): Tool specifications.

        Returns:
            dict: A dictionary with keys like "response", "prompt_tokens", "completion_tokens".
        """
        start_time = time.time()
        response: ChatResponse = chat(
            model,
            messages=messages_history,
            tools=tool_definitions,
            options= {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict
            }
        )
        elapsed_time = round(time.time() - start_time, 4)

        print(response.message.tool_calls) # TODO: always returns more calls!
        # get next tool call
        # if response.message.tool_calls is not None:
        #     tool_next = response.message.tool_calls[0]
        #     print(tool_next)
        #     tool_call_id = getattr(tool_next, 'id', 0)
        #     tool_call = ToolCall(
        #         id=tool_call_id,
        #         name=tool_next.function.name,
        #         arguments=json.dumps(tool_next.function.arguments),
        #         tool_type=getattr(tool_next, 'type', "function")
        #     )
        #     return tool_call_id, tool_call

        # return None, None
        return response.message.tool_calls

    def get_num_ctx(self, model):
        token_limits = {
            128000: {
                "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b", "qwen2.5:72b",
                "qwen2:7b", "qwen2:72b", "qwen3:8b",
                "hermes3:3b", "hermes3:8b", "hermes3:70b",
                "llama3.3", "llama3.3:70b", "llama3.2:1b", "llama3.2:3b",
            },
            32000: {
                "qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b", "qwq", "qwq:32b",
                "mistral-small:22b", "mistral-large:123b", "mistral-small:24b"
            }
        }
        # Check which token limit applies, return default (128000) if not found
        for max_tokens, models in token_limits.items():
            if model in models:
                return max_tokens

        return 128000  # Default case


def _transform_types(x: Any) -> Any:
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if k == "type" and isinstance(v, str):
                out[k] = TYPE_MAP.get(v, v)
            else:
                out[k] = _transform_types(v)
        return out
    if isinstance(x, list):
        return [_transform_types(i) for i in x]
    return x


def parse_world_tools(tool_definitions: Union[str, List[Dict]]) -> List[Dict]:
    # 1) Get to a Python structure without regex text surgery
    if isinstance(tool_definitions, (list, dict)):
        obj = tool_definitions
    elif isinstance(tool_definitions, str):
        # Try JSON first
        try:
            obj = json.loads(tool_definitions)
        except json.JSONDecodeError:
            # Fall back to Python-literal parsing (handles single quotes, etc.)
            # This also safely parses only literals.
            obj = ast.literal_eval(tool_definitions)
    else:
        raise TypeError("tool_definitions must be a list/dict or a string")

    # 2) Transform types structurally (str->string, int->integer, bool->boolean)
    obj = _transform_types(obj)

    # 3) Optionally, normalize to JSON-compatible data (and back to Python) to ensure cleanliness
    # This escapes any embedded quotes correctly.
    return json.loads(json.dumps(obj, ensure_ascii=False))

ollama_client = OllamaClient()

def main(model: str, output_file: str):
    # load dataset
    dataset_file = 'all_worlds_dataset.json'
    prompt_dict, eval_dict = load_prompt_dataset(dataset_file)

    OUTPUT_TOKENS_CAP = 5_000
    
    GENERATED_TOKENS_AVG = 0
    RESULTS = []
    try:
    
        for world in list(tests.values()):
            print(f'---------------------- WORLD: {world.__class__.__name__} ----------------------')
            # for prompt in world.prompts:
            for prompt in world.prompts[:1]:

                # prompt from dataset
                current_prompt = prompt_dict.get(prompt['prompt_id'], None)
                if current_prompt is None:
                    print(f'Prompt with id {prompt["prompt_id"]} not found in dataset.')
                    continue
                
                user_prompt = current_prompt.get('prompt', None)
                if user_prompt is None:
                    print(f'Prompt with id {prompt["id"]} not found in dataset.')
                    continue
                
                print(f'---------------------- PROMPT: {user_prompt} ----------------------')
                
                setup_functions = prompt.get('setup_functions', [])

                # reset the database
                world.reset_world_state()

                # run setup functions
                for function in setup_functions:
                    eval(f'world.{function}')

                tool_definitions = parse_world_tools(world.tool_definitions)
                if isinstance(world, Computations):
                    tool_definitions[1]["function"]["parameters"]["properties"]["numbers"] = {
                            "type": "array",
                            "items": { "type": "integer" },
                            "description": "A list of integers.",
                        }
                    # replace 'float' with 'number'
                    tool_str = json.dumps(tool_definitions).replace("float", "number")
                    tool_definitions = json.loads(tool_str)
                
                function_agent_messages_history = [
                    {
                        "role": "system",
                        "content": f"""
You are a helpful assistant which can use functions in order to satisfy the user's query.

{f"Additional Instructions: {world.function_system_prompt}" if world.function_system_prompt else ""}

Your task is to give the next function which should be called in order to satisfy the user's prompt.

                        """
                    },
                    {
                        "role": "tool",
                        "tool_call_id": str(uuid.uuid4()),
                        "name": "update_world_state",
                        "content": world.world_state_description.format(world.world_state)
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ]
                
                function_sequence = []
                prompt_iterations = 0
                MAX_PROMPT_ITERATIONS = 15

                while prompt_iterations < MAX_PROMPT_ITERATIONS:  # Limit iterations to prevent infinite loops
                    try:
                        tool_calls = ollama_client.get_next_functions(
                            model=model,
                            messages_history=function_agent_messages_history,
                            tool_definitions=tool_definitions,
                        )
                    except Exception as e:
                        raise e
                        print(f'Error: {repr(e)}')
                        print(f'Failed to parse function')
                        break

                    if not tool_calls:
                        print('No tool calls found, ending the process.')
                        break
                    
                    for tool_call in tool_calls:
                        if prompt_iterations >= MAX_PROMPT_ITERATIONS:
                            break
                        tool_call_id = tool_call.id
                        function = FunctionCalled(
                            name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                            response=None,  # Will be filled after function call
                        )

                        print(f'Calling function: {function.name}')

                        try:
                            # calling the function
                            resp = getattr(world, function.name)(**json.loads(function.arguments))
                        except AttributeError as e:
                            # function does not exist
                            print(f'Error: {repr(e)}')
                            print('Failed to call function')
                            print('[CORE]: FUNCTION CALLING ERROR')
                            break
                        except TypeError as e:
                            # parameter does not exist
                            print(f'Error: {repr(e)}')
                            print('Failed to call function')
                            print('[CORE]: FUNCTION CALLING ERROR')
                            # function or parameter does not exist
                            break
                        except Exception as e:
                            # "function_name" or "arguments" do not exist -> invalid JSON format
                            print(f'Error: {repr(e)}')
                            print('Failed to call function')
                            logger.mistake_counters["type_2"] += 1
                            break

                        # add tool call to the history
                        function_agent_messages_history.append({
                            "tool_call_id": tool_call_id,
                            "role": "tool",
                            "name": function.name,
                            "content": json.dumps(resp),
                        })

                        function_sequence.append({
                            "function_name": function.name,
                            "arguments": function.arguments,
                            "response": function.response
                        })
                        
                        prompt_iterations += 1

                    # update additional states
                    new_state = world.world_state_description.format(world.world_state)

                    # add current world state to the history
                    function_agent_messages_history.append({
                        "tool_call_id": str(uuid.uuid4()),
                        "role": "tool",
                        "name": "update_world_state",
                        "content": json.dumps(new_state),
                    })

                # print mistake counters
                print(f'------------ logger ------------')
                print(f'Functions called: {function_sequence}')

                # run evaluation
                prompt_res = {
                    "world": world.__class__.__name__,
                    "prompt_id": prompt['prompt_id'],
                    "prompt": user_prompt,
                    "functions_called": json.dumps(function_sequence),
                    "database": world.world_state,
                }
                prompt_eval_world = eval_dict.get(prompt['prompt_id'], None)

                # stats = evaluate_world(prompt_eval_world, prompt_res)
                bfcl_stats = evaluate_bfcl(world, prompt['prompt_id'], world.world_state.copy(), function_sequence)
                print(f'------------ stats ------------')
                # print(f'Stats: {stats}')
                print(f'BFCL Stats: {bfcl_stats}')

                prompt_res["bfcl_stats"] = bfcl_stats
                # prompt_res["core_stats"] = stats
                RESULTS.append(prompt_res)
    except Exception as e:
        print(f'Error: {repr(e)}')

    finally:
        with open(output_file, 'w') as f:
            json.dump(RESULTS, f, indent=4)