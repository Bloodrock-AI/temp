import os
import re
import sys
import json
import time
from copy import deepcopy
from datetime import datetime
import uuid

from bfcl_dataset import GorillaFileSystem, MathAPI, MessageAPI, TwitterAPI, TicketAPI, TradingBot, TravelAPI, VehicleControlAPI
from const import ModelType, MessageType, Role
from model import Model
from agents import DecisionAgentPrompt, DecisionAgent, FunctionAgentPrompt, FunctionAgent, FunctionCalled
from llm_tool import tool

from logger import logger

from typing import List, Dict, Optional

bfcl_worlds = {
    "GorillaFileSystem": GorillaFileSystem,
    "MathAPI": MathAPI,
    "MessageAPI": MessageAPI,
    "TwitterAPI": TwitterAPI,
    "TicketAPI": TicketAPI,
    "TradingBot": TradingBot,
    "TravelAPI": TravelAPI,
    "VehicleControlAPI": VehicleControlAPI,
}

def load_tool_definitions(tool_definitions_file: str) -> List[Dict]:
    with open(tool_definitions_file, 'r') as f:
        tool_definitions = json.load(f)

    return tool_definitions

def load_test_entries_dataset(dataset_file: str) -> List[Dict]:
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)

    # create dictionary to map prompt ids to prompts
    test_entry_dict = {
        e['prompt_id']: e for e in dataset
    }
    return test_entry_dict

def _prep_name(name: str) -> str:
    # prepare name: capitalize first letter after each underscore & remove underscores
    name = re.sub(r'_(\w)', lambda x: x.group(1).upper(), name)
    # capitalize first letter
    name = name[0].upper() + name[1:]
    # remove underscores
    name = name.replace('_', '')
    # replace `api` with `API`
    name = name.replace('Api', 'API')
    return name

