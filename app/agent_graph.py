from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END
from app.tools.mcp_router import call_mcp_tools
from app.guardrails.basic_guardrails import input_guardrail_check, output_guardrail_check


class KYCState(TypedDict):
    customer_name: str
    request: str
    input_allowed: bool
    input_guardrail_reason: str
    intent: str
    mcp_results: Dict[str, Any]
    risk_score: int
    decision: str
    output_allowed: bool
    output_guardrail_reason: str
    final_response: str


def input_guardrail(state: KYCState):
    result = input_guardrail_check(state["request"])
    return {
        "input_allowed": result["allowed"],
        "input_guardrail_reason": result["reason"]
    }


def classify_intent(state: KYCState):
    if not state["input_allowed"]:
        return {"intent": "blocked"}
    return {"intent": "kyc_risk_check"}


def mcp_tool_router(state: KYCState):
    if state["intent"] == "blocked":
        return {"mcp_results": {}}

    results = call_mcp_tools(
        customer_name=state["customer_name"],
        request=state["request"]
    )
    return {"mcp_results": results}


def calculate_risk(state: KYCState):
    if state["intent"] == "blocked":
        return {"risk_score": 100}

    mcp = state["mcp_results"]

    score = 20

    if mcp["postgres_profile"]["kyc_status"] != "verified":
        score += 40

    if mcp["snowflake_txn"]["suspicious_pattern"]:
        score += 50

    if mcp["oracle_profile"]["overdraft_flag"]:
        score += 10

    if "test" in state["customer_name"].lower():
        score += 50

    return {"risk_score": min(score, 100)}


def make_decision(state: KYCState):
    if not state["input_allowed"]:
        return {"decision": "Blocked by input guardrail"}

    decision = "Manual review required" if state["risk_score"] >= 70 else "Approved"
    return {"decision": decision}


def output_guardrail(state: KYCState):
    response_text = f"KYC decision for {state['customer_name']}: {state['decision']}"
    result = output_guardrail_check(response_text)

    return {
        "output_allowed": result["allowed"],
        "output_guardrail_reason": result["reason"],
        "final_response": response_text if result["allowed"] else "Response blocked by output guardrail"
    }


builder = StateGraph(KYCState)

builder.add_node("input_guardrail", input_guardrail)
builder.add_node("classify_intent", classify_intent)
builder.add_node("mcp_tool_router", mcp_tool_router)
builder.add_node("calculate_risk", calculate_risk)
builder.add_node("make_decision", make_decision)
builder.add_node("output_guardrail", output_guardrail)

builder.add_edge(START, "input_guardrail")
builder.add_edge("input_guardrail", "classify_intent")
builder.add_edge("classify_intent", "mcp_tool_router")
builder.add_edge("mcp_tool_router", "calculate_risk")
builder.add_edge("calculate_risk", "make_decision")
builder.add_edge("make_decision", "output_guardrail")
builder.add_edge("output_guardrail", END)

graph = builder.compile()