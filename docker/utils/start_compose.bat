@echo off
@REM 
@REM +==== BEGIN AsperBackend =================+
@REM LOGO: 
@REM ..........####...####..........
@REM ......###.....#.#########......
@REM ....##........#.###########....
@REM ...#..........#.############...
@REM ...#..........#.#####.######...
@REM ..#.....##....#.###..#...####..
@REM .#.....#.##...#.##..##########.
@REM #.....##########....##...######
@REM #.....#...##..#.##..####.######
@REM .#...##....##.#.##..###..#####.
@REM ..#.##......#.#.####...######..
@REM ..#...........#.#############..
@REM ..#...........#.#############..
@REM ...##.........#.############...
@REM ......#.......#.#########......
@REM .......#......#.########.......
@REM .........#####...#####.........
@REM /STOP
@REM PROJECT: AsperBackend
@REM FILE: start_compose.bat
@REM CREATION DATE: 11-10-2025
@REM LAST Modified: 18:21:48 16-10-2025
@REM DESCRIPTION: 
@REM This is the backend server in charge of making the actual website work.
@REM /STOP
@REM COPYRIGHT: (c) Asperguide
@REM PURPOSE: This is the batch version of the launcher to help start the compose instance (providing the required environement for server testing)
@REM // AR
@REM +==== END AsperBackend =================+
@REM 
@REM start_compose.bat - Windows batch equivalent of start_compose.sh
@REM This script will stop any existing compose stack and start it with build.
@REM /**
@REM  * @file start_compose.bat
@REM  * @brief Windows helper to stop and start the project's Docker Compose stack.
@REM  *
@REM  * This batch file mirrors the behavior of `start_compose.sh` for Windows users.
@REM  * It checks for Docker availability, prefers "docker compose" and falls back to
@REM  * "docker-compose" if necessary, ensures env files exist, and launches the
@REM  * compose stack with rebuild.
@REM  *
@REM  * Usage:
@REM  *   start_compose.bat
@REM  *
@REM  * Notes:
@REM  *  - This script assumes it is run from the repository root.
@REM  *  - Administrative privileges may be required depending on Docker setup.
@REM  */

SETLOCAL ENABLEDELAYEDEXPANSION

SET "ENV_PATH=.env"
IF NOT EXIST "%ENV_PATH%" (
  type NUL > "%ENV_PATH%"
  ECHO Notice: %ENV_PATH% not found — Creating an empty file.
)

SET "ENV_PATH=docker\.db.env"
IF NOT EXIST "%ENV_PATH%" (
  type NUL > "%ENV_PATH%"
  ECHO Notice: %ENV_PATH% not found — Creating an empty file.
)

SET "ENV_PATH=docker\.redis.env"
IF NOT EXIST "%ENV_PATH%" (
  type NUL > "%ENV_PATH%"
  ECHO Notice: %ENV_PATH% not found — Creating an empty file.
)

SET "DATABASE_CACHE_DIR=docker\db\data"
IF NOT EXIST "%DATABASE_CACHE_DIR%" (
  mkdir "%DATABASE_CACHE_DIR%"
  echo "Notice: %DATABASE_CACHE_DIR% not found, creating the directory."
)

SET "REDIS_CACHE_DIR=docker\redis\data"
IF NOT EXIST "%REDIS_CACHE_DIR%" (
  mkdir "%REDIS_CACHE_DIR%"
  echo "Notice: %REDIS_CACHE_DIR% not found, creating the directory."
)

:: Compose file path (relative to repo root)
SET "COMPOSE_FILE=docker-compose.yaml"

echo Checking Docker availability...
where docker >nul 2>&1
IF ERRORLEVEL 1 (
  echo Error: docker is not installed or not in PATH.
  EXIT /B 1
)

echo Checking for 'docker compose'...
REM Try to run 'docker compose version' silently
docker compose version >nul 2>&1
IF ERRORLEVEL 0 (
  SET "COMPOSE_CMD=docker compose"
) ELSE (
  where docker-compose >nul 2>&1
  IF ERRORLEVEL 1 (
    echo Error: neither "docker compose" nor "docker-compose" were found.
    EXIT /B 1
  ) ELSE (
    SET "COMPOSE_CMD=docker-compose"
    echo Falling back to %COMPOSE_CMD%
  )
)

echo Stopping any existing docker compose
%COMPOSE_CMD% -f %COMPOSE_FILE% down

echo Starting docker compose
%COMPOSE_CMD% -f %COMPOSE_FILE% up --build

ENDLOCAL
