import os
import socket
import time

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = "gateway"
VERSION = os.getenv("APP_VERSION", "dev")
POD = os.getenv("POD_NAME", socket.gethostname())
ORDERS_URL = os.getenv("ORDERS_URL", "http://localhost:8000")
TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "2"))

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"]
)

http_client = httpx.AsyncClient(timeout=TIMEOUT)

app = FastAPI(title=SERVICE)


@app.middleware("http")
async def metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    path = request.url.path
    if path != "/metrics":
        REQUESTS.labels(request.method, path, str(response.status_code)).inc()
        LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
    return response


async def fetch_orders():
    r = await http_client.get(f"{ORDERS_URL}/orders")
    return r.status_code, r.json()


@app.get("/")
def root():
    return {"service": SERVICE, "version": VERSION, "pod": POD, "orders_url": ORDERS_URL}


@app.get("/api/orders")
async def api_orders():
    try:
        status, body = await fetch_orders()
    except (httpx.HTTPError, ValueError) as e:
        return JSONResponse(
            {"error": "orders-api unreachable", "detail": str(e), "gateway_pod": POD},
            status_code=502,
        )
    if status != 200:
        return JSONResponse(
            {"error": "orders-api failed", "upstream_status": status, "gateway_pod": POD},
            status_code=502,
        )
    return {
        "gateway_pod": POD,
        "orders_pod": body["pod"],
        "orders_version": body["version"],
        "orders": body["orders"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
