#!/bin/sh
# wait-for-it.sh adapted for BusyBox / Alpine

set -e

HOST=$(printf "%s" "$1" | cut -d: -f1)
PORT=$(printf "%s" "$1" | cut -d: -f2)
shift || true

timeout=${WAIT_FOR_IT_TIMEOUT:-30}

echo "Waiting for $HOST:$PORT (timeout ${timeout}s)..."
for _ in $(seq 1 "$timeout"); do
  if nc -z "$HOST" "$PORT" >/dev/null 2>&1; then
    echo "$HOST:$PORT is available."
    if [ "$#" -gt 0 ]; then
      exec "$@"
    fi
    exit 0
  fi
  sleep 1
done

echo "Timeout waiting for $HOST:$PORT"
exit 1


