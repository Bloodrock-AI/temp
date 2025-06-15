from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="send_message",
        arguments={
            "sender": FunctionArgument(name="sender", value="Charlie", excluded_values=None, type="str"),
            "recipient": FunctionArgument(name="recipient", value="Dana", excluded_values=None, type="str"),
            "content": FunctionArgument(name="content", value="Lunch at noon", excluded_values=None, type="str"),
            "priority": FunctionArgument(name="priority", value="normal", excluded_values=None, type="str"),
        },
    ),
    "A'": FunctionCall(
        name="send_message",
        arguments={
            "sender": FunctionArgument(name="sender", value=None, excluded_values=["Charlie"], type="str"),
            "recipient": FunctionArgument(name="recipient", value=None, excluded_values=["Dana"], type="str"),
            "content": FunctionArgument(name="content", value=None, excluded_values=["Lunch at noon"], type="str"),
            "priority": FunctionArgument(name="priority", value=None, excluded_values=["normal"], type="str"),
        },
    ),
    "B": FunctionCall(
        name="print_messages",
        arguments={
            "recipient": FunctionArgument(name="recipient", value="Dana", excluded_values=None, type="str"),
            "priority": FunctionArgument(name="priority", value="normal", excluded_values=None, type="str"),
        },
    ),
    "B'": FunctionCall(
        name="print_messages",
        arguments={
            "recipient": FunctionArgument(name="recipient", value=None, excluded_values=["Dana"], type="str"),
            "priority": FunctionArgument(name="priority", value=None, excluded_values=["normal"], type="str"),
        },
    ),
    "C": FunctionCall(
        name="delete_message",
        arguments={
            "sender": FunctionArgument(name="sender", value="Charlie", excluded_values=None, type="str"),
            "recipient": FunctionArgument(name="recipient", value="Dana", excluded_values=None, type="str"),
        },
    ),
    "C'": FunctionCall(
        name="delete_message",
        arguments={
            "sender": FunctionArgument(name="sender", value=None, excluded_values=["Charlie"], type="str"),
            "recipient": FunctionArgument(name="recipient", value=None, excluded_values=["Dana"], type="str"),
        },
    ),
    "D": FunctionCall(
        name="forward_message",
        arguments={
            "original_sender": FunctionArgument(name="original_sender", value=None, excluded_values=None, type="str"),
            "new_recipient": FunctionArgument(name="new_recipient", value=None, excluded_values=None, type="str"),
            "timestamp": FunctionArgument(name="timestamp", value=None, excluded_values=None, type="str"),
            "forwarded_by": FunctionArgument(name="forwarded_by", value=None, excluded_values=None, type="str"),
        },
    ),
    "E": FunctionCall(
        name="schedule_message",
        arguments={
            "sender": FunctionArgument(name="sender", value=None, excluded_values=None, type="str"),
            "recipient": FunctionArgument(name="recipient", value=None, excluded_values=None, type="str"),
            "content": FunctionArgument(name="content", value=None, excluded_values=None, type="str"),
            "send_time": FunctionArgument(name="send_time", value=None, excluded_values=None, type="str"),
            "priority": FunctionArgument(name="priority", value=None, excluded_values=None, type="str"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["B", "B'"], _from=G0, _to=G0),
    Transition(symbols=["A"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["B'"], _from=G1, _to=G1),
    Transition(symbols=["B"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["B", "B'"], _from=G2, _to=G2),
    Transition(symbols=["C"], _from=G2, _to=G3),
]

G3.transitions = [
    Transition(symbols=["B", "B'"], _from=G3, _to=G3),
]
