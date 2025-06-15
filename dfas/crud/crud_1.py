from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="add_user",
        arguments={
            "name": FunctionArgument(name="name", value="Alice", excluded_values=None, type="str"),
            "age": FunctionArgument(name="age", value=25, excluded_values=None, type="int"),
            "email": FunctionArgument(name="email", value=None, excluded_values=None, type="Optional[str]"),
        },
    ),
    "A'": FunctionCall(
        name="add_user",
        arguments={
            "name": FunctionArgument(name="name", value=None, excluded_values=["Alice"], type="str"),
            "age": FunctionArgument(name="age", value=None, excluded_values=[25], type="int"),
            "email": FunctionArgument(name="email", value=None, excluded_values=None, type="Optional[str]"),
        },
    ),
    "B": FunctionCall(
        name="update_user_email",
        arguments={
            "user_id": FunctionArgument(name="user_id", value=None, excluded_values=None, type="str"),
            "email": FunctionArgument(name="email", value=None, excluded_values=None, type="str"),
        },
    ),
    "C": FunctionCall(
        name="delete_user",
        arguments={
            "user_id": FunctionArgument(name="user_id", value=None, excluded_values=None, type="str"),
        },
    ),
    "D": FunctionCall(name="list_users", arguments={}),
    "E": FunctionCall(
        name="verify_user_field",
        arguments={
            "user_id": FunctionArgument(name="user_id", value="Alice_id", excluded_values=None, type="str"),
            "field": FunctionArgument(name="field", value="age", excluded_values=None, type="str"),
            "expected_value": FunctionArgument(name="expected_value", value=25, excluded_values=None, type="int"),
        },
    ),
    "E'": FunctionCall(
        name="verify_user_field",
        arguments={
            "user_id": FunctionArgument(name="user_id", value=None, excluded_values=["Alice_id"], type="str"),
            "field": FunctionArgument(name="field", value=None, excluded_values=["age"], type="str"),
            "expected_value": FunctionArgument(name="expected_value", value=None, excluded_values=[25], type="str"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["D", "E", "E'"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["D"], _from=G1, _to=G2),
    Transition(symbols=["E", "E'"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["E"], _from=G2, _to=G3),
    Transition(symbols=["D", "E'"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["D", "E", "E'"], _from=G3, _to=G3),
]
