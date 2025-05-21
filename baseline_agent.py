import os
import re
import sys
import json
import time
from datetime import datetime
import uuid

from const import ModelType, MessageType, Role
from model import Model
from agents import DecisionAgentPrompt, DecisionAgent, FunctionAgentPrompt, FunctionAgent, FunctionCalled, MISTAKE_1_COUNTER, MISTAKE_2_COUNTER, MISTAKE_3_COUNTER
from llm_tool import tool

from worlds import Automation, Communication, Configurations, CRUD, DataProcessing, DesktopManager, EventsScheduler, FileManagement, LegalCompliance, Maths, Navigation, Transactions, Validation, WebBrowsing, Writing

from typing import List, Dict, Optional


tests = {
    "automation": Automation(),
    "communication": Communication(),
    "configurations": Configurations(),
    "crud": CRUD(),
    "data_processing": DataProcessing(),
    "desktop_manager": DesktopManager(),
    "events_scheduler": EventsScheduler(),
    "file_management": FileManagement(),
    "legal_compliance": LegalCompliance(),
    "maths": Maths(),
    "navigation": Navigation(),
    "transactions": Transactions(),
    "validation": Validation(),
    "web_browsing": WebBrowsing(),
    "writing": Writing(),
}

if __name__ == '__main__':
    OUTPUT_TOKENS_CAP = 10_000
    
    temp_mistake_2_counter = 0
    FUNCTION_HALLUCINATION = 0
    PARAMETER_HALLUCINATION = 0
    GENERATED_TOKENS_AVG = 0
    temp_generated_tokens = 0
    RESULTS = []

    model = sys.argv[1]
    
    try:
    
        for world in tests.values():
            print(f'---------------------- WORLD: {world.__class__.__name__} ----------------------')
            for prompt in world.prompts:
                print(f'---------------------- PROMPT: {prompt["prompt"]} ----------------------')
                
                from agents import GENERATED_TOKENS
                temp_generated_tokens = GENERATED_TOKENS
                
                setup_functions = prompt.get('functions', [])
                user_prompt = prompt['prompt']
            
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
                        MISTAKE_3_COUNTER += 1
                        FUNCTION_HALLUCINATION += 1
                        break
                    except TypeError as e:
                        # parameter does not exist
                        print(f'Error: {repr(e)}')
                        print('Failed to call function')
                        print('[CORE]: FUNCTION CALLING ERROR')
                        # function or parameter does not exist
                        MISTAKE_3_COUNTER += 1
                        PARAMETER_HALLUCINATION += 1
                        break
                    except Exception as e:
                        # "function_name" or "arguments" do not exist -> invalid JSON format
                        print(f'Error: {repr(e)}')
                        print('Failed to call function')
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
                from agents import MISTAKE_1_COUNTER, MISTAKE_2_COUNTER, GENERATED_TOKENS
                print(f'MISTAKE_1_COUNTER: {MISTAKE_1_COUNTER}')
                print(f'MISTAKE_2_COUNTER: {MISTAKE_2_COUNTER + temp_mistake_2_counter}')
                print(f'MISTAKE_3_COUNTER: {MISTAKE_3_COUNTER}')
                print(f'FUNCTION_HALLUCINATION: {FUNCTION_HALLUCINATION}')
                print(f'PARAMETER_HALLUCINATION: {PARAMETER_HALLUCINATION}')
                print(f'GENERATED_TOKENS: {GENERATED_TOKENS - temp_generated_tokens}')
                GENERATED_TOKENS_AVG += (GENERATED_TOKENS - temp_generated_tokens)
                
                print(f'Sequence: {decision_prompt.functions_called}')
                RESULTS.append({
                    "world": world.__class__.__name__,
                    "prompt": user_prompt,
                    "functions_called": str(decision_prompt.functions_called),
                    "mistakes": {
                        "MISTAKE_1_COUNTER": MISTAKE_1_COUNTER,
                        "MISTAKE_2_COUNTER": MISTAKE_2_COUNTER + temp_mistake_2_counter,
                        "MISTAKE_3_COUNTER": MISTAKE_3_COUNTER,
                        "FUNCTION_HALLUCINATION": FUNCTION_HALLUCINATION,
                        "PARAMETER_HALLUCINATION": PARAMETER_HALLUCINATION,
                    },
                    "generated_tokens": GENERATED_TOKENS - temp_generated_tokens,
                    "database": world.world_state,
                })
    except KeyboardInterrupt:
        print('KeyboardInterrupt: Stopping the execution')

    with open(sys.argv[2], 'w') as f:
        json.dump(RESULTS, f, indent=4)