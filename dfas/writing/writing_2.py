from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3")
G4 = Node(name="G4")
G5 = Node(name="G5")
G6 = Node(name="G6")
G7 = Node(name="G7")
G8 = Node(name="G8", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="add_article",
        arguments={"article": FunctionArgument(name="article", value="a", excluded_values=None, type="str")},
    ),
    "A'": FunctionCall(
        name="add_article",
        arguments={"article": FunctionArgument(name="article", value=None, excluded_values=["a"], type="str")},
    ),
    "B": FunctionCall(
        name="add_noun",
        arguments={"noun": FunctionArgument(name="noun", value="dog", excluded_values=None, type="str")},
    ),
    "B'": FunctionCall(
        name="add_noun",
        arguments={"noun": FunctionArgument(name="noun", value="tree", excluded_values=None, type="str")},
    ),
    "B''": FunctionCall(
        name="add_noun",
        arguments={"noun": FunctionArgument(name="noun", value=None, excluded_values=["dog", "tree"], type="str")},
    ),
    "C": FunctionCall(
        name="add_verb",
        arguments={"verb": FunctionArgument(name="verb", value="sleeps", excluded_values=None, type="str")},
    ),
    "C'": FunctionCall(
        name="add_verb",
        arguments={"verb": FunctionArgument(name="verb", value=None, excluded_values=["sleeps"], type="str")},
    ),
    "D": FunctionCall(
        name="add_adjective",
        arguments={"adjective": FunctionArgument(name="adjective", value="small", excluded_values=None, type="str")},
    ),
    "D'": FunctionCall(
        name="add_adjective",
        arguments={"adjective": FunctionArgument(name="adjective", value=None, excluded_values=["small"], type="str")},
    ),
    "E": FunctionCall(
        name="add_preposition",
        arguments={"preposition": FunctionArgument(name="preposition", value="under", excluded_values=None, type="str")},
    ),
    "E'": FunctionCall(
        name="add_preposition",
        arguments={"preposition": FunctionArgument(name="preposition", value=None, excluded_values=["under"], type="str")},
    ),
    "F": FunctionCall(name="complete_sentence", arguments={}),
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
    Transition(symbols=["E"], _from=G4, _to=G5),
]

G5.transitions = [
    Transition(symbols=["A"], _from=G5, _to=G6),
]

G6.transitions = [
    Transition(symbols=["B'"], _from=G6, _to=G7),
]

G7.transitions = [
    Transition(symbols=["F"], _from=G7, _to=G8),
]

G8.transitions = []