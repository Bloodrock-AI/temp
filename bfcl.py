import re
import ast
import json
from worlds import RoboticArm, CRUD, Communication
from deepdiff import DeepDiff
from pprint import pprint

from typing import Dict, Any, List

def is_subsequence(seq1: List[Dict[str, Any]], seq2: List[Dict[str, Any]]) -> bool:
    """
    Check if seq1 is a subsequence of seq2.
    
    :param seq1: List of dictionaries representing the first sequence.
    :param seq2: List of dictionaries representing the second sequence.
    :return: True if seq1 is a subsequence of seq2, False otherwise.
    """
    it = iter(seq1)
    return all(item in seq2 for item in it)

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
            "function_name": name,
            "arguments": args_dict
        })
    return result

def evaluate_bfcl(world, prompt_id, actual_state, function_sequence):
    
    # find prompt expected sequences
    prompt = next((p for p in world.prompts if p["prompt_id"] == prompt_id), None)
    if not prompt:
        raise ValueError(f'Prompt with ID {prompt_id} not found in world prompts.')

    expected_sequences = prompt["expected_sequences"]
    print(f'Expected sequences: {[parse_function_call_strings(seq) for seq in expected_sequences]}')
    
    world.reset_world_state()
    
    setup_functions = prompt.get("setup_functions", [])
    for func in setup_functions:
        eval(f"world.{func}")
    
    for func in expected_sequences[0]:
        eval(f"world.{func}")
    
    state_eval, diff = state_based_eval_bfcl(world.world_state, actual_state)
    
    reponse_eval = response_based_eval_bfcl(
        expected_sequences,
        function_sequence
    )
    
    return {
        "state_based_evaluation": state_eval,
        "state_diff": diff,
        "response_based_evaluation": reponse_eval,
    }
    

def state_based_eval_bfcl(expected_state: Dict[str, Any], actual_state: Dict[str, Any]) -> bool:
    diff = DeepDiff(expected_state, actual_state, ignore_order=True)
    return diff == {}, diff

def response_based_eval_bfcl(expected_sequences: List[List[str]], function_sequence: List[str]) -> bool:
    # parse expected sequences
    expected_sequences = [parse_function_call_strings(seq) for seq in expected_sequences]
    
    # remove response from function_sequence
    function_sequence = [
        {
            "function_name": func["function_name"],
            "arguments": json.loads(func["arguments"]) if type(func["arguments"]) == str else func["arguments"],
        }
        for func in function_sequence
    ]
    
    # print(f"Comparing function sequence: {function_sequence} with expected sequences: {expected_sequences}")

    for expected in expected_sequences:
        if is_subsequence(expected, function_sequence):
            return True
    return False

if __name__ == "__main__":
    # world = RoboticArm()
    # for func in world.prompts[0]["expected_sequences"][0]:
    #     eval(f"world.{func}")

    # print(evaluate_bfcl(RoboticArm(), "robotic_arm_1", world.world_state.copy(), ))
    
    test_state = {
            "pose": {
                "x": 0.5,
                "y": 0.0,
                "z": 0.4,
                "yaw": 0.0
            },
            "home_pose": {
                "x": 0.5,
                "y": 0.0,
                "z": 0.4,
                "yaw": 0.0
            },
            "gripper_closed": False,
            "holding_object": None,
            "current_load": 0.0,
            "load_capacity": 5.0,
            "safety_mode": False,
            "workspace_bounds": {
                "xmin": 0.1,
                "xmax": 1.2,
                "ymin": -0.5,
                "ymax": 0.5,
                "zmin": 0.05,
                "zmax": 0.6
            },
            "no_go_xy": [
                {
                    "xmin": 0.7,
                    "xmax": 0.85,
                    "ymin": -0.1,
                    "ymax": 0.1
                }
            ],
            "pick_tolerance_xy": 0.02,
            "pick_tolerance_z": 0.01,
            "place_tolerance_xy": 0.02,
            "place_tolerance_z": 0.01,
            "stations": {
                "assembly_table": {
                    "x": 0.95,
                    "y": 0.2,
                    "z": 0.1,
                    "yaw": 0.0
                },
                "quality_control": {
                    "x": 1.05,
                    "y": -0.2,
                    "z": 0.1,
                    "yaw": 0.0
                },
                "packaging_area": {
                    "x": 0.8,
                    "y": 0.35,
                    "z": 0.1,
                    "yaw": 0.0
                }
            },
            "objects": {
                "box_small": {
                    "weight": 2.0,
                    "pose": {
                        "x": 0.95,
                        "y": 0.2,
                        "z": 0.1
                    }
                },
                "box_large": {
                    "weight": 4.0,
                    "pose": {
                        "x": 0.8,
                        "y": 0.35,
                        "z": 0.1
                    }
                },
                "gear_A": {
                    "weight": 1.0,
                    "pose": {
                        "x": 0.8,
                        "y": 0.35,
                        "z": 0.1
                    }
                },
                "panel_X": {
                    "weight": 3.0,
                    "pose": {
                        "x": 0.95,
                        "y": 0.2,
                        "z": 0.1
                    }
                }
            }
        }
    
    # pprint(evaluate_bfcl(RoboticArm(), "robotic_arm_1", test_state))
    
    # print(parse_function_call_strings(world.prompts[0]["expected_sequences"][0]))

    # world = CRUD()
    # for func in world.prompts[0]["expected_sequences"][0]:
    #     eval(f"world.{func}")
    
    # print(evaluate_bfcl(world, "crud_1", world.world_state.copy(), [{'function_name': 'add_user', 'arguments': '{"name": "Alice", "age": 25}', 'response': 'Alice_id'}, {'function_name': 'list_users', 'arguments': '{}', 'response': [{'id': 'Alice_id', 'name': 'Alice', 'age': 25, 'email': None}]}]))

    world = Communication()
    for func in world.prompts[0]["expected_sequences"][0]:
        eval(f"world.{func}")

    print(evaluate_bfcl(world, "communication_1", world.world_state.copy(), [{'function_name': 'send_message', 'arguments': '{"sender": "Alice", "recipient": "Bob", "content": "Urgent meeting at 3 PM", "priority": "high"}', 'response': None}, {'function_name': 'send_message', 'arguments': '{"sender": "Alice", "recipient": "Bob", "content": "Urgent meeting at 3 PM", "priority": "high"}', 'response': None}, {'function_name': 'send_message', 'arguments': '{"sender": "Alice", "recipient": "Bob", "content": "Urgent meeting at 3 PM", "priority": "high"}', 'response': None}]))