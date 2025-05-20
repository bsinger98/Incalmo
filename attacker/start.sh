#!/bin/bash
./c2server/agents/sandcat.go -server http://$SERVER_IP -group red -paw kali &
uv run ./c2server/c2server.py