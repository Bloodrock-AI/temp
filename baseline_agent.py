import os
import re
import json
import time
from datetime import datetime
import uuid

from const import ModelType, MessageType, Role
from model import Model
from agents import DecisionAgentPrompt, DecisionAgent, FunctionAgentPrompt, FunctionAgent, FunctionCalled, MISTAKE_1_COUNTER, MISTAKE_2_COUNTER, MISTAKE_3_COUNTER
from llm_tool import tool

from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that makes changes on a database. The database is a list of users. Always check the database and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that makes changes on a database. The database is a list of users. Always check the database.
"""

# In-memory database for user records
database = {}

def generate_timestamp():
    """Generates the current timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat() + "Z"

@tool()
def add_user(name: str, age: int, email: Optional[str] = None) -> str:
    """
    Adds a new user to the database and returns the user ID.

    :param name: The name of the user to be added.
    :param age: The age of the user to be added.
    :param email: The email of the user to be added.
    :return: user ID
    """
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    timestamp = generate_timestamp()
    new_user = {
        "id": user_id,
        "name": name,
        "age": age,
        "email": email,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    database[user_id] = new_user
    return user_id

@tool()
def update_user_email(user_id: str, email: str) -> bool:
    """
    Updates a user's email.

    :param user_id: The user ID of the user to be updated.
    :param email: The updated email of the user.
    :return: True if the user was found and updated, False otherwise
    """
    if user_id not in database:
        return False
    user = database[user_id]
    timestamp = generate_timestamp()
    user["email"] = email
    user["updated_at"] = timestamp
    return True
    
@tool()
def delete_user(user_id: str) -> bool:
    """
    Deletes a user from the database by user ID.

    :param user_id: The user ID of the user to be deleted. 
    :return: True if the user was found and deleted, False otherwise
    """
    if user_id in database:
        del database[user_id]
        return True
    return False

@tool()
def list_users() -> List[Dict]:
    """
    Returns a list of users, optionally filtered by specific criteria.
    :return: list of users
    """
    return list(database.values())
    
@tool()
def verify_user_field(user_id: str, field: str, expected_value: str) -> bool:
    """
    Verifies if a specific field in a user record matches the expected value.

    :param user_id: The user ID of the user to be verified.
    :param field: field to check
    :param expected_value: expected value
    :return: True if the field matches the expected value, False otherwise
    """
    user = database.get(user_id, None)
    if not user:
        return False
    return user.get(field) == expected_value

tool_definitions = [
    add_user.definition,
    delete_user.definition,
    list_users.definition,
    verify_user_field.definition,
    update_user_email.definition,
]

prompts = [
    {
        "prompt": "Create a new user named 'Alice' with an age of 25. Retrieve the details of this user and confirm the age field is correct",
    },
    {
        "prompt": "Show all users and update the email of the user with name 'Alice' to 'alice@example.com'. Ensure the changes were applied.",
        "functions": [
            'add_user(name="Alice", age=25)',
        ],
    },
    {
        "prompt": "Show all users. Then, update the emails of all users with no email address to 'default@example.com'. Pick one of these users and ensure the changes were applied.",
        "functions": [
            'add_user(name="John", age=30, email=None)',
            'add_user(name="Jane", age=25, email=None)',
        ],
    },
    {
        "prompt": "Add a new user named 'Charlie' aged 40 with email 'charlie@email.com'. Then, delete that user. Finally, confirm the deletion by showing all the users."
    },
    {
        "prompt": "Create a new user named 'Eve' with an age of 22 and empty email. Then, update their email to 'eve@example.com'. Finally delete the user and verify the deletion by checking all the existing users.",
    }
]


if __name__ == '__main__':
    temp_mistake_2_counter = 0
    FUNCTION_HALLUCINATION = 0
    PARAMETER_HALLUCINATION = 0
    GENERATED_TOKENS_AVG = 0
    temp_generated_tokens = 0

    model = ModelType.DEEPSEEK_LLAMA_8B
    # user_prompt = prompts[0]['prompt']
    
    for test in prompts:
        from agents import GENERATED_TOKENS
        temp_generated_tokens = GENERATED_TOKENS
        setup_functions = test.get('functions', [])
        user_prompt = test['prompt']
    
        # reset the database
        database = {}
        # run setup functions
        for function in setup_functions:
            eval(function)
    
        decision_prompt = DecisionAgentPrompt(
            function_definitions=tool_definitions,
            user_prompt=user_prompt,
            additional_instructions=DECISION_SYSTEM_PROMPT,
            additional_state=f"Database: {database}"
        )
        
        function_prompt = FunctionAgentPrompt(
            function_definitions=tool_definitions,
            user_prompt=user_prompt,
            additional_instructions=FUNCTION_SYSTEM_PROMPT,
            additional_state=f"Database: {database}"
        )
        
        decision_agent = DecisionAgent(
            model=model,
            prompt=decision_prompt,
            max_output_length=5000,
        )
        
        function_agent = FunctionAgent(
            model=model,
            prompt=function_prompt,
            max_output_length=5000,
        )
        
        while True:
            
            try:
                function = function_agent.get_next_function()
            except Exception as e:
                print(f'Error: {repr(e)}')
                print(f'Failed to parse function')
                break
            
            print(function)
            
            try:
                current_module = __import__(__name__)
                resp = getattr(current_module, function["function_name"])(**function["arguments"])
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
            new_state = f"Database: {database}"
            decision_prompt.additional_state = new_state
            function_prompt.additional_state = new_state
            
            decision_prompt.function_called(fc)
            function_prompt.function_called(fc)
            
            if decision_agent.decide(): break
            
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
    
    # print mistake counters
    from agents import MISTAKE_1_COUNTER, MISTAKE_2_COUNTER, GENERATED_TOKENS
    print(f'MISTAKE_1_COUNTER: {MISTAKE_1_COUNTER}')
    print(f'MISTAKE_2_COUNTER: {MISTAKE_2_COUNTER + temp_mistake_2_counter}')
    print(f'MISTAKE_3_COUNTER: {MISTAKE_3_COUNTER}')
    print(f'FUNCTION_HALLUCINATION: {FUNCTION_HALLUCINATION}')
    print(f'PARAMETER_HALLUCINATION: {PARAMETER_HALLUCINATION}')
    print(f'GENERATED_TOKENS_AVG: {GENERATED_TOKENS_AVG / len(prompts)}')