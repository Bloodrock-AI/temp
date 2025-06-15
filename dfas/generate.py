import os
import re
import ast
import json
from typing import Any

from dfa import FunctionCall, FunctionArgument, Node, Transition

def serialize_transition(t: Any) -> dict:
    return {
        "symbols": t.symbols,
        "from": t._from.name,
        "to": t._to.name,
    }

def serialize_node(n: Any) -> dict:
    return {
        "name": n.name,
        "is_final": getattr(n, "is_final", False),
        "transitions": [serialize_transition(t) for t in getattr(n, "transitions", [])],
    }

def serialize_function_call(fc: Any) -> dict:
    return {
        "name": fc.name,
        "arguments": {
            k: {
                "name": v.name,
                "value": v.value,
                "excluded_values": v.excluded_values,
                "type": v.type,
            }
            for k, v in fc.arguments.items()
        },
    }

def parse_function_call_strings(call_strings):
    result = []
    for call in call_strings:
        match = re.match(r"(\w+)\((.*)\)", call)
        if not match:
            continue
        name, args_str = match.groups()
        if args_str.strip():
            # Replace key= with 'key': for each argument
            args_str_fixed = re.sub(r"(\w+)\s*=", r"'\1':", args_str)
            args_dict = ast.literal_eval("{" + args_str_fixed + "}")
        else:
            args_dict = {}
        result.append({
            "name": name,
            "arguments": args_dict
        })
    return result

