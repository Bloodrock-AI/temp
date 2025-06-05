from dfas.dfa import Node, Transition, Prompt, FunctionCall, FunctionArgument


# Prompt 5
G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3")
G4 = Node("G4")
G5 = Node("G5")
G6 = Node("G6", is_final=True)

alphabet: List[str, FunctionCall] = {
    "A": FunctionCall(
        'set_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value="max-connections",
                excluded_values=None,
                type="str"
            ),
            "value": FunctionArgument(
                name="value",
                value="100",
                excluded_values=None,
                type="string"
            ),
            "category": FunctionArgument(
                name="category",
                value="network",
                excluded_values=None,
                type="str"
            ),
            "timestamp": FunctionArgument(
                name="timestamp",
                value="2015-03-14T10:00:00",
                excluded_values=None,
                type="str"
            ),
        },
    ),
    "A'": FunctionCall(
        'set_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value="log-level",
                excluded_values=None,
                type="str"
            ),
            "value": FunctionArgument(
                name="value",
                value="debug",
                excluded_values=None,
                type="string"
            ),
            "category": FunctionArgument(
                name="category",
                value="network",
                excluded_values=None,
                type="str"
            ),
            "timestamp": FunctionArgument(
                name="timestamp",
                value="2015-03-14T10:00:00",
                excluded_values=None,
                type="str"
            ),
        },
    ),
    "A''": FunctionCall(
        'set_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value=None,
                excluded_values=["max-connections", "log-level"],
                type="str"
            ),
            "value": FunctionArgument(
                name="value",
                value=None,
                excluded_values=["100", "debug"],
                type="string"
            ),
            "category": FunctionArgument(
                name="category",
                value=None,
                excluded_values=["network"],
                type="str"
            ),
            "timestamp": FunctionArgument(
                name="timestamp",
                value=None,
                excluded_values=["2015-03-14T10:00:00"],
                type="str"
            ),
        },
    ),
    "B": FunctionCall(
        'print_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value="max-connections",
                excluded_values=None,
                type="str"
            ),
        },
    ),
    "B'": FunctionCall(
        'print_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value="log-level",
                excluded_values=None,
                type="str"
            ),
        },
    ),
    "B''": FunctionCall(
        'print_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value=None,
                excluded_values=["max-connections", "log-level"],
                type="str"
            ),
        },
    ),
    "C": FunctionCall(
        'update_config',
        arguments={
            "key": FunctionArgument(
                name="key",
                value=None,
                excluded_values=[],
                type="str"
            ),
            "new_value": FunctionArgument(
                name="new_value",
                value=None,
                excluded_values=[],
                type="str"
            ),
            "category": FunctionArgument(
                name="category",
                value=None,
                excluded_values=[],
                type="str"
            ),
            "timestamp": FunctionArgument(
                name="timestamp",
                value=None,
                excluded_values=[],
                type="str"
            ),
        },
    ),
    "D": FunctionCall(
        'delete_config',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=None,
                excluded_values=[],
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=None,
                excluded_values=[],
                type="int"
            ),
        },
    ),
    "D": FunctionCall(
        'divide_numbers',
        arguments={
            "key": FunctionArgument(
                name="key",
                value=None,
                excluded_values=[],
                type="str"
            ),
        },
    ),
}

G0.transitions = [
    Transition(symbols=[
        "B", "B'", "B''",
    ], _from=G0, _to=G0),
    Transition(symbols=[
        "A",
    ], _from=G0, _to=G1),
    Transition(symbols=[
        "A'",
    ], _from=G0, _to=G2),
]
G1.transitions = [
    Transition(symbols=[
        "B", "B'", "B''",
    ], _from=G1, _to=G1),
    Transition(symbols=[
        "A'",
    ], _from=G1, _to=G3),
]
G2.transitions = [
    Transition(symbols=[
        "B", "B'", "B''",
    ], _from=G2, _to=G2),
    Transition(symbols=[
        "A",
    ], _from=G2, _to=G3),
]
G3.transitions = [
    Transition(symbols=[
        "B'", "B''",
    ], _from=G3, _to=G3),
    Transition(symbols=[
        "B",
    ], _from=G3, _to=G5),
    Transition(symbols=[
        "B'",
    ], _from=G3, _to=G4),   
]
G4.transitions = [
    Transition(symbols=[
        "B'", "B''",
    ], _from=G4, _to=G4),
    Transition(symbols=[
        "B",
    ], _from=G4, _to=G6),
]
G5.transitions = [
    Transition(symbols=[
        "B", "B''",
    ], _from=G5, _to=G5),
    Transition(symbols=[
        "B'",
    ], _from=G5, _to=G6),
]
G6.transitions = [
    Transition(symbols=[
        "B", "B'", "B''",
    ], _from=G6, _to=G6),
]