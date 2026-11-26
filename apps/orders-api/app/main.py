import os
import random
import socket
import time

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = "orders-api"
VERSION = os.getenv("APP_VERSION", "dev")
POD = os.getenv("POD_NAME", socket.gethostname())
FAIL_RATE = float(os.getenv("FAIL_RATE", "0"))

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"]
)

ORDERS = [
    {"id": 1, "item": "keyboard", "qty": 1},
    {"id": 2, "item": "mouse", "qty": 2},
    {"id": 3, "item": "monitor", "qty": 1},
]

app = FastAPI(title=SERVICE)


@app.middleware("http")
async def metrics_and_faults(request: Request, call_next):
    start = time.perf_counter()
    path = request.url.path

    if path.startswith("/orders") and random.random() < FAIL_RATE:
        response = JSONResponse({"error": "injected failure", "pod": POD}, status_code=500)
    else:
        response = await call_next(request)

    if path != "/metrics":
        REQUESTS.labels(request.method, path, str(response.status_code)).inc()
        LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
    return response


@app.get("/")
def root():
    return {"service": SERVICE, "version": VERSION, "pod": POD}


@app.get("/orders")
def list_orders():
    return {"pod": POD, "version": VERSION, "orders": ORDERS}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
