#!/bin/bash
./c2_server/agents/sandcat.bin -server http://$SERVER_IP -group red -paw kali &
uv run ./c2_server/server.py