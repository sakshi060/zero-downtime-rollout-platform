from fastapi.testclient import TestClient

import app.main as main
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_orders_returns_pod_and_items():
    r = client.get("/orders")
    assert r.status_code == 200
    body = r.json()
    assert "pod" in body
    assert len(body["orders"]) == 3


def test_metrics_exposed():
    client.get("/orders")
    r = client.get("/metrics")
    assert "http_requests_total" in r.text


def test_fault_injection(monkeypatch):
    monkeypatch.setattr(main, "FAIL_RATE", 1.0)
    r = client.get("/orders")
    assert r.status_code == 500
