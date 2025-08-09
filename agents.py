import re
import json
from dataclasses import dataclass

from llm_tool import tool

from model import Model
from const import (
    ModelType
)
from logger import logger

from typing import List, Dict, Any, Optional

LOG_FILE = "run_logs/log.txt"
MISTAKE_1_COUNTER = 0
MISTAKE_2_COUNTER = 0
MISTAKE_3_COUNTER = 0
GENERATED_TOKENS = 0

@dataclass
class FunctionCalled:
    name: str
    arguments: Dict[str, Any]
    response: Any

class DecisionAgentPrompt:

    def __init__(
        self,
        function_definitions: List[Dict[str, str]],
        user_prompt: str,
        think: bool = True,
        additional_instructions: Optional[str] = None,
        additional_state: Optional[str] = None
    ):
        self.function_definitions = function_definitions
        self.user_prompt = user_prompt
        self.functions_called: List[FunctionCalled] = []
        self.functions_called_str: str = ''
        self.think = think
        self.additional_instructions = additional_instructions
        self.additional_state = additional_state
    
    def function_called(self, func: FunctionCalled) -> None:
        self.functions_called.append(func)
        self._parse_functions_called()
    
    def _parse_functions_called(self) -> None:
        if not len(self.functions_called):
            self.functions_called_str = ""
            return
            
        self.functions_called_str = json.dumps([
            {
                "name": func.name,
                "arguments": func.arguments,
                "response": func.response,
            } for func in self.functions_called
        ])
        
    def get_prompt(self) -> str:
        return f'''
You are a helpful assistant which decides whether the user's query is satisfied or not.
Your task is to answer whether or not the user's query is satisfied based on the functions already called.
You cannot call any of the functions. Your task is to solely decide whether the functions called were enough.

{f"Additional Instructions: {self.additional_instructions}" if self.additional_instructions else ""}

User prompt: "{self.user_prompt}"

Available functions:
{self.function_definitions}

Functions called: {self.functions_called_str if self.functions_called_str else "No functions called yet"}

You should decide if the above functions and their responses were enough to satisfy the user's query.
You should provide answer in JSON format as follows:
```json
{{
    "answer": true
}}
```

Please give your answer now:

{"<think>" if self.think else ""}
Alright so the user query is: "{self.user_prompt}"

and the functions called and their responses were: {self.functions_called_str if self.functions_called_str else "No functions called yet"}

{f"and the additional state is: {self.additional_state}" if self.additional_state else ""}

What are the user prompt's different goals? Are the functions called enough to satisfy all of the prompt's aspects? Shoould more functions be called?
Let me break it down:
<token>
'''

    def get_prompt_v2(self) -> str:
        system = f'''
You are a helpful assistant which decides whether the user's query is satisfied or not.
Your task is to answer whether or not the user's query is satisfied based on the functions already called.
You cannot call any of the functions. Your task is to solely decide whether the functions called were enough.

{f"Additional Instructions: {self.additional_instructions}" if self.additional_instructions else ""}

Available functions:
{self.function_definitions}

You should decide if the above functions and their responses were enough to satisfy the user's query.
You should provide answer in JSON format as follows:
```json
{{
    "answer": true
}}
```

Please give your answer now:

{"<think>" if self.think else ""}
Alright so the user query is: "{self.user_prompt}"

and the functions called and their responses were: {self.functions_called_str if self.functions_called_str else "No functions called yet"}

{f"and the additional state is: {self.additional_state}" if self.additional_state else ""}

What are the user prompt's different goals? Are the functions called enough to satisfy all of the prompt's aspects? Shoould more functions be called?
Let me break it down:
'''
        user = self.user_prompt

        tools = str({
                    "name": func.name,
                    "arguments": func.arguments,
                    "response": func.response,
                }) for func in self.functions_called

        return [
            { "system": system },
            { "user": user },
            *[{ "tool": t } for t in tools]
        ]

