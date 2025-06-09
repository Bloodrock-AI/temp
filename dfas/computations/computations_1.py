from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="add_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=15, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=7,  excluded_values=None, type="int"),
        },
    ),
    "A'": FunctionCall(
        name="add_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=[15], type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=[7],  type="int"),
        },
    ),
    "B": FunctionCall(
        name="subtract_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=None, type="int"),
        },
    ),
    "C": FunctionCall(
        name="multiply_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=22, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=3,  excluded_values=None, type="int"),
        },
    ),
    "C'": FunctionCall(
        name="multiply_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=[22], type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=[3],  type="int"),
        },
    ),
    "D": FunctionCall(
        name="divide_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=None, type="int"),
        },
    ),
    "E": FunctionCall(
        name="power",
        arguments={
            "base":     FunctionArgument(name="base",     value=None, excluded_values=None, type="int"),
            "exponent": FunctionArgument(name="exponent", value=None, excluded_values=None, type="int"),
        },
    ),
    "F": FunctionCall(
        name="calculate_average",
        arguments={
            "numbers": FunctionArgument(name="numbers", value=None, excluded_values=None, type="list[int]"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
]
G1.transitions = [
    Transition(symbols=["C"], _from=G1, _to=G2),
]
G2.transitions = []
