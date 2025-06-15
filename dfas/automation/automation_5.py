from dfas.dfa import Node, Transition, Prompt, FunctionCall, FunctionArgument


G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3")
G4 = Node("G4")
G5 = Node("G5")
G6 = Node("G6")
G7 = Node("G7", is_final=True)

alphabet: dict[str, FunctionCall] = {
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
                value=30,
                excluded_values=None,
                type="int"
            ),
        }
    ),
    "G": FunctionCall(
        'set_thermostat',
        arguments={
            "temperature": FunctionArgument(
                name="temperature",
                value=None,
                excluded_values=[30],
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
    Transition(symbols=["E"], _from=G0, _to=G1),
    Transition(symbols=["H"], _from=G0, _to=G0),
]
G1.transitions = [
    Transition(symbols=["C"], _from=G1, _to=G2),
    Transition(symbols=["H"], _from=G1, _to=G1),
]
G2.transitions = [
    Transition(symbols=["B"], _from=G2, _to=G3),
    Transition(symbols=["H"], _from=G2, _to=G2),
]
G3.transitions = [
    Transition(symbols=["G"], _from=G3, _to=G4),
    Transition(symbols=["H"], _from=G3, _to=G3),
]
G4.transitions = [
    Transition(symbols=["F"], _from=G4, _to=G5),
    Transition(symbols=["H"], _from=G4, _to=G4),
]
G5.transitions = [
    Transition(symbols=["D"], _from=G5, _to=G6),
    Transition(symbols=["H"], _from=G5, _to=G5),
]
G6.transitions = [
    Transition(symbols=["A"], _from=G6, _to=G7),
    Transition(symbols=["H"], _from=G6, _to=G6),
]
G7.transitions = [
    Transition(symbols=["H"], _from=G7, _to=G7),
]