tests = [
    {
        "content": "Move 'final_report.pdf' within document directory to 'temp' directory in document. Make sure to create the directory",
        "expected_sequence": [
            {
                "name": "cd",
                "arguments": {"folder": "document"}
            },
            {
                "name": "mkdir",
                "arguments": {"dir_name": "temp"}
            },
            {
                "name": "mv",
                "arguments": {"source": "final_report.pdf", "destination": "temp"}
            }
        ],
        "world": [
            {"name": "cat", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Display the contents of a file of any extension from currrent directory.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "The name of the file from current directory to display. No path is allowed. "}}, "required": ["file_name"]}, "response": {"type": "dict", "properties": {"file_content": {"type": "string", "description": "The content of the file."}}}},
            {"name": "cd", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Change the current working directory to the specified folder.", "parameters": {"type": "dict", "properties": {"folder": {"type": "string", "description": "The folder of the directory to change to. You can only change one folder at a time. "}}, "required": ["folder"]}, "response": {"type": "dict", "properties": {"current_working_directory": {"type": "string", "description": "The new current working directory path."}}}},
            {"name": "cp", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Copy a file or directory from one location to another.  If the destination is a directory, the source file or directory will be copied into the destination directory.  Both source and destination must be local to the current directory.", "parameters": {"type": "dict", "properties": {"source": {"type": "string", "description": "The name of the file or directory to copy."}, "destination": {"type": "string", "description": "The destination name to copy the file or directory to. If the destination is a directory, the source will be copied into this directory. No file paths allowed. "}}, "required": ["source", "destination"]}, "response": {"type": "dict", "properties": {"result": {"type": "string", "description": "The result of the copy operation or an error message if the operation fails."}}}},
            {"name": "diff", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Compare two files of any extension line by line at the current directory.", "parameters": {"type": "dict", "properties": {"file_name1": {"type": "string", "description": "The name of the first file in current directory."}, "file_name2": {"type": "string", "description": "The name of the second file in current directorry. "}}, "required": ["file_name1", "file_name2"]}, "response": {"type": "dict", "properties": {"diff_lines": {"type": "string", "description": "The differences between the two files."}}}},
            {"name": "du", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Estimate the disk usage of a directory and its contents.", "parameters": {"type": "dict", "properties": {"human_readable": {"type": "boolean", "description": "If True, returns the size in human-readable format (e.g., KB, MB). ", "default": False}}, "required": []}, "response": {"type": "dict", "properties": {"disk_usage": {"type": "string", "description": "The estimated disk usage."}}}},
            {"name": "echo", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Write content to a file at current directory or display it in the terminal.", "parameters": {"type": "dict", "properties": {"content": {"type": "string", "description": "The content to write or display."}, "file_name": {"type": "string", "description": "The name of the file at current directory to write the content to. Defaults to None. ", "default": "None"}}, "required": ["content"]}, "response": {"type": "dict", "properties": {"terminal_output": {"type": "string", "description": "The content if no file name is provided, or None if written to file."}}}},
            {"name": "find", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Find any file or directories under specific path that contain name in its file name.  This method searches for files of any extension and directories within a specified path that match the given name. If no name is provided, it returns all files and directories in the specified path and its subdirectories. Note: This method performs a recursive search through all subdirectories of the given path.", "parameters": {"type": "dict", "properties": {"path": {"type": "string", "description": "The directory path to start the search. Defaults to the current directory (\".\").", "default": "."}, "name": {"type": "string", "description": "The name of the file or directory to search for. If None, all items are returned. ", "default": "None"}}, "required": []}, "response": {"type": "dict", "properties": {"matches": {"type": "array", "description": "A list of matching file and directory paths relative to the given path.", "items": {"type": "string"}}}}},
            {"name": "grep", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Search for lines in a file of any extension at current directory that contain the specified pattern.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "The name of the file to search. No path is allowed and you can only perform on file at local directory."}, "pattern": {"type": "string", "description": "The pattern to search for. "}}, "required": ["file_name", "pattern"]}, "response": {"type": "dict", "properties": {"matching_lines": {"type": "array", "description": "Lines that match the pattern.", "items": {"type": "string"}}}}},
            {"name": "ls",  "type": "R","description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: List the contents of the current directory.", "parameters": {"type": "dict", "properties": {"a": {"type": "boolean", "description": "Show hidden files and directories. Defaults to False. ", "default": False}}, "required": []}, "response": {"type": "dict", "properties": {"current_directory_content": {"type": "array", "description": "A list of the contents of the specified directory.", "items": {"type": "string"}}}}},
            {"name": "mkdir", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Create a new directory in the current directory.", "parameters": {"type": "dict", "properties": {"dir_name": {"type": "string", "description": "The name of the new directory at current directory. You can only create directory at current directory."}}, "required": ["dir_name"]}, "response": {"type": "dict", "properties": {}}},
            {"name": "mv", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Move a file or directory from one location to another. so", "parameters": {"type": "dict", "properties": {"source": {"type": "string", "description": "Source name of the file or directory to move. Source must be local to the current directory."}, "destination": {"type": "string", "description": "The destination name to move the file or directory to. Destination must be local to the current directory and cannot be a path. If destination is not an existing directory like when renaming something, destination is the new file name. "}}, "required": ["source", "destination"]}, "response": {"type": "dict", "properties": {"result": {"type": "string", "description": "The result of the move operation."}}}},
            {"name": "pwd", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Return the current working directory path.", "parameters": {"type": "dict", "properties": {}, "required": []}, "response": {"type": "dict", "properties": {"current_working_directory": {"type": "string", "description": "The current working directory path."}}}},
            {"name": "rm", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Remove a file or directory.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "The name of the file or directory to remove. "}}, "required": ["file_name"]}, "response": {"type": "dict", "properties": {"result": {"type": "string", "description": "The result of the remove operation."}}}},
            {"name": "rmdir", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Remove a directory at current directory.", "parameters": {"type": "dict", "properties": {"dir_name": {"type": "string", "description": "The name of the directory to remove. Directory must be local to the current directory. "}}, "required": ["dir_name"]}, "response": {"type": "dict", "properties": {"result": {"type": "string", "description": "The result of the remove operation."}}}},
            {"name": "sort", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Sort the contents of a file line by line.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "The name of the file appeared at current directory to sort. "}}, "required": ["file_name"]}, "response": {"type": "dict", "properties": {"sorted_content": {"type": "string", "description": "The sorted content of the file."}}}},
            {"name": "tail", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Display the last part of a file of any extension.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "The name of the file to display. No path is allowed and you can only perform on file at local directory."}, "lines": {"type": "integer", "description": "The number of lines to display from the end of the file. Defaults to 10. ", "default": 10}}, "required": ["file_name"]}, "response": {"type": "dict", "properties": {"last_lines": {"type": "string", "description": "The last part of the file."}}}},
            {"name": "touch", "type": "W", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Create a new file of any extension in the current directory.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "The name of the new file in the current directory. file_name is local to the current directory and does not allow path."}}, "required": ["file_name"]}, "response": {"type": "dict", "properties": {}}},
            {"name": "wc", "type": "R", "description": "This tool belongs to the Gorilla file system. It is a simple file system that allows users to perform basic file operations such as navigating directories, creating files and directories, reading and writing to files, etc. Tool description: Count the number of lines, words, and characters in a file of any extension from current directory.", "parameters": {"type": "dict", "properties": {"file_name": {"type": "string", "description": "Name of the file of current directory to perform wc operation on."}, "mode": {"type": "string", "description": "Mode of operation ('l' for lines, 'w' for words, 'c' for characters). ", "default": "l"}}, "required": ["file_name"]}, "response": {"type": "dict", "properties": {"count": {"type": "integer", "description": "The count of the number of lines, words, or characters in the file."}, "type": {"type": "string", "description": "The type of unit we are counting. [Enum]: [\"lines\", \"words\", \"characters\"]"}}}}
        ]
    }
]

