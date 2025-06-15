from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")                    
G1 = Node("G1")                    
G2 = Node("G2")                   
G3 = Node("G3", is_final=True)     

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(                
        name="open_application",
        arguments={
            "app_name": FunctionArgument(
                name="app_name", value="Terminal", excluded_values=None, type="str"
            )
        },
    ),
    "B": FunctionCall(                 
        name="close_application",
        arguments={
            "app_name": FunctionArgument(
                name="app_name", value=None, excluded_values=None, type="str"
            )
        },
    ),
    "C": FunctionCall(name="print_open_applications", arguments={}),
    "D": FunctionCall(name="print_application_history", arguments={}),
    "E": FunctionCall(                
        name="perform_action",
        arguments={
            "app_name": FunctionArgument(name="app_name", value="Terminal", excluded_values=None, type="str"),
            "action":   FunctionArgument(name="action",   value="execute_command", excluded_values=None, type="str"),
        },
    ),
    "E'": FunctionCall(                
        name="perform_action",
        arguments={
            "app_name": FunctionArgument(name="app_name", value=None, excluded_values=["Terminal"], type="str"),
            "action":   FunctionArgument(name="action",   value=None, excluded_values=["execute_command"], type="str"),
        },
    ),
    "F": FunctionCall(                
        name="print_application_actions",
        arguments={
            "app_name": FunctionArgument(
                name="app_name", value=None, excluded_values=None, type="str"
            )
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["C", "D", "F"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["E"], _from=G1, _to=G2),
    Transition(symbols=["C", "D", "F"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["C"], _from=G2, _to=G3),
    Transition(symbols=["D", "F"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["C", "D", "F"], _from=G3, _to=G3),
]
