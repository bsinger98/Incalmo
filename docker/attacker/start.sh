#!/bin/bash
set -e

redis-server --daemonize yes --port 6379 --bind 0.0.0.0

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
until redis-cli ping > /dev/null 2>&1; do
    echo "Redis not ready yet, waiting..."
    sleep 1
done
echo "Redis is ready!"

if [ "$MODE" == "docker" ]; then
  cd /agents
  ./sandcat.go -server http://$SERVER_IP:8888 -group red &
fi


cd /incalmo
uv run celery -A incalmo.c2server.celery.celery_worker worker --concurrency=1 &
uv run celery -A incalmo.c2server.celery.celery_worker beat &
sleep 3
uv run ./incalmo/c2server/c2server.py