import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_verify_news_short_input():
    # Less than 10 characters should fail Pydantic validation
    response = client.post("/api/v1/verify", json={"text": "short"})
    assert response.status_code == 422
