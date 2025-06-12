from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument
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

string = '''
"[FunctionCalled(name='set_config', arguments={'key': 'theme', 'value': 'light mode'}, response=\"Configuration 'theme' set to 'light mode' in category 'general'.\")]",
'''

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

print(fc2symbol(function_calls[2], alphabet_proc))