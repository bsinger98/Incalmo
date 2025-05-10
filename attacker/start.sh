#!/bin/bash
./c2server/agents/sandcat.bin -server http://$SERVER_IP -group red -paw kali &
uv run server.py
