from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2")
G3 = Node(name="G3")
G4 = Node(name="G4")
G5 = Node(name="G5")
G6 = Node(name="G6", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="create_account",
        arguments={"account_id": FunctionArgument(name="account_id", value="A123", excluded_values=None, type="str")},
    ),
    "A'": FunctionCall(
        name="create_account",
        arguments={"account_id": FunctionArgument(name="account_id", value="B456", excluded_values=None, type="str")},
    ),
    "A''": FunctionCall(
        name="create_account",
        arguments={"account_id": FunctionArgument(name="account_id", value=None, excluded_values=["A123", "B456"], type="str")},
    ),
    "B": FunctionCall(
        name="deposit",
        arguments={
            "account_id": FunctionArgument(name="account_id", value="A123", excluded_values=None, type="str"),
            "amount": FunctionArgument(name="amount", value=500, excluded_values=None, type="float"),
        },
    ),
    "B'": FunctionCall(
        name="deposit",
        arguments={
            "account_id": FunctionArgument(name="account_id", value=None, excluded_values=["A123"], type="str"),
            "amount": FunctionArgument(name="amount", value=None, excluded_values=[500], type="float"),
        },
    ),
    "C": FunctionCall(
        name="withdraw",
        arguments={
            "account_id": FunctionArgument(name="account_id", value=None, excluded_values=None, type="str"),
            "amount": FunctionArgument(name="amount", value=None, excluded_values=None, type="float"),
        },
    ),
    "D": FunctionCall(
        name="check_balance",
        arguments={"account_id": FunctionArgument(name="account_id", value="A123", excluded_values=None, type="str")},
    ),
    "D'": FunctionCall(
        name="check_balance",
        arguments={"account_id": FunctionArgument(name="account_id", value="B456", excluded_values=None, type="str")},
    ),
    "D''": FunctionCall(
        name="check_balance",
        arguments={"account_id": FunctionArgument(name="account_id", value=None, excluded_values=["A123", "B456"], type="str")},
    ),
    "E": FunctionCall(
        name="transfer",
        arguments={
            "sender_id": FunctionArgument(name="sender_id", value="A123", excluded_values=None, type="str"),
            "receiver_id": FunctionArgument(name="receiver_id", value="B456", excluded_values=None, type="str"),
            "amount": FunctionArgument(name="amount", value=300, excluded_values=None, type="float"),
        },
    ),
    "E'": FunctionCall(
        name="transfer",
        arguments={
            "sender_id": FunctionArgument(name="sender_id", value=None, excluded_values=["A123"], type="str"),
            "receiver_id": FunctionArgument(name="receiver_id", value=None, excluded_values=["B456"], type="str"),
            "amount": FunctionArgument(name="amount", value=None, excluded_values=[300], type="float"),
        },
    ),
    "F": FunctionCall(
        name="get_transaction_history",
        arguments={"account_id": FunctionArgument(name="account_id", value=None, excluded_values=None, type="str")},
    ),
    "G": FunctionCall(
        name="apply_interest",
        arguments={
            "account_id": FunctionArgument(name="account_id", value=None, excluded_values=None, type="str"),
            "rate": FunctionArgument(name="rate", value=None, excluded_values=None, type="float"),
        },
    ),
    "H": FunctionCall(
        name="close_account",
        arguments={"account_id": FunctionArgument(name="account_id", value=None, excluded_values=None, type="str")},
    ),
    "I": FunctionCall(
        name="charge_fee",
        arguments={
            "account_id": FunctionArgument(name="account_id", value=None, excluded_values=None, type="str"),
            "amount": FunctionArgument(name="amount", value=None, excluded_values=None, type="float"),
        },
    ),
    "J": FunctionCall(
        name="refund",
        arguments={
            "account_id": FunctionArgument(name="account_id", value=None, excluded_values=None, type="str"),
            "amount": FunctionArgument(name="amount", value=None, excluded_values=None, type="float"),
        },
    ),
}

loop_syms = ["D", "D'", "D''", "F"]
for node in [G0, G1, G2, G3, G4, G5, G6]:
    node.transitions.extend([Transition(symbols=loop_syms, _from=node, _to=node)])

G0.transitions = [
    Transition(symbols=["A"], _from=G0, _to=G1),
    Transition(symbols=["D", "D'", "D''", "F"], _from=G0, _to=G0),
    ]
G1.transitions = [
    Transition(symbols=["A'"], _from=G1, _to=G2),
    Transition(symbols=["D", "D'", "D''", "F"], _from=G1, _to=G1),
    ]
G2.transitions = [
    Transition(symbols=["B"], _from=G2, _to=G3),
    Transition(symbols=["D", "D'", "D''", "F"], _from=G2, _to=G2),
    ]
G3.transitions = [
    Transition(symbols=["E"], _from=G3, _to=G4),
    Transition(symbols=["D", "D'", "D''", "F"], _from=G3, _to=G3),
    ]
G4.transitions = [
    Transition(symbols=["D"], _from=G4, _to=G5),
    Transition(symbols=["D'", "D''", "F"], _from=G4, _to=G4),
    ]
G5.transitions = [
    Transition(symbols=["D'"], _from=G5, _to=G6),
    Transition(symbols=["D'", "D''", "F"], _from=G5, _to=G5),
    ]
G6.transitions = [
    Transition(symbols=["D", "D'", "D''", "F"], _from=G6, _to=G6),
    ]