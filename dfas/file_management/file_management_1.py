from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="create_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value="new_meeting.txt",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "A'": FunctionCall(
        name="create_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=["new_meeting.txt"],
                type="str",
            ),
        },
    ),
    "B": FunctionCall(
        name="delete_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "C": FunctionCall(
        name="read_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "D": FunctionCall(
        name="write_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value="new_meeting.txt",
                excluded_values=None,
                type="str",
            ),
            "content": FunctionArgument(
                name="content",
                value="Meeting at 10 AM",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "D'": FunctionCall(
        name="write_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=["new_meeting.txt"],
                type="str",
            ),
            "content": FunctionArgument(
                name="content",
                value=None,
                excluded_values=["Meeting at 10 AM"],
                type="str",
            ),
        },
    ),
    "E": FunctionCall(
        name="append_to_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "content": FunctionArgument(
                name="content",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "F": FunctionCall(name="list_files", arguments={}),
    "G": FunctionCall(
        name="rename_file",
        arguments={
            "old_name": FunctionArgument(
                name="old_name",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "new_name": FunctionArgument(
                name="new_name",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "H": FunctionCall(
        name="copy_file",
        arguments={
            "source": FunctionArgument(
                name="source",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "destination": FunctionArgument(
                name="destination",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "I": FunctionCall(
        name="move_file",
        arguments={
            "source": FunctionArgument(
                name="source",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "destination": FunctionArgument(
                name="destination",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "J": FunctionCall(
        name="file_exists",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "K": FunctionCall(
        name="get_file_size",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "L": FunctionCall(
        name="clear_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "M": FunctionCall(
        name="count_words",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "N": FunctionCall(
        name="search_in_file",
        arguments={
            "filename": FunctionArgument(
                name="filename",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "keyword": FunctionArgument(
                name="keyword",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["C", "F", "J", "K", "M", "N"], _from=G0, _to=G0),
    Transition(symbols=["A"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["C", "F", "J", "K", "M", "N"], _from=G1, _to=G1),
    Transition(symbols=["D"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["C", "F", "J", "K", "M", "N"], _from=G2, _to=G2),
]