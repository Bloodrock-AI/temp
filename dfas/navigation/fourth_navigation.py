from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3")
G4 = Node(name="G4", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="is_within_bounds",
        arguments={
            "position": FunctionArgument(
                name="position",
                value=None,
                excluded_values=None,
                type="tuple[int,int]",
            ),
        },
    ),
    "B": FunctionCall(
        name="move_up",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=0,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "B'": FunctionCall(
        name="move_up",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=2,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "B''": FunctionCall(
        name="move_up",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=None,
                excluded_values=[0, 2],
                type="int",
            ),
        },
    ),
    "C": FunctionCall(
        name="move_down",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=0,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "C'": FunctionCall(
        name="move_down",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=2,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "C''": FunctionCall(
        name="move_down",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=None,
                excluded_values=[0, 2],
                type="int",
            ),
        },
    ),
    "D": FunctionCall(
        name="move_left",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=0,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "D'": FunctionCall(
        name="move_left",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=2,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "D''": FunctionCall(
        name="move_left",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=None,
                excluded_values=[0, 2],
                type="int",
            ),
        },
    ),
    "E": FunctionCall(
        name="move_right",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=0,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "E'": FunctionCall(
        name="move_right",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=2,
                excluded_values=None,
                type="int",
            ),
        },
    ),
    "E''": FunctionCall(
        name="move_right",
        arguments={
            "steps": FunctionArgument(
                name="steps",
                value=None,
                excluded_values=[0, 2],
                type="int",
            ),
        },
    ),
    "F": FunctionCall(
        name="get_player_position",
        arguments={},
    ),
    "G": FunctionCall(
        name="reset_position",
        arguments={},
    ),
}

G0.transitions = [
    Transition(symbols=["A", "F", "G", "B", "C", "D", "E"], _from=G0, _to=G0),
    Transition(symbols=["E'"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["A", "F", "B", "C", "D", "E"], _from=G1, _to=G1),
    Transition(symbols=["C'"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["A", "F", "B", "C", "D", "E"], _from=G2, _to=G2),
    Transition(symbols=["D'"], _from=G2, _to=G3),
]

G3.transitions = [
    Transition(symbols=["A", "F", "B", "C", "D", "E"], _from=G3, _to=G3),
    Transition(symbols=["B'"], _from=G3, _to=G4),
]

G4.transitions = [
    Transition(symbols=["A", "F", "G", "B", "C", "D", "E"], _from=G4, _to=G4),
]
