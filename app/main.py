import logging
from fastapi import FastAPI
from pydantic import BaseModel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.agent_graph import graph
from app.observability.otel import setup_tracing
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response


 

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
REQUEST_COUNT = Counter(
    "agent_kyc_requests_total",
    "Total Agent KYC requests",
    ["environment", "decision"]
)

GUARDRAIL_BLOCK_COUNT = Counter(
    "agent_kyc_guardrail_blocks_total",
    "Total guardrail blocked requests",
    ["environment"]
)

REQUEST_LATENCY = Histogram(
    "agent_kyc_request_latency_seconds",
    "Agent KYC request latency",
    ["environment"]
)


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
    start = time.time()
    env_name = os.getenv("ENV_NAME", "local")

    with tracer.start_as_current_span("agent_kyc_invoke") as span:
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

        decision = result.get("decision", "unknown")
        REQUEST_COUNT.labels(environment=env_name, decision=decision).inc()
        REQUEST_LATENCY.labels(environment=env_name).observe(time.time() - start)

        if not result.get("input_allowed", True) or not result.get("output_allowed", True):
            GUARDRAIL_BLOCK_COUNT.labels(environment=env_name).inc()

        span.set_attribute("agent.decision", decision)
        span.set_attribute("agent.risk_score", result.get("risk_score", 0))

        return result



@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)