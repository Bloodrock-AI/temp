import os
import re
import sys
import json
import time
from datetime import datetime
import uuid

from const import ModelType, MessageType, Role
from model import Model
from agents import DecisionAgentPrompt, DecisionAgent, FunctionAgentPrompt, FunctionAgent, FunctionCalled
from llm_tool import tool

from worlds import Automation, Communication, Configurations, CRUD, DesktopManager, EventsScheduler, FileManagement, LegalCompliance, Maths, Navigation, Transactions, Validation, WebBrowsing, Writing
from logger import logger

from typing import List, Dict, Optional


tests = {
    "automation": Automation(),
    # "communication": Communication(),
    # "configurations": Configurations(),
    # "crud": CRUD(),
    # "desktop_manager": DesktopManager(),
    # "events_scheduler": EventsScheduler(),
    # "file_management": FileManagement(),
    # "legal_compliance": LegalCompliance(),
    # "maths": Maths(),
    # "navigation": Navigation(),
    # "transactions": Transactions(),
    # "validation": Validation(),
    # "web_browsing": WebBrowsing(),
    # "writing": Writing(),
}

def load_prompt_dataset(dataset_file: str) -> List[Dict]:
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)

    # create dictionary to map prompt ids to prompts
    prompt_dict = {
        prompt['id']: prompt for prompt in dataset
    }
    return prompt_dict

def main(model: str, output_file: str):

    # load dataset
    dataset_file = 'all_worlds_dataset.json'
    prompt_dict = load_prompt_dataset(dataset_file)

    OUTPUT_TOKENS_CAP = 10_000
    
    GENERATED_TOKENS_AVG = 0
    RESULTS = []
    
    try:
    
        for world in list(tests.values()):
            logger.reset()
            print(f'---------------------- WORLD: {world.__class__.__name__} ----------------------')
            for prompt in world.prompts:
                logger.reset()
                
                # prompt from dataset
                user_prompt = prompt_dict.get(prompt['id'], None)
                if user_prompt is None:
                    print(f'Prompt with id {prompt["id"]} not found in dataset.')
                    continue
                
                print(f'---------------------- PROMPT: {user_prompt} ----------------------')
                
                # from agents import GENERATED_TOKENS
                # temp_generated_tokens = GENERATED_TOKENS
                prev_generated_tokens = logger.mistake_counters["generated_tokens"]
                
                setup_functions = prompt.get('functions', [])
            
                # reset the database
                world_state = world.world_state
                
                # run setup functions
                for function in setup_functions:
                    eval(f'world.{function}')

                tool_definitions = world.tool_definitions
            
                FUNCTION_SYSTEM_PROMPT = world.function_system_prompt
                DECISION_SYSTEM_PROMPT = world.decision_system_prompt

                decision_prompt = DecisionAgentPrompt(
                    function_definitions=tool_definitions,
                    user_prompt=user_prompt,
                    additional_instructions=DECISION_SYSTEM_PROMPT,
                    additional_state=world.world_state_description.format(world_state)
                )

                function_prompt = FunctionAgentPrompt(
                    function_definitions=tool_definitions,
                    user_prompt=user_prompt,
                    additional_instructions=FUNCTION_SYSTEM_PROMPT,
                    additional_state=world.world_state_description.format(world_state)
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
                        temp_mistake_2_counter += 1
                        break
                    
                    fc = FunctionCalled(
                        name=function["function_name"],
                        arguments=function["arguments"],
                        response=resp,
                    )
                    
                    # update additional states
                    new_state = world.world_state_description.format(world_state)
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
                    "prompt_id": prompt['id'],
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