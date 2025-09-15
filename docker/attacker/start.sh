#!/bin/bash
set -e

echo "Waiting for RabbitMQ to be ready..."
until curl -s -u guest:guest http://rabbitmq:15672/api/aliveness-test/%2F > /dev/null 2>&1; do
    echo "RabbitMQ not ready yet, waiting..."
    sleep 5
done
echo "RabbitMQ is ready!"

if [ "$MODE" == "docker" ]; then
  cd /agents
  ./sandcat.go -server http://$SERVER_IP:8888 -group red &
fi


cd /incalmo
uv run celery -A incalmo.c2server.celery.celery_worker worker --concurrency=1 &
sleep 3
uv run ./incalmo/c2server/c2server.py