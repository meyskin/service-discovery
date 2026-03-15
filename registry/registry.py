"""
Service Registry - Central store for service instances.
Services register on startup and deregister on shutdown.
Clients query here to discover available instances.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

import time
import threading
from flask import Flask, request, jsonify
from common.log import get_logger

app = Flask(__name__)
log = get_logger("REGISTRY")

# { service_name: [ {id, host, port, registered_at, last_heartbeat} ] }
registry: dict[str, list[dict]] = {}
registry_lock = threading.Lock()

HEARTBEAT_TIMEOUT = 30  # seconds before a service is considered dead


def _prune_dead_services():
    """Background thread: remove instances that missed heartbeats."""
    while True:
        time.sleep(10)
        now = time.time()
        with registry_lock:
            for name in list(registry.keys()):
                alive = []
                for inst in registry[name]:
                    if now - inst["last_heartbeat"] < HEARTBEAT_TIMEOUT:
                        alive.append(inst)
                    else:
                        log.warning("Pruning dead instance %s of %s (no heartbeat for %ds)",
                                    inst["id"], name, int(now - inst["last_heartbeat"]))
                if alive:
                    registry[name] = alive
                else:
                    del registry[name]


@app.route("/register", methods=["POST"])
def register():
    """Register a service instance."""
    data = request.json
    name = data.get("name")
    host = data.get("host")
    port = data.get("port")

    if not all([name, host, port]):
        return jsonify({"error": "name, host, port required"}), 400

    instance_id = f"{host}:{port}"
    now = time.time()

    with registry_lock:
        instances = registry.setdefault(name, [])
        # Update if already registered (re-register)
        for inst in instances:
            if inst["id"] == instance_id:
                inst["last_heartbeat"] = now
                return jsonify({"message": "re-registered", "id": instance_id}), 200

        instances.append({
            "id": instance_id,
            "host": host,
            "port": port,
            "registered_at": now,
            "last_heartbeat": now,
        })

    log.info("Registered %s at %s", name, instance_id)
    return jsonify({"message": "registered", "id": instance_id}), 201


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    """Keep a service instance alive."""
    data = request.json
    name = data.get("name")
    host = data.get("host")
    port = data.get("port")
    instance_id = f"{host}:{port}"

    with registry_lock:
        for inst in registry.get(name, []):
            if inst["id"] == instance_id:
                inst["last_heartbeat"] = time.time()
                return jsonify({"message": "ok"}), 200

    return jsonify({"error": "not registered"}), 404


@app.route("/deregister", methods=["POST"])
def deregister():
    """Remove a service instance from the registry."""
    data = request.json
    name = data.get("name")
    host = data.get("host")
    port = data.get("port")
    instance_id = f"{host}:{port}"

    removed = False
    with registry_lock:
        if name in registry:
            before = len(registry[name])
            registry[name] = [i for i in registry[name] if i["id"] != instance_id]
            removed = before != len(registry[name])
            if not registry[name]:
                del registry[name]

    if removed:
        log.info("Deregistered %s at %s", name, instance_id)
        return jsonify({"message": "deregistered"}), 200
    else:
        return jsonify({"error": "instance not found"}), 404


@app.route("/discover/<service_name>", methods=["GET"])
def discover(service_name):
    """Return all healthy instances of a service."""
    with registry_lock:
        instances = registry.get(service_name, [])

    if not instances:
        return jsonify({"error": f"No instances found for '{service_name}'"}), 404

    return jsonify({"service": service_name, "instances": instances}), 200


@app.route("/services", methods=["GET"])
def list_services():
    """List all registered services and their instances."""
    with registry_lock:
        snapshot = {name: list(insts) for name, insts in registry.items()}
    return jsonify(snapshot), 200


if __name__ == "__main__":
    threading.Thread(target=_prune_dead_services, daemon=True).start()
    log.info("Starting on port 8000")
    app.run(host="0.0.0.0", port=8000)
