#!/bin/bash
set -e
set -u
set -o pipefail

# Build Equifax images
docker build -t incalmo/equifax/webserver:latest -f equifax/webserver/Dockerfile ./equifax/webserver
docker build -t incalmo/equifax/database:latest -f equifax/database/Dockerfile ./equifax/database
