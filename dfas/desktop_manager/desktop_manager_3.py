from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")                
G1 = Node("G1")
G3 = Node("G3")
G4 = Node("G4")
G5 = Node("G5", is_final=True)  

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="open_application",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value="Music Player",
                excluded_values=None,
                type="str",
            )
        },
    ),
    "A'": FunctionCall( 
        name="open_application",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value=None,
                excluded_values=["Music Player"],
                type="str",
            )
        },
    ),
    "B": FunctionCall(
        name="close_application",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value="Music Player",
                excluded_values=None,
                type="str",
            )
        },
    ),
    "B'": FunctionCall(  
        name="close_application",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value=None,
                excluded_values=["Music Player"],
                type="str",
            )
        },
    ),
    "C": FunctionCall(name="print_open_applications", arguments={}),
    "D": FunctionCall(name="print_application_history", arguments={}),
    "E": FunctionCall(
        name="perform_action",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value="Music Player",
                excluded_values=None,
                type="str",
            ),
            "action": FunctionArgument(
                name="action",
                value="play_song",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "E'": FunctionCall( 
        name="perform_action",
        arguments={
            "app_name": FunctionArgument(name="app_name", value=None, excluded_values=None, type="str"),
            "action": FunctionArgument(name="action", value=None, excluded_values=["play_song"], type="str"),
        },
    ),
    "F": FunctionCall(
        name="print_application_actions",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value="Music Player",
                excluded_values=None,
                type="str",
            )
        },
    ),
    "F'": FunctionCall( 
        name="print_application_actions",
        arguments={
            "app_name": FunctionArgument(
                name="app_name",
                value=None,
                excluded_values=["Music Player"],
                type="str",
            )
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["C", "D", "F", "F'"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["F"], _from=G1, _to=G3),
    Transition(symbols=["C", "D", "F'"], _from=G1, _to=G1),
]

G3.transitions = [
    Transition(symbols=["E"], _from=G3, _to=G4),
    Transition(symbols=["C", "D", "F", "F'"], _from=G3, _to=G3),
]

G4.transitions = [
    Transition(symbols=["B"], _from=G4, _to=G5),
    Transition(symbols=["C", "D", "F", "F'"], _from=G4, _to=G4),
]

G5.transitions = [
    Transition(symbols=["C", "D", "F", "F'"], _from=G5, _to=G5),
]
