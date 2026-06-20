def get_transaction_summary(customer_name: str) -> dict:
    # Phase 1: mock Snowflake response
    # Phase 2: replace with snowflake connector query
    return {
        "source": "snowflake",
        "customer_name": customer_name,
        "last_30_day_txn_count": 18,
        "high_value_txn_count": 1,
        "suspicious_pattern": False
    }