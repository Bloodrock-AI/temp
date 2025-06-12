from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument
from build_json_dataset import serialize_function_call

import sys
import re
import ast
import json
from typing import Optional, Dict, List

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="set_config",
        arguments={
            "key":        FunctionArgument(name="key",        value="theme",      excluded_values=None,          type="str"),
            "value":      FunctionArgument(name="value",      value="light mode", excluded_values=None,          type="str"),
            "category":   FunctionArgument(name="category",   value="UI",         excluded_values=None,          type="str"),
            "timestamp":  FunctionArgument(name="timestamp",  value=None,         excluded_values=None,          type="str"),
        },
    ),
    "A'": FunctionCall(
        name="set_config",
        arguments={
            "key":        FunctionArgument(name="key",        value=None,         excluded_values=["theme"],      type="str"),
            "value":      FunctionArgument(name="value",      value=None,         excluded_values=["light mode"], type="str"),
            "category":   FunctionArgument(name="category",   value=None,         excluded_values=["UI"],         type="str"),
            "timestamp":  FunctionArgument(name="timestamp",  value=None,         excluded_values=None,           type="str"),
        },
    ),
    "B": FunctionCall(
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value="theme", excluded_values=None, type="str"),
        },
    ),
    "B'": FunctionCall(
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=["theme"], type="str"),
        },
    ),
    "C": FunctionCall(
        name="update_config",
        arguments={
            "key":       FunctionArgument(name="key",       value=None, excluded_values=None, type="str"),
            "new_value": FunctionArgument(name="new_value", value=None, excluded_values=None, type="str"),
            "category":  FunctionArgument(name="category",  value=None, excluded_values=None, type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None, excluded_values=None, type="str"),
        },
    ),
    "D": FunctionCall(
        name="delete_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=None, type="str"),
        },
    ),
}

def fix_response_quotes(s):
    # Find the response value and escape inner quotes
    
    def replacer(match):
        before = match.group(1)
        content = match.group(2)
        print(f"Original content: {content}")
        print(f"Before content: {before}")
        # Escape quotes inside the content
        fixed_content = content.replace('"', "'")
        return f'{before}"{fixed_content}"'
    return re.sub(r'("response":)"(.*)"(\s*})', replacer, s, flags=re.DOTALL)

string = '''
[FunctionCalled(name='set_config', arguments={'key': 'theme', 'value': 'light mode', 'category': 'UI'}, response=\"Configuration 'theme' set to 'light mode' in category 'general'.\"),FunctionCalled(name='set_config', arguments={'key': 'theme', 'value': 'light mode'}, response=\"Configuration 'theme' set to "light mode" in category 'general'.\")]
'''

def parse_function_calls_from_string(seq_str: str) -> List[Dict[str, Optional[str]]]:
    """
    Parses a string like the variable `string` in evaluate.py into a list of dicts:
    [
        {"name": ..., "arguments": {...}, "response": ...}
    ]
    """
    out = seq_str.replace("'", "\"").replace("FunctionCalled", '').replace("[", "").replace("]", "").replace("\n", "").replace("=", ":").strip().split("),(")
    for index, s in enumerate(out):
        s = s.strip()
        if s.endswith(")"):
            s = s[:-1]
        if s.startswith("("):
            s = s[1:]
        s = f"{{{s}}}"
        s = re.sub(r'(\w+):', r'"\1":', s)
        s = fix_response_quotes(s)
        s += "}"
        out[index] = s
    return [json.loads(s) for s in out if s.strip()]

alphabet_proc = {
    "set_config": [
        {
            "symbol": "A",
            "arguments": {
                "key":        FunctionArgument(name="key",        value="theme",      excluded_values=None,          type="str"),
                "value":      FunctionArgument(name="value",      value="light mode", excluded_values=None,          type="str"),
                "category":   FunctionArgument(name="category",   value="UI",         excluded_values=None,          type="str"),
                "timestamp":  FunctionArgument(name="timestamp",  value=None,         excluded_values=None,          type="str"),
            },
        },
        {
            "symbol": "A''",     
            "arguments": {
                "key":        FunctionArgument(name="key",        value=None,         excluded_values=["theme"],      type="str"),
                "value":      FunctionArgument(name="value",      value="bruh",         excluded_values=[],           type="str"),
                "category":   FunctionArgument(name="category",   value=None,         excluded_values=["UI"],         type="str"),
                "timestamp":  FunctionArgument(name="timestamp",  value=None,         excluded_values=None,           type="str"),
            },
        },
        {
            "symbol": "A'",     
            "arguments": {
                "key":        FunctionArgument(name="key",        value=None,         excluded_values=["theme"],      type="str"),
                "value":      FunctionArgument(name="value",      value=None,         excluded_values=["light mode"], type="str"),
                "category":   FunctionArgument(name="category",   value=None,         excluded_values=["UI"],         type="str"),
                "timestamp":  FunctionArgument(name="timestamp",  value=None,         excluded_values=None,           type="str"),
            },
        },
    ]
}

