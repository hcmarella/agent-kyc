from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ready_health():
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
