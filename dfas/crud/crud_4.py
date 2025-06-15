from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="add_user",
        arguments={
            "name": FunctionArgument(name="name", value="Charlie", excluded_values=None, type="str"),
            "age": FunctionArgument(name="age", value=40, excluded_values=None, type="int"),
            "email": FunctionArgument(name="email", value="charlie@email.com", excluded_values=None, type="str"),
        },
    ),
    "A'": FunctionCall(
        name="add_user",
        arguments={
            "name": FunctionArgument(name="name", value=None, excluded_values=["Charlie"], type="str"),
            "age": FunctionArgument(name="age", value=None, excluded_values=[40], type="int"),
            "email": FunctionArgument(name="email", value=None, excluded_values=["charlie@email.com"], type="Optional[str]"),
        },
    ),
    "C": FunctionCall(
        name="delete_user",
        arguments={
            "user_id": FunctionArgument(name="user_id", value="Charlie_id", excluded_values=None, type="str"),
        },
    ),
    "C'": FunctionCall(
        name="delete_user",
        arguments={
            "user_id": FunctionArgument(name="user_id", value=None, excluded_values=["Charlie_id"], type="str"),
        },
    ),
    "D": FunctionCall(name="list_users", arguments={}),
    "E": FunctionCall(
        name="verify_user_field",
        arguments={
            "user_id": FunctionArgument(name="user_id", value=None, excluded_values=None, type="str"),
            "field": FunctionArgument(name="field", value=None, excluded_values=None, type="str"),
            "expected_value": FunctionArgument(name="expected_value", value=None, excluded_values=None, type="str"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["D", "E"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["C"], _from=G1, _to=G2),
    Transition(symbols=["D", "E"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["D"], _from=G2, _to=G3),
    Transition(symbols=["E"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["D", "E"], _from=G3, _to=G3),
]
