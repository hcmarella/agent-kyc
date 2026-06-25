import logging
from fastapi import FastAPI
from pydantic import BaseModel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.agent_graph import graph
from app.observability.otel import setup_tracing
import os

 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kyc-agent")

tracer = setup_tracing("kyc-agent")

app = FastAPI(title="KYC Agent API")
FastAPIInstrumentor.instrument_app(app)
service_name = os.getenv("OTEL_SERVICE_NAME", "agent-kyc-local")
tracer = setup_tracing(service_name)

FastAPIInstrumentor.instrument_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-kyc")


class AgentRequest(BaseModel):
    customer_name: str
    request: str


@app.get("/health/live")
def live():
    return {"status": "alive"}


@app.get("/health/ready")
def ready():
    return {"status": "ready"}


@app.post("/agent/invoke")
def invoke_agent(payload: AgentRequest):
    logger.info({
        "event": "agent_invoked",
        "customer_name": payload.customer_name
    })

    with tracer.start_as_current_span("agent_kyc_invoke") as span:
        span.set_attribute("customer.name", payload.customer_name)
        span.set_attribute("agent.request", payload.request)

        result = graph.invoke({
            "customer_name": payload.customer_name,
            "request": payload.request,
            "input_allowed": True,
            "input_guardrail_reason": "",
            "intent": "",
            "mcp_results": {},
            "risk_score": 0,
            "decision": "",
            "output_allowed": True,
            "output_guardrail_reason": "",
            "final_response": ""
        })

        span.set_attribute("agent.decision", result.get("decision", ""))
        span.set_attribute("agent.risk_score", result.get("risk_score", 0))
        span.set_attribute("guardrail.output_allowed", result.get("output_allowed", True))

        return result



   