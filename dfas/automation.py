from typing import List
from dfas.dfa import Node, Transition, Prompt, FunctionCall, FunctionArgument


# Prompt 1
G0 = Node("G0")
G1 = Node("G1", is_final=True)

alphabet: List[str, FunctionCall] = {
    "A": FunctionCall(
        'turn_on_lights',
        arguments={},
    ),
    "B": FunctionCall(
        'turn_off_lights',
        arguments={},
    ),
    "C": FunctionCall(
        'activate_alarm',
        arguments={},
    ),
    "D": FunctionCall(
        'deactivate_alarm',
        arguments={},
    ),
    "E": FunctionCall(
        'lock_door',
        arguments={},
    ),
    "F": FunctionCall(
        'unlock_door',
        arguments={},
    ),
    "G": FunctionCall(
        'set_thermostat',
        arguments={
            "temperature": FunctionArgument(
                name="temperature",
                value=22,
                excluded_values=None,
                type="int"
            ),
        }
    ),
    "G'": FunctionCall(
        'set_thermostat',
        arguments={
            "temperature": FunctionArgument(
                name="temperature",
                value=None,
                excluded_values=[22],
                type="int"
            ),
        }
    ),
    "H": FunctionCall(
        'print_system_status',
        arguments={},
    ),  
}

G0.transitions = [
    Transition(symbols=["C"], _from=G0, _to=G1),
    Transition(symbols=[
        "B", "E", "G", "D", "H"
    ], _from=G0, _to=G0),
]
G1.transitions = [
    Transition(symbols=[
        "B", "C", "E", "G", "H",
    ], _from=G1, _to=G1),
]