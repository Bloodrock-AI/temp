from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1", is_final=True)

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
            "a": FunctionArgument(name="a", value=None, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=None, type="int"),
        },
    ),
    "C": FunctionCall(
        name="multiply_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=None, type="int"),
        },
    ),
    "D": FunctionCall(  # divide_numbers – not used in this DFA
        name="divide_numbers",
        arguments={
            "a": FunctionArgument(name="a", value=None, excluded_values=None, type="int"),
            "b": FunctionArgument(name="b", value=None, excluded_values=None, type="int"),
        },
    ),
    "E": FunctionCall(  # power – not used in this DFA
        name="power",
        arguments={
            "base":     FunctionArgument(name="base",     value=None, excluded_values=None, type="int"),
            "exponent": FunctionArgument(name="exponent", value=None, excluded_values=None, type="int"),
        },
    ),
    "F": FunctionCall(  # calculate_average([10, 20, 30])
        name="calculate_average",
        arguments={
            "numbers": FunctionArgument(name="numbers", value=[10, 20, 30], excluded_values=None, type="list[int]"),
        },
    ),
    "F'": FunctionCall(  # calculate_average(any other list)
        name="calculate_average",
        arguments={
            "numbers": FunctionArgument(name="numbers", value=None, excluded_values=[[10, 20, 30]], type="list[int]"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["F"], _from=G0, _to=G1),
]
G1.transitions = []