def main(model: str, output_file: str):

    # load datasets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_file = os.path.join(base_dir, 'bfcl_dataset', 'all_bfcl_worlds_dataset.json')
    test_entry_dict = load_test_entries_dataset(dataset_file)
    tool_definitions = {}
    for file in os.listdir(os.path.join(base_dir, 'bfcl_dataset', 'worlds')):
        if file.endswith('.json'):
            tool_definitions_file = os.path.join(base_dir, 'bfcl_dataset', 'worlds', file)
            _tool_definitions = load_tool_definitions(tool_definitions_file)
            
            name = _prep_name(file[:-5])  # remove .json extension
            tool_definitions[name] = _tool_definitions

    OUTPUT_TOKENS_CAP = 10_000
    
    GENERATED_TOKENS_AVG = 0
    RESULTS = []
    
    try:
        for test_entry in test_entry_dict.values():
            logger.reset()

            active_worlds = {}
            for world in test_entry['involved_classes']:
                active_worlds[world] = bfcl_worlds[world]()
                active_worlds[world]._load_scenario(test_entry['initial_config'])
    
            # prompt from dataset
            user_prompt = test_entry["prompt"]
            
            print(f'---------------------- PROMPT: {user_prompt} ----------------------')
            
            prev_generated_tokens = logger.mistake_counters["generated_tokens"]
            
            # tool_definitions = world.tool_definitions
            # get tool descriptions from all active worlds
            
        
            FUNCTION_SYSTEM_PROMPT = world.function_system_prompt
            DECISION_SYSTEM_PROMPT = world.decision_system_prompt

            decision_prompt = DecisionAgentPrompt(
                function_definitions=tool_definitions,
                user_prompt=user_prompt,
                additional_instructions=DECISION_SYSTEM_PROMPT,
                additional_state=world.world_state_description.format(world.world_state)
            )

            function_prompt = FunctionAgentPrompt(
                function_definitions=tool_definitions,
                user_prompt=user_prompt,
                additional_instructions=FUNCTION_SYSTEM_PROMPT,
                additional_state=world.world_state_description.format(world.world_state)
            )
            
            decision_agent = DecisionAgent(
                model=model,
                prompt=decision_prompt,
                max_output_length=OUTPUT_TOKENS_CAP,
            )
            
            function_agent = FunctionAgent(
                model=model,
                prompt=function_prompt,
                max_output_length=OUTPUT_TOKENS_CAP,
            )
            
            while True:
                
                try:
                    function = function_agent.get_next_function()
                except Exception as e:
                    print(f'Error: {repr(e)}')
                    print(f'Failed to parse function')
                    break
                
                print(f'Calling function: {function}')
                
                try:
                    resp = getattr(world, function["function_name"])(**function["arguments"])
                except AttributeError as e:
                    # function does not exist
                    print(f'Error: {repr(e)}')
                    print('Failed to call function')
                    print('[CORE]: FUNCTION CALLING ERROR')
                    logger.mistake_counters["type_3"] += 1
                    logger.mistake_counters["function_hallucination"] += 1
                    break
                except TypeError as e:
                    # parameter does not exist
                    print(f'Error: {repr(e)}')
                    print('Failed to call function')
                    print('[CORE]: FUNCTION CALLING ERROR')
                    # function or parameter does not exist
                    logger.mistake_counters["type_3"] += 1
                    logger.mistake_counters["parameter_hallucination"] += 1
                    break
                except Exception as e:
                    # "function_name" or "arguments" do not exist -> invalid JSON format
                    print(f'Error: {repr(e)}')
                    print('Failed to call function')
                    logger.mistake_counters["type_2"] += 1
                    break
                
                fc = FunctionCalled(
                    name=function["function_name"],
                    arguments=function["arguments"],
                    response=resp,
                )
                
                # update additional states
                new_state = world.world_state_description.format(world.world_state)
                decision_prompt.additional_state = new_state
                function_prompt.additional_state = new_state
                
                decision_prompt.function_called(fc)
                function_prompt.function_called(fc)
                
                try:
                    if decision_agent.decide(): break
                except Exception as e:
                    print(f'Error: {repr(e)}')
                    print('Failed to parse decision')
                    break
                    
                # print mistake counters
                print(f'------------ logger ------------')
                print(f'MISTAKE_1_COUNTER: {logger.mistake_counters["type_1"]}')
                print(f'MISTAKE_2_COUNTER: {logger.mistake_counters["type_2"]}')
                print(f'MISTAKE_3_COUNTER: {logger.mistake_counters["type_3"]}')
                print(f'FUNCTION_HALLUCINATION: {logger.mistake_counters["function_hallucination"]}')
                print(f'PARAMETER_HALLUCINATION: {logger.mistake_counters["parameter_hallucination"]}')
                print(f'GENERATED_TOKENS: {logger.mistake_counters["generated_tokens"] - prev_generated_tokens}')
                GENERATED_TOKENS_AVG += logger.mistake_counters["generated_tokens"] - prev_generated_tokens
                
                print(f'Sequence: {decision_prompt.functions_called}')
                RESULTS.append({
                    "world": world.__class__.__name__,
                    "prompt_id": prompt['prompt_id'],
                    "prompt": user_prompt,
                    "functions_called": str(decision_prompt.functions_called),
                    "mistakes": {
                        "MISTAKE_1_COUNTER": logger.mistake_counters["type_1"],
                        "MISTAKE_2_COUNTER": logger.mistake_counters["type_2"],
                        "MISTAKE_3_COUNTER": logger.mistake_counters["type_3"],
                        "FUNCTION_HALLUCINATION": logger.mistake_counters["function_hallucination"],
                        "PARAMETER_HALLUCINATION": logger.mistake_counters["parameter_hallucination"],
                    },
                    "generated_tokens": logger.mistake_counters["generated_tokens"] - prev_generated_tokens,
                    "database": world.world_state,
                })
    except KeyboardInterrupt:
        print('KeyboardInterrupt: Stopping the execution')

    with open(output_file, 'w') as f:
        json.dump(RESULTS, f, indent=4)