function_calls = [
    {
        "name": "set_config",
        "arguments": {
            "key": "theme",
            "value": "light mode",
            "category": "UI",
        },
        "response": "Configuration 'theme' set to 'light mode' in category 'general'."
    },
    {
        "name": "set_config",
        "arguments": {
            "key": "X",
            "value": "X",
            "category": "general",
        },
        "response": "Configuration 'theme' set to 'light mode' in category 'general'."
    },
    {
        "name": "set_config",
        "arguments": {
            "key": "theme",
            "value": "light mode",
            "category": "general",
        },
        "response": "Configuration 'theme' set to 'light mode' in category 'general'."
    },
    {
        "name": "set_config",
        "arguments": {
            "key": "theme",
            "value": "light mode",
        },
        "response": "Configuration 'theme' set to 'light mode' in category 'general'."
    },
]

def fc2symbol(fc, alphabet) -> str:
    
    out_symbol = ""
    
    for symbol in alphabet[fc["name"]]:
        print("--------")
        print(f"Checking symbol: {symbol['symbol']} for function call: {fc['name']}")
        
        try:
            for arg_name, arg in symbol["arguments"].items():
                arg_value = {
                    "value": arg.value,
                    "excluded_values": arg.excluded_values,
                    "type": arg.type
                }
                print(f"Checking argument: {arg_name} with value: {arg_value}")

                if arg_value["value"] is not None:
                    # this argument is required

                    # throws KeyError if argument is not present
                    # throws AssertionError if argument value does not match
                    assert fc["arguments"][arg_name] == arg_value["value"]
                    print(f"Argument {arg_name} matched with value: {arg_value['value']}")
                    out_symbol = symbol["symbol"]
                else:
                    # this argument is not required
                    # check excluded values
                    
                    # if excluded values are None then the value should be None or not present
                    if arg_value["excluded_values"] is None:
                        assert arg_name not in fc["arguments"] or fc["arguments"][arg_name] is None
                        
                        out_symbol = symbol["symbol"]
                        continue
                    
                    if arg_name not in fc["arguments"]:
                        continue
                    
                    # if the argument is not in the excluded values continue
                    if fc["arguments"][arg_name] not in arg_value["excluded_values"]:
                        out_symbol = symbol["symbol"]
                        continue

        except (KeyError, AssertionError):
            out_symbol = ""

        if out_symbol:
            break

    return out_symbol

def convert_alphabet_to_proc(alphabet: dict[str, FunctionCall]) -> dict[str, list[dict]]:
    proc = {}
    for symbol, func_call in alphabet.items():
        name = func_call.name
        entry = {
            "symbol": symbol,
            "arguments": func_call.arguments,
        }
        if name not in proc:
            proc[name] = []
        proc[name].append(entry)
    return proc

# print(fc2symbol(function_calls[2], alphabet_proc))
# for fc in parse_function_calls_from_string(string):
#     print(fc2symbol(fc, alphabet_proc))

def json_to_alphabet(data):
    """
    Convert a JSON representation of an alphabet to a dictionary of FunctionCall objects.
    """
    alphabet = {}
    for symbol, func_call in data.items():
        name = func_call["name"]
        arguments = {k: FunctionArgument(**v) for k, v in func_call["arguments"].items()}
        alphabet[symbol] = FunctionCall(name=name, arguments=arguments)
    return alphabet

def load_world(a):
    out = {
        "prompt_id": a["prompt_id"],
        "alphabet": {},
        "nodes": {}
    }
    
    for node in a["nodes"]:
        out["nodes"][node["name"]] = Node(name=node["name"], is_final=node.get("is_final", False))
    
    out["alphabet"] = json_to_alphabet(a["alphabet"])
    
    # add transitions
    for node in a["nodes"]:
        out["nodes"][node["name"]].transitions = []
        for transition in node.get("transitions", []):
            out["nodes"][node["name"]].transitions.append(Transition(
                symbols=transition["symbols"],
                _from=out["nodes"][transition["from"]],
                _to=out["nodes"][transition["to"]]
            ))

    return out

# def load_results(results)

if __name__ == "__main__":
    dataset_file = sys.argv[1]
    results_file = sys.argv[2]
    
    # Load the dataset (json)
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)
    
    # data = load_dataset(dataset)
    # expected format:
    # {
        # prompt_id: "",
        # alphabet: <alphabet>,
        # nodes: <nodes>, # dfa
    # }
    
    world = load_world(dataset[0])
    print(f"World loaded: {world}")
    
    
    # Load the results (json)
    # with open(results_file, 'r') as f:
    #     results = json.load(f)
        
        
    