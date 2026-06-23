import logging
from fastapi import FastAPI
from pydantic import BaseModel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.agent_graph import graph
from app.observability.otel import setup_tracing
 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kyc-agent")

tracer = setup_tracing("kyc-agent")

app = FastAPI(title="KYC Agent API")
FastAPIInstrumentor.instrument_app(app)


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
        "customer_name": payload.customer_name,
        "request": payload.request
    })

    with tracer.start_as_current_span("kyc_agent") as span:
        span.set_attribute("agent.customer_name", payload.customer_name)
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

        span.set_attribute("agent.decision", result["decision"])
        span.set_attribute("agent.risk_score", result["risk_score"])
        span.set_attribute("agent.output_allowed", result["output_allowed"])

        logger.info({
            "event": "agent_completed",
            "customer_name": payload.customer_name,
            "decision": result["decision"],
            "risk_score": result["risk_score"],
            "output_allowed": result["output_allowed"]
        })

        return result