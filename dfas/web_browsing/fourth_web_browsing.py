from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="move_to_url",
        arguments={
            "file_name": FunctionArgument(
                name="file_name",
                value="page1.html",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "A'": FunctionCall(
        name="move_to_url",
        arguments={
            "file_name": FunctionArgument(
                name="file_name",
                value="page2.html",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "A''": FunctionCall(
        name="move_to_url",
        arguments={
            "file_name": FunctionArgument(
                name="file_name",
                value=None,
                excluded_values=["page1.html", "page2.html"],
                type="str",
            ),
        },
    ),
    "B": FunctionCall(
        name="get_page_source",
        arguments={},
    ),
    "C": FunctionCall(
        name="get_current_url",
        arguments={},
    ),
    "D": FunctionCall(
        name="go_back",
        arguments={},
    ),
    "E": FunctionCall(
        name="view_browsing_history",
        arguments={},
    ),
    "F": FunctionCall(
        name="find_text_in_page",
        arguments={
            "text": FunctionArgument(
                name="text",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["B", "C", "E", "F"], _from=G0, _to=G0),
    Transition(symbols=["A"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["B", "C", "E", "F"], _from=G1, _to=G1),
    Transition(symbols=["A'"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["B", "C", "E", "F"], _from=G2, _to=G2),
    Transition(symbols=["D"], _from=G2, _to=G3),
]

G3.transitions = [
    Transition(symbols=["B", "C", "E", "F"], _from=G3, _to=G3),
]
