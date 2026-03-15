"""
Discovery Client - Queries the Service Registry to find a service instance,
then calls it. Demonstrates client-side service discovery with random
load balancing across available instances.
"""

import os
import random
import requests
from log import get_logger

REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8000")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "order-service")
LOCAL_MODE   = os.environ.get("LOCAL_MODE", "1") == "1"  # rewrite hosts to localhost
CALLS        = 6   # number of requests to make

log = get_logger("CLIENT")


def discover(service_name: str) -> list[dict]:
    """Ask the registry for all healthy instances of a service."""
    url = f"{REGISTRY_URL}/discover/{service_name}"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()["instances"]


def call_instance(instance: dict, path: str = "/orders") -> dict:
    """Call a specific service instance."""
    url = f"http://{instance['host']}:{instance['port']}{path}"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()


def main():
    log.info("Service Discovery Client  registry=%s  service=%s",
             REGISTRY_URL, SERVICE_NAME)

    # Step 1 – Discover
    log.info("Querying registry for '%s'...", SERVICE_NAME)
    instances = discover(SERVICE_NAME)
    log.info("Found %d instance(s): %s",
             len(instances), ", ".join(i["id"] for i in instances))

    # When running locally, rewrite Docker hostnames to localhost
    if LOCAL_MODE:
        for inst in instances:
            inst["host"] = "localhost"
        log.info("Local mode: rewriting hosts to localhost")

    # Step 2 – Call random instances (client-side load balancing)
    log.info("Making %d calls (random instance selection)...", CALLS)
    for i in range(1, CALLS + 1):
        chosen = random.choice(instances)
        try:
            result = call_instance(chosen)
            log.info("Call %d -> %s  orders=%d",
                     i, chosen["id"], len(result.get("orders", [])))
        except Exception as e:
            log.error("Call %d -> %s  failed: %s", i, chosen["id"], e)

    log.info("Done.")


if __name__ == "__main__":
    main()
