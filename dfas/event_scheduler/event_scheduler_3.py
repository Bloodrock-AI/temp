from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="schedule_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value=None, excluded_values=None, type="str"),
            "event_time": FunctionArgument(name="event_time", value=None,  excluded_values=None, type="str"),
        },
    ),
    "B": FunctionCall(
        name="cancel_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value=None, excluded_values=None, type="str"),
        },
    ),
    "C": FunctionCall(
        name="list_events",
        arguments={},
    ),
    "D": FunctionCall(
        name="reschedule_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value="Team Sync", excluded_values=None, type="str"),
            "new_time": FunctionArgument(name="new_time", value="2025-02-10T10:00:00",  excluded_values=None, type="str"),
        },
    ),
    "D'": FunctionCall(
        name="reschedule_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value=None, excluded_values=["Team Sync"], type="str"),
            "new_time": FunctionArgument(name="new_time", value=None,  excluded_values=["2025-02-10T10:00:00"], type="str"),
        },
    ),
    "E": FunctionCall(
        name="get_event_time",
        arguments={
            "event_name": FunctionArgument(name="event_name", value=None, excluded_values=None, type="str"),
        },
    ),
    "F": FunctionCall(
        name="time_until_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value="Team Sync", excluded_values=None, type="str"),
        },
    ),
    "F'": FunctionCall(
        name="time_until_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value=None, excluded_values=["Team Sync"], type="str"),
        },
    ),
    "G": FunctionCall(
        name="schedule_recurring_event",
        arguments={
            "event_name": FunctionArgument(name="event_name", value=None, excluded_values=None, type="str"),
            "interval_minutes": FunctionArgument(name="interval_minutes", value=None, excluded_values=None, type="int"),

        },
    ),
}

G0.transitions = [
    Transition(symbols=["D"], _from=G0, _to=G1),
    Transition(symbols=["C", "E","F", "F'"], _from=G0, _to=G0),
]
G1.transitions = [
    Transition(symbols=["F"], _from=G1, _to=G2),
    Transition(symbols=["C", "E", "F'"], _from=G1, _to=G1),
]
G2.transitions = [
    Transition(symbols=["C", "E", "F", "F'"], _from=G2, _to=G2),
]
