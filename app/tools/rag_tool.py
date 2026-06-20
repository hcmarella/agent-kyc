def search_policy_knowledge(request: str) -> dict:
    # Phase 1: mock RAG response
    # Phase 2: replace with pgvector/OpenSearch/Pinecone
    return {
        "source": "rag",
        "matched_policy": "KYC-RISK-POLICY-001",
        "summary": "Customers with verified KYC and low risk score can be approved automatically."
    }