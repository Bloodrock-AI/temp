from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="validate_email",
        arguments={
            "email": FunctionArgument(name="email", value=None, excluded_values=None, type="str")
        },
    ),
    "B": FunctionCall(
        name="hash_password",
        arguments={
            "password": FunctionArgument(name="password", value=None, excluded_values=None, type="str")
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
            "length": FunctionArgument(name="length", value=7, excluded_values=None, type="int")
        },
    ),
    "E'": FunctionCall(
        name="generate_otp",
        arguments={
            "length": FunctionArgument(name="length", value=None, excluded_values=[7], type="int")
        },
    ),
    "F": FunctionCall(
        name="verify_otp",
        arguments={
            "input_otp": FunctionArgument(name="input_otp", value="1234567", excluded_values=None, type="str"),
            "correct_otp": FunctionArgument(name="correct_otp", value="1234567", excluded_values=None, type="str"),
        },
    ),
    "F'": FunctionCall(
        name="verify_otp",
        arguments={
            "input_otp": FunctionArgument(name="input_otp", value=None, excluded_values=["1234567"], type="str"),
            "correct_otp": FunctionArgument(name="correct_otp", value=None, excluded_values=["1234567"], type="str"),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A", "D"], _from=G0, _to=G0),
    Transition(symbols=["E"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["A", "D"], _from=G1, _to=G1),
    Transition(symbols=["F"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["A", "D"], _from=G2, _to=G2),
]
