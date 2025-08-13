# robot_farm_1.py
# DFA for:
# "Disengage safety. Drive to plant C and harvest its fruit.
#  Then take the load to the collection bin, empty the hopper, and return to base."

from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument


G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3")
G4 = Node("G4")
G5 = Node("G5")
G6 = Node("G6", is_final=True)

alphabet: dict[str, FunctionCall] = {

    "A": FunctionCall(name="unlock_safety_mode", arguments={}),

    "B": FunctionCall(name="lock_safety_mode", arguments={}),

    "C": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=14.0, type="float", excluded_values=None),
            "y":   FunctionArgument(name="y",   value=8.5,  type="float", excluded_values=None),
            "yaw": FunctionArgument(name="yaw", value=0.0,  type="float", excluded_values=None),
        },
    ),
    "C'": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=6.0,  type="float", excluded_values=None),
            "y":   FunctionArgument(name="y",   value=18.0, type="float", excluded_values=None),
            "yaw": FunctionArgument(name="yaw", value=0.0,  type="float", excluded_values=None),
        },
    ),
    "C''": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=5.0, type="float", excluded_values=None),
            "y":   FunctionArgument(name="y",   value=5.0, type="float", excluded_values=None),
            "yaw": FunctionArgument(name="yaw", value=0.0, type="float", excluded_values=None),
        },
    ),
    "C'''": FunctionCall(
        name="move_to",
        arguments={
            "x":   FunctionArgument(name="x",   value=None, type="float", excluded_values=[14.0, 6.0, 5.0]),
            "y":   FunctionArgument(name="y",   value=None, type="float", excluded_values=[8.5, 18.0, 5.0]),
            "yaw": FunctionArgument(name="yaw", value=None, type="float", excluded_values=[0.0]),
        },
    ),

    "D": FunctionCall(name="move_home", arguments={}),

 
    "E": FunctionCall(
        name="harvest_fruit",
        arguments={"plant_id": FunctionArgument(name="plant_id", value="plant_C", type="str", excluded_values=None)},
    ),

    "E'": FunctionCall(
        name="harvest_fruit",
        arguments={"plant_id": FunctionArgument(name="plant_id", value=None, type="str", excluded_values=["plant_C"])},
    ),

    "F": FunctionCall(name="dump_hopper", arguments={}),

    "G": FunctionCall(
        name="water_plant",
        arguments={
            "plant_id": FunctionArgument(name="plant_id", value=None, type="str",   excluded_values=None),
            "liters":   FunctionArgument(name="liters",   value=None, type="float", excluded_values=None),
        },
    ),

    "H": FunctionCall(
        name="spray_pesticide",
        arguments={
            "plant_id": FunctionArgument(name="plant_id", value=None, type="str",   excluded_values=None),
            "ml":       FunctionArgument(name="ml",       value=None, type="float", excluded_values=None),
        },
    ),

    "I": FunctionCall(name="refill_water_tank", arguments={}),

    "J": FunctionCall(name="refill_pesticide", arguments={}),

    "K": FunctionCall(name="recharge", arguments={}),

    "L": FunctionCall(name="sense_pose", arguments={}),

    "M": FunctionCall(name="sense_battery", arguments={}),

    "N": FunctionCall(name="sense_hopper", arguments={}),

    "O": FunctionCall(name="list_plants", arguments={}),

    "P": FunctionCall(
        name="scan_plant",
        arguments={"plant_id": FunctionArgument(name="plant_id", value=None, type="str", excluded_values=None)},
    ),

    "Q": FunctionCall(
        name="get_plant_pose",
        arguments={"plant_id": FunctionArgument(name="plant_id", value=None, type="str", excluded_values=None)},
    ),

    "R": FunctionCall(
        name="get_station_pose",
        arguments={"station_name": FunctionArgument(name="station_name", value=None, type="str", excluded_values=None)},
    ),
}

READS = ["L", "M", "N", "O", "P", "Q", "R"]



G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=READS, _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["C"], _from=G1, _to=G2),
    Transition(symbols=READS, _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["E"], _from=G2, _to=G3),
    Transition(symbols=READS, _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["C'"], _from=G3, _to=G4),
    Transition(symbols=READS, _from=G3, _to=G3),
]

G4.transitions = [
    Transition(symbols=["F"], _from=G4, _to=G5),
    Transition(symbols=READS, _from=G4, _to=G4),
]

G5.transitions = [
    Transition(symbols=["D", "C''"], _from=G5, _to=G6),
    Transition(symbols=READS, _from=G5, _to=G5),
]

G6.transitions = [
    Transition(symbols=READS, _from=G6, _to=G6),
]
