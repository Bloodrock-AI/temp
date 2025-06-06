from typing import List
from dfas.dfa import Node, Transition, Prompt, FunctionCall, FunctionArgument


# Prompt 1
G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2", is_final=True)

alphabet: List[str, FunctionCall] = {
    "A": FunctionCall(
        'add_numbers',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=15,
                excluded_values=None,
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=7,
                excluded_values=None,
                type="int"
            ),
        },
    ),
    "A'": FunctionCall(
        'add_numbers',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=None,
                excluded_values=[15],
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=None,
                excluded_values=[7],
                type="int"
            ),
        },
    ),
    "B": FunctionCall(
        'subtract_numbers',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=None,
                excluded_values=[],
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=None,
                excluded_values=[],
                type="int"
            ),
        },
    ),
    "C": FunctionCall(
        'multiply_numbers',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=22,
                excluded_values=None,
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=3,
                excluded_values=None,
                type="int"
            ),
        },
    ),
    "C'": FunctionCall(
        'multiply_numbers',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=None,
                excluded_values=[],
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=None,
                excluded_values=[],
                type="int"
            ),
        },
    ),
    "D": FunctionCall(
        'divide_numbers',
        arguments={
            "a": FunctionArgument(
                name="a",
                value=None,
                excluded_values=[],
                type="int"
            ),
            "b": FunctionArgument(
                name="b",
                value=None,
                excluded_values=[],
                type="int"
            ),
        },
    ),
    "E": FunctionCall(
        'power',
        arguments={
            "base": FunctionArgument(
                name="base",
                value=None,
                excluded_values=[],
                type="int"
            ),
            "exponent": FunctionArgument(
                name="exponent",
                value=None,
                excluded_values=[],
                type="int"
            ),
        },
    ),
    "F": FunctionCall(
        'calculate_average',
        arguments={
            "numbers": FunctionArgument(
                name="numbers",
                value=None,
                excluded_values=[],
                type="list[int]"
            ),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
]
G1.transitions = [
    Transition(symbols=["C",], _from=G1, _to=G2),
]
G2.transitions = []