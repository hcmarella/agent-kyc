BLOCKED_TERMS = [
    "ignore previous instructions",
    "bypass policy",
    "delete customer",
    "drop table",
    "disable audit"
]


def input_guardrail_check(user_text: str) -> dict:
    lowered = user_text.lower()

    for term in BLOCKED_TERMS:
        if term in lowered:
            return {
                "allowed": False,
                "reason": f"Blocked unsafe input: {term}"
            }

    return {
        "allowed": True,
        "reason": "Input allowed"
    }


def output_guardrail_check(response_text: str) -> dict:
    if "ssn" in response_text.lower():
        return {
            "allowed": False,
            "reason": "Potential sensitive data exposure"
        }

    return {
        "allowed": True,
        "reason": "Output allowed"
    }