def get_function_type(function_name, world):
    """Returns the type of the function based on its name."""
    for function in world:
        if function["name"] == function_name:
            return function["type"]
    return None

def symbol_generator():
    """Yields symbols: 'A', 'B', ..., 'Z', 'AA', 'AB', ..."""
    i = 0
    while True:
        s = ""
        n = i
        while True:
            s = chr(ord('A') + (n % 26)) + s
            n = n // 26 - 1
            if n < 0:
                break
        yield s
        i += 1

def create_alphabet(expected_sequence, world):
    gen = symbol_generator()
    used_functions = {function["name"]: function for function in expected_sequence}
    excluded_values = {}
    
    alphabet = {}
    
    # creating alphabet
    for function in world:
        # if the function is in the expected sequence, create the specific versions
        if function["name"] in used_functions:
            alphabet[next(gen)] = FunctionCall(
                function["name"],
                arguments={
                    arg_name: FunctionArgument(
                        name=arg_name,
                        value=used_functions[function["name"]]["arguments"].get(arg_name, None),
                        excluded_values=None,
                        type=arg_info["type"]
                    )
                    for arg_name, arg_info in function["parameters"]["properties"].items()
                }
            )
            
            if function["name"] not in excluded_values:
                excluded_values[function["name"]] = {}
            
            for arg_name, arg_info in function["parameters"]["properties"].items():
                value = used_functions[function["name"]]["arguments"].get(arg_name, None)
                if arg_name not in excluded_values[function["name"]]:
                    excluded_values[function["name"]][arg_name] = []
                excluded_values[function["name"]][arg_name].append(value)
    
    # creating generals
    for function in world:
        alphabet[next(gen)] = FunctionCall(
            function["name"],
            arguments={
                arg_name: FunctionArgument(
                    name=arg_name,
                    value=None,
                    excluded_values=excluded_values[function["name"]][arg_name] if function["name"] in excluded_values and arg_name in excluded_values[function["name"]] else [],
                    type=arg_info["type"]
                )
                for arg_name, arg_info in function["parameters"]["properties"].items()
            }
        )
            
    # print("Alphabet generated:", alphabet)
    # print("Excluded values generated:", excluded_values)
    
    return alphabet

