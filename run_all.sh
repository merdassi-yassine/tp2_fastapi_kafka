#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
KAFKA_DIR="$ROOT_DIR/kafka_local/kafka_2.13-4.2.0"
KAFKA_CONFIG="$ROOT_DIR/kafka_local/server-tp2.properties"

mkdir -p "$LOG_DIR"

PIDS=()

cleanup() {
  echo
  echo "Stopping services..."

  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
  done

  wait || true
}

trap cleanup EXIT INT TERM

start_process() {
  local name="$1"
  shift

  echo "Starting $name..."
  "$@" >"$LOG_DIR/$name.log" 2>&1 &
  local pid=$!
  PIDS+=("$pid")
  echo "$name started (pid=$pid, log=$LOG_DIR/$name.log)"
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local retries="${3:-30}"

  for ((i = 1; i <= retries; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$name is ready on $url"
      return 0
    fi
    sleep 1
  done

  echo "Failed to reach $name on $url"
  return 1
}

echo "Logs directory: $LOG_DIR"

start_process kafka /bin/bash -lc "cd '$ROOT_DIR' && JMX_PORT='' KAFKA_JMX_OPTS='' ./kafka_local/kafka_2.13-4.2.0/bin/kafka-server-start.sh ./kafka_local/server-tp2.properties"
sleep 8

start_process users_api /bin/bash -lc "cd '$ROOT_DIR' && uvicorn users_service:app --port 8000"
start_process products_api /bin/bash -lc "cd '$ROOT_DIR' && uvicorn products_service:app --port 8001"
start_process products_worker /bin/bash -lc "cd '$ROOT_DIR' && python3 products_service.py"
start_process gateway /bin/bash -lc "cd '$ROOT_DIR' && uvicorn gateway_service:app --port 8002"

wait_for_http "Users API" "http://127.0.0.1:8000/users/1"
wait_for_http "Products API" "http://127.0.0.1:8001/products/1"
wait_for_http "Gateway" "http://127.0.0.1:8002/"

echo
echo "All services are running."
echo "Open: http://127.0.0.1:8002"
echo "Press Ctrl+C to stop everything."

wait