class FunctionAgentPrompt:

    def __init__(
        self,
        function_definitions: List[Dict[str, str]],
        user_prompt: str,
        think: bool = True,
        additional_instructions: Optional[str] = None,
        additional_state: Optional[str] = None
    ):
        self.function_definitions = function_definitions
        self.user_prompt = user_prompt
        self.functions_called: List[FunctionCalled] = []
        self.functions_called_str: str = ''
        self.think = think
        self.additional_instructions = additional_instructions
        self.additional_state = additional_state
    
    def function_called(self, func: FunctionCalled) -> None:
        self.functions_called.append(func)
        self._parse_functions_called()
    
    def _parse_functions_called(self) -> None:
        if not len(self.functions_called):
            self.functions_called_str = ""
            return
            
        self.functions_called_str = '\n\n'.join([
            f'''
            Step {index+1}
            I call the function:
            ```json
                {{
                    "type": "function_call",
                    "function_name": "{func.name}",
                    "arguments": {func.arguments}
                }}
            ```
            
            The function returned:
            {{
                "type": "function_response",
                "function_name": "{func.name}",
                "response": {func.response}
            }}
            ''' for index, func in enumerate(self.functions_called)
        ])
        
    def get_prompt(self) -> str:
        return f'''
You are a helpful assistant which can use functions in order to satisfy the user's query.
These are the functions which you have access to:
{self.function_definitions}

{f"Additional Instructions: {self.additional_instructions}" if self.additional_instructions else ""}

Your task is to give the next function which should be called in order to satisfy the user's prompt.

User prompt: "{self.user_prompt}"

You should give the next function which should be called.
You should provide ONLY ONE function, the one that should be called right now.
Give a SINGLE function call. Give a SINGLE JSON object.
Give your answer in JSON format as follows:
```json
{{
    "type": "function_call",
    "function_name": "function name",
    "arguments": {{
        "argument name": "argument value"
    }}
}}
```


Please give your answer now:

{"<think>" if self.think else ""}
{self.functions_called_str if self.functions_called_str else "I haven't called any functions yet."}

{f"and the additional state is: {self.additional_state}" if self.additional_state else ""}

What function should I call next?
<token>
'''
        
    def get_prompt_v2(self) -> str:
        system = f'''
You are a helpful assistant which can use functions in order to satisfy the user's query.
These are the functions which you have access to:
{self.function_definitions}

{f"Additional Instructions: {self.additional_instructions}" if self.additional_instructions else ""}

Your task is to give the next function which should be called in order to satisfy the user's prompt.

You should give the next function which should be called.
You should provide ONLY ONE function, the one that should be called right now.
Give a SINGLE function call. Give a SINGLE JSON object.
Give your answer in JSON format as follows:
```json
{{
    "answer": true
}}
```

Please give your answer now:

{"<think>" if self.think else ""}
Alright so the user query is: "{self.user_prompt}"

and the functions called and their responses were: {self.functions_called_str if self.functions_called_str else "No functions called yet"}

{f"and the additional state is: {self.additional_state}" if self.additional_state else ""}

What are the user prompt's different goals? Are the functions called enough to satisfy all of the prompt's aspects? Shoould more functions be called?
Let me break it down:
'''
        user = self.user_prompt

        tools = str({
                    "name": func.name,
                    "arguments": func.arguments,
                    "response": func.response,
                }) for func in self.functions_called

        return [
            { "system": system },
            { "user": user },
            *[{ "tool": t } for t in tools]
        ]

class DecisionAgent:
    def __init__(
        self,
        model: ModelType,
        prompt: DecisionAgentPrompt,
        **kwargs,
    ):
        self.model = Model(
            model=model,
            **kwargs
        )
        self.prompt = prompt
    
    def decide(self) -> bool:
        global GENERATED_TOKENS
        # out = self.model.prompt(
        #    self.prompt.get_prompt()
        #)
        out = self.model.prompt_v2(self.prompt.get_prompt_v2())
        logger.mistake_counters["generated_tokens"] += self.model.last_generated_tokens
        # out=out.split('<token>')[1]
        
        reg = r'"answer":\s*(true|false)'
        m = re.search(reg, out)
        
        if m:
            answer = m.group(1)
            return answer == "true"
        logger.mistake_counters["type_1"] += 1
        raise Exception("Could not parse answer")

