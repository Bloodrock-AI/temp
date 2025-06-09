from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="set_config",
        arguments={
            "key": FunctionArgument(name="key", value="theme", excluded_values=None, type="str"),
            "value": FunctionArgument(name="value", value="dark mode", excluded_values=None, type="str"),
            "category": FunctionArgument(name="category", value="UI", excluded_values=None, type="str"),
            "timestamp": FunctionArgument(
                name="timestamp", value="2025-02-12T10:00:00", excluded_values=None, type="str"
            ),
        },
    ),
    "A'": FunctionCall(
        name="set_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=["theme"], type="str"),
            "value": FunctionArgument(name="value", value=None, excluded_values=["dark mode"], type="str"),
            "category": FunctionArgument(name="category", value=None, excluded_values=["UI"], type="str"),
            "timestamp": FunctionArgument(
                name="timestamp", value=None, excluded_values=["2025-02-12T10:00:00"], type="str"
            ),
        },
    ),
    "B": FunctionCall(
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=None, type="str"),
        },
    ),
    "C": FunctionCall(
        name="update_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=None, type="str"),
            "new_value": FunctionArgument(name="new_value", value=None, excluded_values=None, type="str"),
            "category": FunctionArgument(name="category", value=None, excluded_values=None, type="str"),
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
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["B"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["B"], _from=G1, _to=G1),
]
