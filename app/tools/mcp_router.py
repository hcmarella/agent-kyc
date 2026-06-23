from app.tools.postgres_tool import get_customer_profile
from app.tools.rag_tool import search_policy_knowledge
from app.tools.snowflake_tool import get_transaction_summary
from app.tools.oracle_tool import get_core_banking_profile


def call_mcp_tools(customer_name: str, request: str) -> dict:
    """
    MCP-style router.
    Later this can call real MCP servers instead of direct Python functions.
    """
    return {
        "postgres_profile": get_customer_profile(customer_name),
        "rag_policy": search_policy_knowledge(request),
        "snowflake_txn": get_transaction_summary(customer_name),
        "oracle_profile": get_core_banking_profile(customer_name)
    }