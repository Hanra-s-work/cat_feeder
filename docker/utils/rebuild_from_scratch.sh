#!/bin/bash
# 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: rebuild_from_scratch.sh
# CREATION DATE: 16-10-2025
# LAST Modified: 1:21:16 26-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Complete Docker environment rebuild script - stops containers, removes all volumes and cached data, then rebuilds from scratch
# // AR
# +==== END CatFeeder =================+
# 
#
# @file rebuild_from_scratch.sh
# @brief Nuclear option: Complete Docker Compose stack rebuild with full cleanup (Linux/macOS).
#
# This script performs a complete teardown and rebuild of the Docker environment:
#   1. Stops all running containers from docker-compose.yaml
#   2. Runs docker system prune to remove all unused containers, networks, images, and volumes
#   3. Forcefully removes ALL Docker volumes (including those not managed by this project)
#   4. Rebuilds the Docker Compose stack from scratch with --no-cache
#   5. Optionally starts the rebuilt stack
#
# WARNING: This script is destructive and will delete ALL Docker volumes on your system,
# not just those related to this project. Use with extreme caution.
#
# @author Cat Feeder
# @date 2025-10-16
#
# Usage:
#   ./docker/utils/rebuild_from_scratch.sh
#
# Notes:
#  - This script should be run from the repository root
#  - It will try to run Docker without sudo first, falling back to sudo if needed
#  - The compose file is expected at `./docker-compose.yaml`
#  - This is useful when the Docker environment is corrupted or you need a clean slate
#  - Consider using start_compose.sh for normal operations instead

set -euo pipefail

echo "Checking docker and compose availability..."

SUDO=""

check_docker_no_sudo() {
	docker info > /dev/null 2>&1
}

if ! command -v docker > /dev/null 2>&1; then
	echo "Error: docker is not installed or not in PATH." >&2
	exit 1
fi

if ! check_docker_no_sudo; then
	if command -v sudo > /dev/null 2>&1 && sudo -n true 2>/dev/null; then
		if sudo docker info > /dev/null 2>&1; then
			SUDO="sudo "
			echo "Using sudo for docker commands"
		fi
	else
		if command -v sudo > /dev/null 2>&1 && sudo docker info > /dev/null 2>&1; then
			SUDO="sudo "
			echo "Using sudo for docker commands (password may be prompted)"
		else
			echo "Warning: current user cannot access docker daemon and sudo docker failed or is unavailable." >&2
			echo "You may need to add your user to the 'docker' group or run this script with appropriate privileges." >&2
		fi
	fi
fi

COMPOSE_CMD="docker compose"
if ! ${SUDO}${COMPOSE_CMD} version > /dev/null 2>&1; then
	if command -v docker-compose > /dev/null 2>&1; then
		COMPOSE_CMD="docker-compose"
		echo "Falling back to: ${COMPOSE_CMD}"
	else
		echo "Error: neither 'docker compose' nor 'docker-compose' is available." >&2
		exit 1
	fi
fi

COMPOSE_FOLDER="./docker"
if [ ! -d "$COMPOSE_FOLDER" ]; then
	echo "Error: $COMPOSE_FOLDER folder not found. Please ensure you are running this script from the correct directory." >&2
	exit 1
fi

ENV_FILE="./.env"
if [ ! -f "$ENV_FILE" ]; then
	touch "$ENV_FILE"
	echo "Notice: $ENV_FILE not found, creating an empty $ENV_FILE file."
fi
ENV_FILE="./docker/.db.env"
if [ ! -f "$ENV_FILE" ]; then
	touch "$ENV_FILE"
	echo "Notice: $ENV_FILE not found, creating an empty $ENV_FILE file."
fi
ENV_FILE="./docker/.redis.env"
if [ ! -f "$ENV_FILE" ]; then
	touch "$ENV_FILE"
	echo "Notice: $ENV_FILE not found, creating an empty $ENV_FILE file."
fi

DATABASE_CACHE_DIR="./docker/db/data"
if [ ! -d "$DATABASE_CACHE_DIR" ]; then
	mkdir -p "$DATABASE_CACHE_DIR"
	echo "Notice: $DATABASE_CACHE_DIR not found, creating the directory."
fi

REDIS_CACHE_DIR="./docker/redis/data"
if [ ! -d "$REDIS_CACHE_DIR" ]; then
	mkdir -p "$REDIS_CACHE_DIR"
	echo "Notice: $REDIS_CACHE_DIR not found, creating the directory."
fi


COMPOSE_FILE="./docker-compose.yaml"
echo "Stopping any existing docker compose"
eval ${SUDO}${COMPOSE_CMD} -f ${COMPOSE_FILE} down
echo "Cleaning up any docker ressources"
echo "Running a system prune"
eval ${SUDO}docker system prune -fa --volumes
echo "Removing any volumes"
ALL_CONTAINERS_VOLUMES=$(eval ${SUDO}docker volume ls -q)
echo "Located volumes: $ALL_CONTAINERS_VOLUMES"
echo "Removing volumes..."
for volume in $ALL_CONTAINERS_VOLUMES; do
    echo "Removing volume: $volume"
    eval ${SUDO}docker volume rm -f "$volume"
done
echo "Building docker compose"
eval ${SUDO}${COMPOSE_CMD} -f ${COMPOSE_FILE} build --no-cache
echo "Do you wish to start the docker compose now? (y/n)"
read -r START_NOW
if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    echo "Starting docker compose"
    eval ${SUDO}${COMPOSE_CMD} -f ${COMPOSE_FILE} up --build
else
    echo "Docker compose build complete. You can start it later with the start_compose or '${SUDO}${COMPOSE_CMD} up' command."
fi
