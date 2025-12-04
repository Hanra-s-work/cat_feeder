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
# FILE: start_compose.sh
# CREATION DATE: 16-10-2025
# LAST Modified: 18:21:33 16-10-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: This is the readme file of the repository to help explain it's aim and how to use it
# // AR
# +==== END CatFeeder =================+
# 
#
# @file start_compose.sh
# @brief Simple helper script to start the project's Docker Compose stack (Linux/macOS).
#
# This file contains safety checks for Docker and Compose, ensures required env files
# and cache directories exist, and then runs `docker compose up --build` (or
# `docker-compose up --build` as a fallback). The script is intended to be run from
# the repository root.
#
# @author Cat Feeder
# @date 2025-10-16
#
# Usage:
#   ./start_compose.sh
#
# Notes:
#  - The script will try to run Docker without sudo first. If that fails and sudo is
#    available, it will attempt to use sudo for Docker commands.
#  - The compose file is expected at `./docker-compose.yaml` and compose assets under
#    `./docker`.

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
echo "Starting docker compose"
eval ${SUDO}${COMPOSE_CMD} -f ${COMPOSE_FILE} up --build
