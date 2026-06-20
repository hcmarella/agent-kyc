from typing import TypedDict
from langgraph.graph import StateGraph, START, END
 
class KYCState(TypedDict):
    customer_name: str
    request: str
    intent: str
    kyc_result: str
    risk_score: int
    decision: str

def classify_intent(state: KYCState):
    return{"intent": "kyc_risk_check"}

def run_kyc_check(state: KYCState):
    return {"kyc_result": "KYC document verification completed"}

def calculate_risk(state: KYCState):
    risk_score = 75 if "test" in state["customer_name"].lower() else 25
    return {"risk_score": risk_score}

def make_decision(state: KYCState):
    decision = "Manual Review Required" if state["risk_score"] >= 70 else "Approved"
    return {"decision": decision}

builder = StateGraph(KYCState)
builder.add_node("classify_intent", classify_intent)
builder.add_node("run_kyc_check", run_kyc_check)
builder.add_node("calculate_risk", calculate_risk)
builder.add_node("make_decision", make_decision)

builder.add_edge(START, "classify_intent")
builder.add_edge("classify_intent", "run_kyc_check")
builder.add_edge("run_kyc_check", "calculate_risk")
builder.add_edge("calculate_risk", "make_decision")
builder.add_edge("make_decision", END)

agent = builder.compile()