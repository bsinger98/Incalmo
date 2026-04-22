#!/bin/bash
set -e

if [ "$MODE" == "docker" ]; then
  cd /agents
  ./sandcat.go -server http://$SERVER_IP:8888 -group red &
fi

CELERY_STATE_DIR="/tmp/celery_state"
mkdir -p "$CELERY_STATE_DIR"
chmod 777 "$CELERY_STATE_DIR"

cd /incalmo

msfrpcd -P password &

uv run celery -A incalmo.c2server.celery.celery_worker worker \
  --concurrency=1 \
  --statedb "$CELERY_STATE_DIR/celery.db" &

uv run celery -A incalmo.c2server.celery.celery_worker beat \
  --schedule "$CELERY_STATE_DIR/celerybeat-schedule" &
  
sleep 3
uv run ./incalmo/c2server/c2server.py