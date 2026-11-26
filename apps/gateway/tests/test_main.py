import httpx
from fastapi.testclient import TestClient

import app.main as main
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_api_orders_ok(monkeypatch):
    async def fake_fetch():
        return 200, {"pod": "orders-1", "version": "v1", "orders": [{"id": 1}]}

    monkeypatch.setattr(main, "fetch_orders", fake_fetch)
    r = client.get("/api/orders")
    assert r.status_code == 200
    assert r.json()["orders_pod"] == "orders-1"


def test_upstream_error_returns_502(monkeypatch):
    async def fake_fetch():
        return 500, {"error": "boom"}

    monkeypatch.setattr(main, "fetch_orders", fake_fetch)
    r = client.get("/api/orders")
    assert r.status_code == 502


def test_upstream_down_returns_502(monkeypatch):
    async def fake_fetch():
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(main, "fetch_orders", fake_fetch)
    r = client.get("/api/orders")
    assert r.status_code == 502
