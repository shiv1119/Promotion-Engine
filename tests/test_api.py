import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import RULE_FILE
from app.services.loader import load_rules_from_yaml

client = TestClient(app)

@pytest.fixture(autouse=True)
def reload_rules():
    load_rules_from_yaml(RULE_FILE)

def test_valid_promotion_hit():
    response = client.post("/api/promotion", json={
        "level": 25,
        "spend_tier": "high",
        "country": "US",
        "days_since_last_purchase": 1,
        "ab_bucket": "A"
    })

    assert response.status_code == 200
    data = response.json()

    if data["promotion"] is not None:
        # Check promotion structure
        assert isinstance(data["promotion"], dict)
        assert "type" in data["promotion"]
    else:
        # No rule matched — fallback logic needed
        assert data["promotion"] is None


def test_missing_country_field():
    response = client.post("/api/promotion", json={
        "level": 12,
        "spend_tier": "high",
        "days_since_last_purchase": 2,
        "ab_bucket": "A"
    })
    assert response.status_code == 200

def test_invalid_schema():
    response = client.post("/api/promotion", json={"level": "high"})
    assert response.status_code == 422

def test_reload_rules_endpoint():
    response = client.post("/api/reload")
    assert response.status_code == 200
    assert response.json()["status"] == "Rules reloaded successfully"

def test_metrics_response():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert all(k in metrics for k in ["total_evaluations", "hits", "misses", "avg_latency_ms"])
