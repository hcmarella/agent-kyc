from fastapi import FastAPI
from pydantic import BaseModel
from app.agent_graph import agent as graph

app = FastAPI(title="Agent KYC")

class AgentRequest(BaseModel):
    customer_name: str
    request: str

@app.get("/health/live")
def live():
    return {"status": "Alive"}
    
@app.get("/health/ready")
def ready():
    return {"status": "Ready"}

@app.post("/agent/invoke")
def invoke_agent(payload: AgentRequest):
    result = graph.invoke({
        "customer_name": payload.customer_name,
        "request": payload.request,
        "intent": " ",
        "kyc_result": " ",
        "risk_score": 0,
        "decision": " "
    })
    return result