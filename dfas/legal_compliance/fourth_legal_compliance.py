from dfas.dfa import Node, Transition, FunctionCall, FunctionArgument

G0 = Node(name="G0")
G1 = Node(name="G1")
G2 = Node(name="G2", is_final=True)

alphabet: dict[str, FunctionCall] = {
    "A": FunctionCall(
        name="check_compliance",
        arguments={
            "doc_name": FunctionArgument(
                name="doc_name",
                value="terms_of_service",
                excluded_values=None,
                type="str",
            ),
            "statement": FunctionArgument(
                name="statement",
                value="Users must not engage in fraudulent activities",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "A'": FunctionCall(
        name="check_compliance",
        arguments={
            "doc_name": FunctionArgument(
                name="doc_name",
                value=None,
                excluded_values=["terms_of_service"],
                type="str",
            ),
            "statement": FunctionArgument(
                name="statement",
                value=None,
                excluded_values=["Users must not engage in fraudulent activities"],
                type="str",
            ),
        },
    ),
    "B": FunctionCall(
        name="flag_violation",
        arguments={
            "issue": FunctionArgument(
                name="issue",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "C": FunctionCall(
        name="approve_policy",
        arguments={
            "statement": FunctionArgument(
                name="statement",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "D": FunctionCall(
        name="request_consent",
        arguments={
            "user_id": FunctionArgument(
                name="user_id",
                value=None,
                excluded_values=None,
                type="str",
            ),
            "reason": FunctionArgument(
                name="reason",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "E": FunctionCall(
        name="generate_audit_report",
        arguments={
            "doc_name": FunctionArgument(
                name="doc_name",
                value=None,
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "F": FunctionCall(
        name="enforce_compliance",
        arguments={
            "doc_name": FunctionArgument(
                name="doc_name",
                value="terms_of_service",
                excluded_values=None,
                type="str",
            ),
            "issue": FunctionArgument(
                name="issue",
                value="Fraudulent activity detected",
                excluded_values=None,
                type="str",
            ),
        },
    ),
    "F'": FunctionCall(
        name="enforce_compliance",
        arguments={
            "doc_name": FunctionArgument(
                name="doc_name",
                value=None,
                excluded_values=["terms_of_service"],
                type="str",
            ),
            "issue": FunctionArgument(
                name="issue",
                value=None,
                excluded_values=["Fraudulent activity detected"],
                type="str",
            ),
        },
    ),
}

G0.transitions = [
    Transition(symbols=["A'"], _from=G0, _to=G0),
    Transition(symbols=["A"], _from=G0, _to=G1),
]

G1.transitions = [
    Transition(symbols=["A", "A'"], _from=G1, _to=G1),
    Transition(symbols=["F"], _from=G1, _to=G2),
]

G2.transitions = [
    Transition(symbols=["A", "A'"], _from=G2, _to=G2),
]
