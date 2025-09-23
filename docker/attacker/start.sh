#!/bin/bash
set -e

if [ "$MODE" == "docker" ]; then
  cd /agents
  ./sandcat.go -server http://$SERVER_IP:8888 -group red &
fi


cd /incalmo
uv run celery -A incalmo.c2server.celery.celery_worker worker --concurrency=1 &
sleep 3
uv run ./incalmo/c2server/c2server.py