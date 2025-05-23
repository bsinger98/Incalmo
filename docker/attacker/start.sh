#!/bin/bash
set -e

./incalmo/c2server/agents/sandcat.go -server http://$SERVER_IP -group red -paw kali &
uv run ./incalmo/c2server/c2server.py