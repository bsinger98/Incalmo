#!/bin/bash
set -e
set -u
set -o pipefail

# Build attacker images
docker build -t incalmo/attacker_controller:latest -f attacker/attacker_controller.Dockerfile ./attacker
docker build -t incalmo/attacker_host:latest -f attacker/attacker_host.Dockerfile ./attacker

# Build Equifax images
docker build -t incalmo/equifax/webserver:latest -f environment/docker/equifax/webserver/Dockerfile ./environment/docker/equifax/webserver
docker build -t incalmo/equifax/database:latest -f environment/docker/equifax/database/Dockerfile ./environment/docker/equifax/database
