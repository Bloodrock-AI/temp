from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node("G0")
G1 = Node("G1")
G2 = Node("G2")
G3 = Node("G3")
G4 = Node("G4", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="create_account",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value="D001",
                excluded_values=None,
                type="str",
            )
        },
    ),
    "A'": FunctionCall(
        name="create_account",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=["D001"],
                type="str",
            )
        },
    ),
    "B": FunctionCall(
        name="deposit",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value="D001",
                excluded_values=None,
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=1000,
                excluded_values=None,
                type="float",
            ),
        },
    ),
    "B'": FunctionCall(
        name="deposit",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=["D001"],
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=None,
                excluded_values=[1000],
                type="float",
            ),
        },
    ),
    "C": FunctionCall(
        name="withdraw",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value="D001",
                excluded_values=None,
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=300,
                excluded_values=None,
                type="float",
            ),
        },
    ),
    "C'": FunctionCall(
        name="withdraw",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=["D001"],
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=None,
                excluded_values=[300],
                type="float",
            ),
        },
    ),
    "D": FunctionCall(
        name="check_balance",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=None,
                type="str",
            )
        },
    ),
    "E": FunctionCall(
        name="transfer",
        arguments={
            "sender_id": FunctionArgument(
                name="sender_id",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "receiver_id": FunctionArgument(
                name="receiver_id",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=None,
                excluded_values=None,
                type="float",
            ),
        },
    ),
    "F": FunctionCall(
        name="get_transaction_history",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=None,
                type="str",
            )
        },
    ),
    "G": FunctionCall(
        name="apply_interest",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value="D001",
                excluded_values=None,
                type="str",
            ),
            "rate": FunctionArgument(
                name="rate",
                value=0.1,
                excluded_values=None,
                type="float",
            ),
        },
    ),
    "G'": FunctionCall(
        name="apply_interest",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=["D001"],
                type="str",
            ),
            "rate": FunctionArgument(
                name="rate",
                value=None,
                excluded_values=[0.1],
                type="float",
            ),
        },
    ),
    "H": FunctionCall(
        name="close_account",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=None,
                type="str",
            )
        },
    ),
    "I": FunctionCall(
        name="charge_fee",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=None,
                excluded_values=None,
                type="float",
            ),
        },
    ),
    "J": FunctionCall(
        name="refund",
        arguments={
            "account_id": FunctionArgument(
                name="account_id",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "amount": FunctionArgument(
                name="amount",
                value=None,
                excluded_values=None,
                type="float",
            ),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["D", "F"], _from=G0, _to=G0),
]

G1.transitions = [
    Transition(symbols=["B"], _from=G1, _to=G2),
    Transition(symbols=["D", "F"], _from=G1, _to=G1),
]

G2.transitions = [
    Transition(symbols=["G"], _from=G2, _to=G3),
    Transition(symbols=["D", "F"], _from=G2, _to=G2),
]

G3.transitions = [
    Transition(symbols=["C"], _from=G3, _to=G4),
    Transition(symbols=["D", "F"], _from=G3, _to=G3),
]

G4.transitions = [
    Transition(symbols=["D", "F"], _from=G4, _to=G4),
]
