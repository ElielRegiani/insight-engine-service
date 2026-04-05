from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


@patch("app.api.routes.get_service")
def test_health(mock_service):
    mock_service.return_value = None
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("app.api.routes.get_service")
def test_explain(mock_get):
    mock_svc = mock_get.return_value
    mock_svc.explain.return_value = {
        "symbol": "PETR4",
        "prediction": "UP",
        "confidence": 0.5,
        "explanation": "ok",
    }
    c = TestClient(app)
    r = c.post("/insight/explain", json={"symbol": "PETR4"})
    assert r.status_code == 200
    assert r.json()["explanation"] == "ok"
