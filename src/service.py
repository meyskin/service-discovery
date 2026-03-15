"""
Order Service - A sample microservice.
On startup it registers with the Service Registry.
Sends periodic heartbeats to stay alive in the registry.
On shutdown it deregisters cleanly.
"""

import sys
import os
import time
import signal
import threading
import requests
from flask import Flask, jsonify
from log import get_logger

app = Flask(__name__)

# Config from environment (makes it easy to run two instances)
PORT = int(os.environ.get("PORT", 8001))
HOST = os.environ.get("HOST", "localhost")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "order-service")
REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8000")
HEARTBEAT_INTERVAL = 10  # seconds

log = get_logger(f"{SERVICE_NAME}:{PORT}")


def register():
    payload = {"name": SERVICE_NAME, "host": HOST, "port": PORT}
    for attempt in range(1, 4):
        try:
            r = requests.post(f"{REGISTRY_URL}/register", json=payload, timeout=5)
            log.info("Registered with registry: %s", r.json())
            return
        except Exception as e:
            log.error("Registration attempt %d/3 failed: %s", attempt, e)
            if attempt < 3:
                time.sleep(2)
    log.error("Could not register after 3 attempts")


def deregister():
    payload = {"name": SERVICE_NAME, "host": HOST, "port": PORT}
    try:
        requests.post(f"{REGISTRY_URL}/deregister", json=payload, timeout=5)
        log.info("Deregistered from registry")
    except Exception as e:
        log.error("Deregistration failed: %s", e)


def heartbeat_loop():
    payload = {"name": SERVICE_NAME, "host": HOST, "port": PORT}
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        try:
            requests.post(f"{REGISTRY_URL}/heartbeat", json=payload, timeout=5)
            log.debug("Heartbeat sent")
        except Exception as e:
            log.warning("Heartbeat failed: %s", e)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({
        "service": SERVICE_NAME,
        "instance": f"{HOST}:{PORT}",
        "message": f"Hello from {SERVICE_NAME} running on port {PORT}!",
    })


@app.route("/orders")
def orders():
    """Sample business endpoint."""
    return jsonify({
        "instance": f"{HOST}:{PORT}",
        "orders": [
            {"id": "ORD-001", "item": "Laptop", "status": "shipped"},
            {"id": "ORD-002", "item": "Mouse",  "status": "pending"},
        ],
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "instance": f"{HOST}:{PORT}"}), 200


# ── Startup / shutdown ───────────────────────────────────────────────────────

def handle_shutdown(sig, frame):
    deregister()
    sys.exit(0)


if __name__ == "__main__":
    register()

    # Heartbeat thread keeps the registry entry alive
    t = threading.Thread(target=heartbeat_loop, daemon=True)
    t.start()

    signal.signal(signal.SIGINT,  handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    log.info("Service starting on port %d", PORT)
    app.run(host="0.0.0.0", port=PORT)
