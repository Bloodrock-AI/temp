from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3")
G4 = Node("G4")
G5 = Node("G5")
G6 = Node("G6")
G7 = Node("G7")
G8 = Node("G8", is_final=True)


alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(name="unlock_safety_mode", arguments={}),
    "B": FunctionCall(name="lock_safety_mode", arguments={}),

    "C": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=0.60, excluded_values=None, type="float"),
            "y":   FunctionArgument(name="y",   value=0.10, excluded_values=None, type="float"),
            "z":   FunctionArgument(name="z",   value=0.11, excluded_values=None, type="float"),
            "yaw": FunctionArgument(name="yaw", value=0.0,  excluded_values=None, type="float"),
        },
    ),

    "C'": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=0.80, excluded_values=None, type="float"),
            "y":   FunctionArgument(name="y",   value=0.35, excluded_values=None, type="float"),
            "z":   FunctionArgument(name="z",   value=0.10, excluded_values=None, type="float"),
            "yaw": FunctionArgument(name="yaw", value=0.0,  excluded_values=None, type="float"),
        },
    ),

    "C''": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=None, excluded_values=[0.60, 0.80], type="float"),
            "y":   FunctionArgument(name="y",   value=None, excluded_values=[0.10, 0.35], type="float"),
            "z":   FunctionArgument(name="z",   value=None, excluded_values=[0.11, 0.10], type="float"),
            "yaw": FunctionArgument(name="yaw", value=None, excluded_values=[0.0],      type="float"),
        },
    ),
    "D": FunctionCall(name="move_home", arguments={}),

    "E": FunctionCall(name="open_gripper", arguments={}),
    "F": FunctionCall(name="close_gripper", arguments={}),

    "G": FunctionCall(
        name="pick",
        arguments={"object_name": FunctionArgument(name="object_name", value="gear_A", excluded_values=None, type="str")},
    ),
    "G'": FunctionCall(
        name="pick",
        arguments={"object_name": FunctionArgument(name="object_name", value=None, excluded_values=["gear_A"], type="str")},
    ),
    "H": FunctionCall(name="place", arguments={}),

    "I": FunctionCall(name="sense_pose", arguments={}),
    "J": FunctionCall(name="sense_gripper", arguments={}),
    "K": FunctionCall(name="list_objects", arguments={}),
    "L": FunctionCall(
        name="get_object_pose",
        arguments={
            "object_name": FunctionArgument(name="object_name", value=None, excluded_values=None, type="str")
        },
    ),
    "M": FunctionCall(
        name="get_station_pose",
        arguments={"station_name": FunctionArgument(name="station_name", value=None, excluded_values=None, type="str")},
    ),
}

READS_ALL = ["I", "J", "K", "L", "M"]
READS_G1 = ["J", "K", "L", "M"]          # I advances to G2
READS_G2 = ["I", "J", "L", "M"]          # K advances to G3


G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=READS_ALL, _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["I"], _from=G1, _to=G2),
    Transition(symbols=READS_G1, _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["K"], _from=G2, _to=G3),
    Transition(symbols=READS_G2, _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["C"], _from=G3, _to=G4),
    Transition(symbols=READS_ALL, _from=G3, _to=G3),
]

G4.transitions = [
    Transition(symbols=["E"], _from=G4, _to=G5),
    Transition(symbols=READS_ALL, _from=G4, _to=G4),
]

G5.transitions = [
    Transition(symbols=["G"], _from=G5, _to=G6),
    Transition(symbols=READS_ALL, _from=G5, _to=G5),
]

G6.transitions = [
    Transition(symbols=["C'"], _from=G6, _to=G7),
    Transition(symbols=READS_ALL, _from=G6, _to=G6),
]

G7.transitions = [
    Transition(symbols=["H"], _from=G7, _to=G8),
    Transition(symbols=READS_ALL, _from=G7, _to=G7),
]

G8.transitions = [
    Transition(symbols=READS_ALL, _from=G8, _to=G8),
]
