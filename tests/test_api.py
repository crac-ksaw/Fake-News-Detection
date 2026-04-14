from fastapi.testclient import TestClient

from backend.api import routes
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


def test_verify_news_success(monkeypatch):
    monkeypatch.setattr(
        routes,
        "analyze_news",
        lambda text: {
            "classification": "REAL",
            "confidence_score": 0.91,
            "reasoning": "- Supported by the model output.",
            "retrieved_context": ["Reuters | Source: reuters.com | Seen: 20260414"],
        },
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": "Scientists confirm a new climate dataset was published today."},
    )

    assert response.status_code == 200
    assert response.json()["classification"] == "REAL"
    assert response.json()["retrieved_context"]


def test_verify_news_internal_error(monkeypatch):
    monkeypatch.setattr(
        routes,
        "analyze_news",
        lambda text: {
            "classification": "ERROR",
            "confidence_score": 0.0,
            "reasoning": "Inference failed: missing API key",
            "retrieved_context": [],
        },
    )

    response = client.post(
        "/api/v1/verify",
        json={"text": "A sufficiently long headline that triggers the endpoint path."},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Inference failed: missing API key"
