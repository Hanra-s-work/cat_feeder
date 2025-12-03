<!-- 
-- +==== BEGIN AsperBackend =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: AsperBackend
-- FILE: README.md
-- CREATION DATE: 16-10-2025
-- LAST Modified: 19:8:39 22-11-2025
-- DESCRIPTION: 
-- This is the backend server in charge of making the actual website work.
-- /STOP
-- COPYRIGHT: (c) Asperguide
-- PURPOSE: The readme file of the project
-- // AR
-- +==== END AsperBackend =================+
-->
# Asperguide backend — Docker Compose helper

 This repository contains the backend for the Asperguide project and helper files to run it via Docker Compose.

 This README explains how to start the compose stack, what components are required, which environment files the project uses, and provides simple examples for Linux and Windows.

## Required components

- Docker (Engine) — install from <https://docs.docker.com/get-docker/>
- Docker Compose v2 (integrated as `docker compose`) or `docker-compose` (v1) fallback

 Optional but recommended:

- Add your user to the `docker` group to avoid using sudo for Docker commands (Linux).

## Files of interest

- `start_compose.sh` — POSIX shell script to start/stop the compose stack (Linux/macOS). Now contains Doxygen-style comments.
- `start_compose.bat` — Windows batch equivalent. Also contains Doxygen-style comments.
- `docker/dockerfile.backend` — Dockerfile used to build the backend image; now annotated with Doxygen-style header comments.
- `.env` and `sample.env` — environment variables used by the server and the image build.
- `docker/.db.env`, `docker/.redis.env` — optional service-specific env files used by the compose config.

## Environment variables

### LAST Modified: 15:43:1 16-10-2025Important variables used at runtime include

- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE — database connection
- REDIS_PASSWORD, REDIS_SOCKET — redis connection
- PORT, HOST — server bind settings (default: PORT=5000, HOST=0.0.0.0)
- DEBUG — whether to launch the server in debug mode
- LOG_SERVER_DATA, LOG_PATH, LOG_DATA — logging configuration

 When running with Docker Compose, the compose file will pick up `.env` from the repository root and the additional files under `docker/` if the compose manifest references them.

## How to start the Docker Compose stack

 Choose the platform you're on.

 Linux / macOS (recommended):

 1. Make sure Docker is installed and your user can access the Docker daemon. If not, run the script with sudo or add your user to the `docker` group.
 2. From the repository root run:

 ```bash
 chmod +x ./start_compose.sh && ./start_compose.sh
 ```

 This script will:

- check Docker and Compose availability
- create `.env`, `docker/.db.env`, `docker/.redis.env` if missing
- create `docker/db/data` and `docker/redis/data` directories if missing
- run `docker compose -f ./docker-compose.yaml down` then
- run `docker compose -f ./docker-compose.yaml up --build`

 If your system does not allow running docker without sudo, the script will try to use `sudo` transparently and prompt for a password if needed.

 Windows (PowerShell / CMD):

 Run from repository root in a Command Prompt:

 ```batch
 start_compose.bat
 ```

 The batch file mirrors the Linux script’s behavior, checks for Docker availability and launches the compose stack. On Windows, administrative privileges may be required depending on your Docker Desktop configuration.

## Notes about the Dockerfile and scripts

- `docker/dockerfile.backend` contains the image build logic. It builds a Python virtual environment inside the image, installs dependencies from `requirements.txt`, and creates a small launcher script to run the server.
- `start_compose.sh`, `start_compose.bat`, and the Dockerfile now include Doxygen-style headers to make it easier to generate documentation or scan file metadata.

## Troubleshooting

- Permission denied while accessing Docker? Add your Linux user to the `docker` group:

 ```bash
 sudo usermod -aG docker $USER
 # then re-login or run: newgrp docker
 ```

- Docker Compose command not found? Install Docker Compose v2 (usually included in modern Docker Desktop/Engine) or install `docker-compose` separately.

- If you changed `PORT` in `.env` and the container binding needs updating, verify `docker-compose.yaml` port mappings match your desired host port.

## Contributions

Please visit [`CONTRIBUTING.md`](./CONTRIBUTING.md) and [`COMMIT_CONVENTION.md`](./COMMIT_CONVENTION.md) to check the rules and norms of the repository.
