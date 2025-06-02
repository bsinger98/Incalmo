#!/bin/bash
set -e

cd /agents
./sandcat.go -server http://$SERVER_IP -group red &

cd /incalmo
uv run ./incalmo/c2server/c2server.py