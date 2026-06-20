def get_customer_profile(customer_name: str) -> dict:
    # Phase 1: mock Postgres response
    # Phase 2: replace with real psycopg2/sqlalchemy query
    return {
        "source": "postgres",
        "customer_name": customer_name,
        "customer_type": "retail",
        "kyc_status": "verified",
        "relationship_years": 3
    }