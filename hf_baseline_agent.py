import os
import re
import sys
import ast
import json
import time
from datetime import datetime
import uuid

from const import ModelType, MessageType, Role
from huggingface_hub import InferenceClient
from llm_tool import tool

from worlds import Automation, Communication, Configurations, CRUD, DesktopManager, EventsScheduler, FileManagement, LegalCompliance, Computations, Navigation, Transactions, Validation, WebBrowsing, Writing, RoboticArm, FarmingRover
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
    "robotic_arm": RoboticArm(),
    "robot_farm": FarmingRover(),
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

def get_next_function(
        model: str,
        messages_history: List[Dict] = None,
        client: Optional[InferenceClient] = None,
        tool_definitions: List[Dict] = None,
        max_tokens: int = 1000,
    ) -> Dict:
    output = client.chat.completions.create(
        model=model,
        messages=messages_history,
        tools=tool_definitions,
        tool_choice="auto",
        temperature=0.0,
        max_tokens=max_tokens,
    )
    # get next tool call
    if output.choices[0].message.tool_calls:
        print(output.choices[0].message.tool_calls)
        return output.choices[0].message.tool_calls[0].id, output.choices[0].message.tool_calls[0].function
    return None, None

client = InferenceClient(provider="auto")

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
            for prompt in world.prompts:

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
                        tool_call_id, function = get_next_function(
                            model=model.value,
                            messages_history=function_agent_messages_history,
                            client=client,
                            tool_definitions=tool_definitions,
                            max_tokens=OUTPUT_TOKENS_CAP,
                        )
                    except Exception as e:
                        raise e
                        print(f'Error: {repr(e)}')
                        print(f'Failed to parse function')
                        break

                    print(f'Calling function: {function}')

                    if function is None:
                        print("No function needed, ending the process.")
                        break

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

                    # update additional states
                    new_state = world.world_state_description.format(world.world_state)

                    # add current world state to the history
                    function_agent_messages_history.append({
                        "tool_call_id": str(uuid.uuid4()),
                        "role": "tool",
                        "name": "update_world_state",
                        "content": json.dumps(new_state),
                    })

                    fc = FunctionCalled(
                        name=function.name,
                        arguments=function.arguments,
                        response=resp,
                    )
                    function_sequence.append({
                        "function_name": fc.name,
                        "arguments": fc.arguments,
                        "response": fc.response
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