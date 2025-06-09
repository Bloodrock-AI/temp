from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="set_config",
        arguments={
            "key":       FunctionArgument(name="key", value="timeout",     excluded_values=None,          type="str"),
            "value":     FunctionArgument(name="value", value="30 minutes", excluded_values=None,          type="str"),
            "category":  FunctionArgument(name="category", value="security",  excluded_values=None,          type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None,    excluded_values=None,          type="str"),
        },
    ),
    "A'": FunctionCall(
        name="set_config",
        arguments={
            "key":       FunctionArgument(name="key", value="timeout",     excluded_values=None,          type="str"),
            "value":     FunctionArgument(name="value", value="15 minutes", excluded_values=None, type="str"),
            "category":  FunctionArgument(name="category", value="security",  excluded_values=None,          type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None,    excluded_values=None,          type="str"),
        },
    ),
    "A''": FunctionCall(
        name="set_config",
        arguments={
            "key":       FunctionArgument(name="key", value=None,     excluded_values=["timeout"],          type="str"),
            "value":     FunctionArgument(name="value", value=None, excluded_values=["30 minutes", "15 minutes"], type="str"),
            "category":  FunctionArgument(name="category", value=None,  excluded_values=["security"],          type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None,    excluded_values=None,          type="str"),
        },
    ),
    "B": FunctionCall(
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value="timeout", excluded_values=None, type="str"),
        },
    ),
    "B'": FunctionCall(
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=["timeout"], type="str"),
        },
    ),
    "C": FunctionCall(
        name="update_config",
        arguments={
            "key":       FunctionArgument(name="key", value=None, excluded_values=None, type="str"),
            "new_value": FunctionArgument(name="new_value", value=None, excluded_values=None, type="str"),
            "category":  FunctionArgument(name="category", value=None, excluded_values=None, type="str"),
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

G0.transitions = [
    Transition(symbols=["A"],  _from=G0, _to=G1),
    Transition(symbols=["B", "B'"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["A'"], _from=G1, _to=G2),
    Transition(symbols=["B", "B'"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["B"],  _from=G2, _to=G3),
    Transition(symbols=["B'"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["B", "B'"], _from=G3, _to=G3),
]
