from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="validate_email",
        arguments={
            "email": FunctionArgument(name="email", value=None, excluded_values=None, type="str"),
        },
    ),
    "B": FunctionCall(
        name="hash_password",
        arguments={
            "password": FunctionArgument(name="password", value="Yharnam", excluded_values=None, type="str"),
        },
    ),
    "B'": FunctionCall(
        name="hash_password",
        arguments={
            "password": FunctionArgument(name="password", value=None, excluded_values=["Yharnam"], type="str"),
        },
    ),
    "C": FunctionCall(
        name="check_password_hash",
        arguments={
            "password": FunctionArgument(name="password", value="Hunter", excluded_values=None, type="str"),
            "hashed_password": FunctionArgument(
                name="hashed_password",
                value="0a099edf6266ef30bc1f157a1cb2a0c8cdec45be4e7fbbff6c765949076ead14",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "C'": FunctionCall(
        name="check_password_hash",
        arguments={
            "password": FunctionArgument(name="password", value=None, excluded_values=["Hunter"], type="str"),
            "hashed_password": FunctionArgument(name="hashed_password", value=None, excluded_values=["0a099edf6266ef30bc1f157a1cb2a0c8cdec45be4e7fbbff6c765949076ead14"], type="str"),
        },
    ),
    "D": FunctionCall(
        name="validate_username",
        arguments={
            "username": FunctionArgument(name="username", value=None, excluded_values=None, type="str"),
        },
    ),
    "E": FunctionCall(
        name="generate_otp",
        arguments={
            "length": FunctionArgument(name="length", value=None, excluded_values=None, type="int"),
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
    Transition(symbols=["A", "D"], _from=G0, _to=G0),
    Transition(symbols=["B"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["A", "D"], _from=G1, _to=G1),
    Transition(symbols=["C"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["A", "D"], _from=G2, _to=G2),
]
