#!/usr/bin/env bash
# Run the full demo locally (no Docker required).
# Open three terminals and run this script, or just let it fork processes.

set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

pip install -q -r requirements.txt

echo "==> Starting Service Registry on :8000"
python3 src/registry.py &
REGISTRY_PID=$!
sleep 1

echo "==> Starting order-service instance 1 on :8001"
PORT=8001 HOST=localhost SERVICE_NAME=order-service REGISTRY_URL=http://localhost:8000 \
  python3 src/service.py &
SVC1_PID=$!

echo "==> Starting order-service instance 2 on :8002"
PORT=8002 HOST=localhost SERVICE_NAME=order-service REGISTRY_URL=http://localhost:8000 \
  python3 src/service.py &
SVC2_PID=$!

sleep 2   # let both services register

echo ""
echo "==> Running discovery client"
REGISTRY_URL=http://localhost:8000 python3 src/client.py

echo ""
echo "==> Shutting down..."
kill $SVC1_PID $SVC2_PID 2>/dev/null
wait $SVC1_PID $SVC2_PID 2>/dev/null
kill $REGISTRY_PID 2>/dev/null
wait $REGISTRY_PID 2>/dev/null
echo "Done."