def generate_dfa(expected_sequence, alphabet, world):
    alphabet = create_alphabet(expected_sequence, world)
    used_functions = {function["name"]: function for function in expected_sequence}

    nodes = []
    nodes.append(
        Node("G0")
    )
    for index, fc in enumerate(expected_sequence):
        nodes.append(
            Node(f"G{index + 1}")
        )
    nodes[-1].is_final = True

    for index, node in enumerate(nodes):
        node.transitions = []
        expected_fc = expected_sequence[index] if index < len(expected_sequence) else None
        self_loop_transition = Transition(
            symbols=[], _from=node, _to=node  # self-loop transition
        )

        for i, function_call in enumerate(alphabet.items()):
            symbol, fc = function_call
            check = expected_fc is not None and fc.name == expected_fc["name"]
            
            # evaluate what happens in this state if the function is called
            if check:
                # check if the arguments match
                if all(
                    expected_fc["arguments"].get(arg_name) == fc.arguments[arg_name].value
                    for arg_name in expected_fc["arguments"]
                ):
                    node.transitions.append(
                        Transition(
                            symbols=[symbol],
                            _from=node,
                            _to=nodes[index + 1] if index + 1 < len(nodes) else node  # stay in the same node if it's the last one
                        )
                    )
                    continue
            
            # if the function is not the expected one, we need to self-loop if it
            # is a Read function
            if get_function_type(fc.name, world) == "R":
                self_loop_transition.symbols.append(symbol)
            
            # if the last iteration then append the self-loop transition
            if i == len(alphabet) - 1:
                node.transitions.append(self_loop_transition)
    
    return nodes

# alphabet = create_alphabet(tests[0]["expected_sequence"], tests[0]["world"])
# print({k: serialize_function_call(fc) for k, fc in alphabet.items()})
# # write to file
# with open("alphabet.json", "w") as f:
#     import json
#     json.dump({k: serialize_function_call(fc) for k, fc in alphabet.items()}, f, indent=4)

# dfa = generate_dfa(tests[0]["expected_sequence"], alphabet, tests[0]["world"])
# print([serialize_node(node) for node in dfa])
# # write to file
# with open("dfa.json", "w") as f:
#     json.dump([serialize_node(node) for node in dfa], f, indent=4)

if __name__ == "__main__":
    # load all worlds
    worlds = {}
    for filename in os.listdir("../bfcl_dataset/worlds"):
        if filename.endswith(".json"):
            with open(os.path.join("../bfcl_dataset/worlds", filename), "r") as f:
                world = json.load(f)
            
            # remove the .json extension from the filename
            filename = filename[:-5]
            worlds[filename] = world
    
    # load dataset
    with open("../bfcl_dataset/bfcl_unified_dataset_list.json", "r") as f:
        dataset = json.load(f)
    
    # iterate over dataset
    problematic_ids = []
    for item in dataset:
        world = worlds.get(item["world"])
        expected_sequence = parse_function_call_strings(item["expected_sequences"][0])
        # print(expected_sequence)
        try:
            alphabet = create_alphabet(expected_sequence, world)
        except AttributeError as e:
            print(f"Error creating alphabet for {item['world']} - {item['prompt_id']}: {e}")
            problematic_ids.append(item["prompt_id"])
            continue
        dfa = generate_dfa(expected_sequence, alphabet, world)
        
        # serialize dfa
        serialized_dfa = [serialize_node(node) for node in dfa]
        serialized_alphabet = {k: serialize_function_call(fc) for k, fc in alphabet.items()}
        # write to file
        output_filename = f"{item['world']}_{item['prompt_id']}.json"
        with open(os.path.join("output", output_filename), "w") as f:
            json.dump({
                "dfa": serialized_dfa,
                "alphabet": serialized_alphabet,
                "expected_sequence": expected_sequence
            }, f, indent=4)
        print(f"Generated DFA for {item['world']} - {item['prompt_id']} saved to {output_filename}")
        
    if problematic_ids:
        print("Problematic IDs:", problematic_ids)