class FunctionAgent:
    def __init__(
        self,
        model: ModelType,
        prompt: FunctionAgentPrompt,
        **kwargs,
    ):
        self.model = Model(
            model=model,
            **kwargs,
        )
        self.prompt = prompt
    
    def get_next_function(self) -> Dict[str, Any]:
        #out = self.model.prompt(
        #    self.prompt.get_prompt()
        #)
        out = self.model.prompt_v2(self.prompt.get_prompt_v2())
        logger.mistake_counters["generated_tokens"] += self.model.last_generated_tokens
        #out=out.split('<token>')[-1]
        
        reg = re.compile(
            r'```json\s*'        # opening fence + optional space
            r'(\{[\s\S]*?\})'    # capture “{ … }” (non-greedy, across newlines)
            r'\s*```',           # closing fence
            re.DOTALL
        )
        # reg = r'json\n(\s*\{\s*"type":\s*"function_call".*?\n\s*\})\n'
        # reg = r'json\n(\s*\{\s*"type":\s*"function_call".*?\})\n'
        matches = re.findall(reg, out)

        if matches:
            if len(matches) > 1:
                print("[CORE]: MORE THAN ONE OUTPUT JSON")
                logger.mistake_counters["type_1"] += 1
                # raise Exception("More than one function call found")
            
            check_chars = ['{', '}', ':', '[', ']', ',', ' ']
            last_function_call = matches[-1]
            t = ''
            
            for index, c in enumerate(last_function_call):
                if c != "'":
                    t += c
                    continue

                left = last_function_call[index-1]
                right = last_function_call[index+1]

                if left in check_chars or right in check_chars:
                    t += '"'
                    continue

                t += "'"
            last_function_call = t

            print(f"Last function call: {last_function_call}")
            
            try:
                try:
                    return json.loads(last_function_call)
                except json.decoder.JSONDecodeError as e:
                    return json.loads(last_function_call+'\n}')
            except json.decoder.JSONDecodeError as e:
                print(f'Error: {repr(e)}')
                print('[CORE]: INVALID JSON')
                logger.mistake_counters["type_2"] += 1
                raise e
        
        print("[CORE]: NOT FOLLOWING SYSTEM PROMPT FORMAT")
        logger.mistake_counters["type_1"] += 1
        raise Exception("Could not parse answer")

@tool()
def search_restaurant(location: str, cuisine: str, budget: str = "medium") -> List[str]:
    """
    Get a list of the names of restaurants around the location, the cuisine and the budget provided.
    
    :param location: the location to search restaurants at
    :param cuisine: cuisine of the restaurants to search for
    :param budget: budget of the restaurants to search for
    
    :return: The names of the restaurants found
    """
    return ['Italiano', 'Frisco', 'Amar\'e']

@tool()
def save_restaurant_names(names: List[str]) -> None:
    """
    Saves restaurant names in database.
    
    :param names: names of the restaurants to save to the db.
    """
    return { 'message': 'restaurants saved succesfully' }

if __name__ == '__main__':
    model = ModelType.DEEPSEEK_LLAMA_8B
    user_prompt = "I am looking for italian restaurants in Athens. I have a high budget. I want to save the restaurant names to a database."
    
    decision_prompt = DecisionAgentPrompt(
        function_definitions=[
            search_restaurant.definition,
            save_restaurant_names.definition,
        ],
        user_prompt=user_prompt,
    )
    
    function_prompt = FunctionAgentPrompt(
        function_definitions=[
            search_restaurant.definition,
            save_restaurant_names.definition,
        ],
        user_prompt=user_prompt,
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
        except json.decoder.JSONDecodeError as e:
            print(f'Error: {repr(e)}')
            print(f'Failed to parse function')
            break
        
        print(function)
        
        try:
            current_module = __import__(__name__)
            resp = getattr(current_module, function["function_name"])(**function["arguments"])
        except Exception as e:
            print(f'Error: {repr(e)}')
            print('Failed to call function')
            break
        
        fc = FunctionCalled(
            name=function["function_name"],
            arguments=function["arguments"],
            response=resp,
        )
        
        decision_prompt.function_called(fc)
        function_prompt.function_called(fc)
        
        if decision_agent.decide(): break
        
    
    print(f'Sequence: {decision_prompt.functions_called}')
    # print(agent.decide())
    # print(agent.get_next_function())
