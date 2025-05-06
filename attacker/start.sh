#!/bin/bash
uv run /server/server.py &
/tmp/sandcat.bin -server http://$SERVER_IP -group red -paw kali