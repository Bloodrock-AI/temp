from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3")
G4 = Node("G4", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="add_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=None, type="int"),
        },
    ),
    "B": FunctionCall(
        name="subtract_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=25, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=4,  excluded_values=None, type="int"),
        },
    ),
    "B'": FunctionCall(
        name="subtract_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=[25], type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=[4],  type="int"),
        },
    ),
    "C": FunctionCall(
        name="multiply_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=4, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=5, excluded_values=None, type="int"),
        },
    ),
    "C'": FunctionCall(
        name="multiply_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=[4], type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=[5], type="int"),
        },
    ),
    "D": FunctionCall(
        name="divide_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=21, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=3,  excluded_values=None, type="int"),
        },
    ),
    "D'": FunctionCall(
        name="divide_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=[21], type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=[3],  type="int"),
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
            "numbers": FunctionArgument(name="numbers", value=[7, 20], excluded_values=None, type="list[int]"),
        },
    ),
    "F'": FunctionCall(
        name="calculate_average",
        arguments={
            "numbers": FunctionArgument(name="numbers", value=None, excluded_values=[[7, 20]], type="list[int]"),
        },
    ),
}

G0.transitions = [Transition(symbols=["B"], _from=G0, _to=G1)]
G1.transitions = [Transition(symbols=["D"], _from=G1, _to=G2)]
G2.transitions = [Transition(symbols=["C"], _from=G2, _to=G3)]
G3.transitions = [Transition(symbols=["F"], _from=G3, _to=G4)]
G4.transitions = []
