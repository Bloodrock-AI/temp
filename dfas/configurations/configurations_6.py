from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3")
G4 = Node(name="G4")
G5 = Node(name="G5", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall( 
        name="set_config",
        arguments={
            "key":       FunctionArgument(name="key",       value=None, excluded_values=None, type="str"),
            "value":     FunctionArgument(name="value",     value=None, excluded_values=None, type="str"),
            "category":  FunctionArgument(name="category",  value=None, excluded_values=None, type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None, excluded_values=None, type="str"),
        },
    ),
    "B": FunctionCall(  
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value="log-level", excluded_values=None, type="str"),
        },
    ),
    "B'": FunctionCall(  
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value="timeout", excluded_values=None, type="str"),
        },
    ),
    "B''": FunctionCall( 
        name="print_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=["log-level", "timeout"], type="str"),
        },
    ),
    "C": FunctionCall( 
        name="update_config",
        arguments={
            "key":       FunctionArgument(name="key",       value="log-level", excluded_values=None, type="str"),
            "new_value": FunctionArgument(name="new_value", value="info",      excluded_values=None, type="str"),
            "category":  FunctionArgument(name="category",  value=None,        excluded_values=None, type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None,        excluded_values=None, type="str"),
        },
    ),
    "C'": FunctionCall( 
        name="update_config",
        arguments={
            "key":       FunctionArgument(name="key",       value=None, excluded_values=["log-level"], type="str"),
            "new_value": FunctionArgument(name="new_value", value=None, excluded_values=["info"], type="str"),
            "category":  FunctionArgument(name="category",  value=None, excluded_values=None, type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None, excluded_values=None, type="str"),
        },
    ),
    "D": FunctionCall( 
        name="delete_config",
        arguments={
            "key": FunctionArgument(name="key", value="max-connections", excluded_values=None, type="str"),
        },
    ),
    "D'": FunctionCall(  
        name="delete_config",
        arguments={
            "key": FunctionArgument(name="key", value=None, excluded_values=["max-connections"], type="str"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["C"], _from=G0, _to=G1),
    Transition(symbols=["B", "B'", "B''"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["D"], _from=G1, _to=G2),
    Transition(symbols=["B", "B'", "B''"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["B"],   _from=G2, _to=G3),
    Transition(symbols=["B'"],  _from=G2, _to=G4),
    Transition(symbols=["B''"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["B'"], _from=G3, _to=G5),
    Transition(symbols=["B", "B''"], _from=G3, _to=G3),
]

G4.transitions = [
    Transition(symbols=["B"], _from=G4, _to=G5),
    Transition(symbols=["B'", "B''"], _from=G4, _to=G4),
]

G5.transitions = [
    Transition(symbols=["B", "B'", "B''"], _from=G5, _to=G5),
]
