from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

# Nodes
G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2", is_final=True)

# Alphabet
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
            "key":       FunctionArgument(name="key",       value=None, excluded_values=[], type="str"),
            "new_value": FunctionArgument(name="new_value", value=None, excluded_values=[], type="str"),
            "category":  FunctionArgument(name="category",  value=None, excluded_values=[], type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None, excluded_values=[], type="str"),
        },
    ),
    "D": FunctionCall(
        name="delete_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=None, type="str"),
        },
    ),
}

# Transitions
G0.transitions = [
    Transition(symbols=["B"],  _from=G0, _to=G1),
    Transition(symbols=["B'"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["A"],  _from=G1, _to=G2),
    Transition(symbols=["B"],  _from=G1, _to=G1),
    Transition(symbols=["B'"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["B"],  _from=G2, _to=G2),
    Transition(symbols=["B'"], _from=G2, _to=G2),
]
