from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3")
G4 = Node(name="G4")
G5 = Node(name="G5", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="add_article",
        arguments={
            "article": FunctionArgument(
                name="article",
                value="the",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "A'": FunctionCall(
        name="add_article",
        arguments={
            "article": FunctionArgument(
                name="article",
                value=None,
                excluded_values=["the"],
                type="str",
            ),
        },
    ),
    "B": FunctionCall(
        name="add_noun",
        arguments={
            "noun": FunctionArgument(
                name="noun",
                value="cat",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "B'": FunctionCall(
        name="add_noun",
        arguments={
            "noun": FunctionArgument(
                name="noun",
                value=None,
                excluded_values=["cat"],
                type="str",
            ),
        },
    ),
    "C": FunctionCall(
        name="add_verb",
        arguments={
            "verb": FunctionArgument(
                name="verb",
                value="runs",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "C'": FunctionCall(
        name="add_verb",
        arguments={
            "verb": FunctionArgument(
                name="verb",
                value=None,
                excluded_values=["runs"],
                type="str",
            ),
        },
    ),
    "D": FunctionCall(
        name="add_adjective",
        arguments={
            "adjective": FunctionArgument(
                name="adjective",
                value="big",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "D'": FunctionCall(
        name="add_adjective",
        arguments={
            "adjective": FunctionArgument(
                name="adjective",
                value=None,
                excluded_values=["big"],
                type="str",
            ),
        },
    ),
    "E": FunctionCall(
        name="add_preposition",
        arguments={
            "preposition": FunctionArgument(
                name="preposition",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "F": FunctionCall(
        name="complete_sentence",
        arguments={},
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["D"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["B"], _from=G2, _to=G3),
]

G3.transitions = [
    Transition(symbols=["C"], _from=G3, _to=G4),
]

G4.transitions = [
    Transition(symbols=["F"], _from=G4, _to=G5),
]

G5.transitions = []