from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="validate_email",
        arguments={
            "email": FunctionArgument(name="email", value="invalid-email", excluded_values=None, type="str")
        },
    ),
    "A'": FunctionCall(
        name="validate_email",
        arguments={
            "email": FunctionArgument(name="email", value=None, excluded_values=["invalid-email"], type="str")
        },
    ),
    "B": FunctionCall(
        name="hash_password",
        arguments={
            "password": FunctionArgument(name="password", value="test123", excluded_values=None, type="str")
        },
    ),
    "B'": FunctionCall(
        name="hash_password",
        arguments={
            "password": FunctionArgument(name="password", value=None, excluded_values=["test123"], type="str")
        },
    ),
    "C": FunctionCall(
        name="check_password_hash",
        arguments={
            "password": FunctionArgument(name="password", value=None, excluded_values=None, type="str"),
            "hashed_password": FunctionArgument(name="hashed_password", value=None, excluded_values=None, type="str"),
        },
    ),
    "D": FunctionCall(
        name="validate_username",
        arguments={
            "username": FunctionArgument(name="username", value=None, excluded_values=None, type="str")
        },
    ),
    "E": FunctionCall(
        name="generate_otp",
        arguments={
            "length": FunctionArgument(name="length", value=9, excluded_values=None, type="int")
        },
    ),
    "E'": FunctionCall(
        name="generate_otp",
        arguments={
            "length": FunctionArgument(name="length", value=None, excluded_values=[9], type="int")
        },
    ),
    "F": FunctionCall(
        name="verify_otp",
        arguments={
            "input_otp": FunctionArgument(name="input_otp", value=None, excluded_values=None, type="str"),
            "correct_otp": FunctionArgument(name="correct_otp", value=None, excluded_values=None, type="str"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["A'", "D"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["B"], _from=G1, _to=G2),
    Transition(symbols=["A", "A'", "D"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["E"], _from=G2, _to=G3),
    Transition(symbols=["A", "A'", "D"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["A", "A'", "D"], _from=G3, _to=G3),
]
