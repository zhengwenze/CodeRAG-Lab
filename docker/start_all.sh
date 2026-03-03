#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "[CodeRAG-Lab] Starting all services via docker-compose..."
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" up -d
echo "[CodeRAG-Lab] All services started."
