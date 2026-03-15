# Service Discovery — Demo Script

## Prerequisites

- Docker Desktop running
- Terminal open in the project root

## Step 1: Show the Code Structure

```bash
ls src/
# registry.py   — Service registry (port 8000)
# service.py    — Order service (instances on 8001, 8002)
# client.py     — Discovery client
```

Optionally open `docker-compose.yml` to show the 3 containers defined:
- `registry` on port 8000
- `order-service-1` on port 8001
- `order-service-2` on port 8002

## Step 2: Start Services with Docker Compose

```bash
docker compose up --build
```

Wait for logs showing:
- `REGISTRY` starting on port 8000
- `order-service:8001` registered with registry
- `order-service:8002` registered with registry

Both instances send heartbeats every 10 seconds.

## Step 3: Verify Registration (new terminal)

```bash
curl -s http://localhost:8000/services | python3 -m json.tool
```

Shows both instances (`order-service-1:8001`, `order-service-2:8002`) in the registry catalog.

## Step 4: Demonstrate Discovery

```bash
curl -s http://localhost:8000/discover/order-service | python3 -m json.tool
```

Returns both instances under the logical name `order-service` — this is the endpoint the client uses.

## Step 5: Run the Discovery Client

```bash
REGISTRY_URL=http://localhost:8000 python3 src/client.py
```

The client:
1. Queries the registry for `order-service`
2. Discovers 2 instances
3. Makes 6 calls, picking a **random instance** each time

Calls are distributed across both `:8001` and `:8002`.

## Step 6: Show Heartbeat / Resilience

```bash
# Stop one service instance
docker compose stop order-service-2

# Wait ~35s for the registry to prune it (heartbeat timeout is 30s)
sleep 35

# Discover again — only the surviving instance remains
curl -s http://localhost:8000/discover/order-service | python3 -m json.tool

# Run client again — now only hits the surviving instance
REGISTRY_URL=http://localhost:8000 python3 src/client.py
```

## Step 7: Clean Up

```bash
docker compose down
```

## Key Talking Points

- **Naming**: logical name `order-service` maps to dynamic host:port addresses
- **Client-side discovery**: client queries registry, selects instance (Pattern 1 from slides)
- **Heartbeat**: services send heartbeats every 10s; registry prunes after 30s of silence
- **Random load balancing**: `random.choice` distributes calls across instances
- **Resilience**: dead instances are automatically removed from the registry
