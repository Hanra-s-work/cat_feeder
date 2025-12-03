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
@REM FILE: rebuild_from_scratch.bat
@REM CREATION DATE: 26-11-2025
@REM LAST Modified: 1:26:32 26-11-2025
@REM DESCRIPTION: 
@REM This is the backend server in charge of making the actual website work.
@REM /STOP
@REM COPYRIGHT: (c) Asperguide
@REM PURPOSE: Complete Docker environment rebuild script - stops containers, removes all volumes and cached data, then rebuilds from scratch (Windows version)
@REM // AR
@REM +==== END AsperBackend =================+
@REM 
@REM rebuild_from_scratch.bat - Windows batch equivalent of rebuild_from_scratch.sh
@REM /**
@REM  * @file rebuild_from_scratch.bat
@REM  * @brief Nuclear option: Complete Docker Compose stack rebuild with full cleanup (Windows).
@REM  *
@REM  * This script performs a complete teardown and rebuild of the Docker environment:
@REM  *   1. Stops all running containers from docker-compose.yaml
@REM  *   2. Runs docker system prune to remove all unused containers, networks, images, and volumes
@REM  *   3. Forcefully removes ALL Docker volumes (including those not managed by this project)
@REM  *   4. Rebuilds the Docker Compose stack from scratch with --no-cache
@REM  *   5. Optionally starts the rebuilt stack
@REM  *
@REM  * WARNING: This script is destructive and will delete ALL Docker volumes on your system,
@REM  * not just those related to this project. Use with extreme caution.
@REM  *
@REM  * Usage:
@REM  *   docker\utils\rebuild_from_scratch.bat
@REM  *
@REM  * Notes:
@REM  *  - This script should be run from the repository root
@REM  *  - Administrative privileges may be required depending on Docker setup
@REM  *  - This is useful when the Docker environment is corrupted or you need a clean slate
@REM  *  - Consider using start_compose.bat for normal operations instead
@REM  */

SETLOCAL ENABLEDELAYEDEXPANSION

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

IF NOT EXIST "docker" (
  echo Error: docker folder not found. Please ensure you are running this script from the correct directory.
  EXIT /B 1
)

SET "ENV_PATH=.env"
IF NOT EXIST "%ENV_PATH%" (
  type NUL > "%ENV_PATH%"
  ECHO Notice: %ENV_PATH% not found - Creating an empty file.
)

SET "ENV_PATH=docker\.db.env"
IF NOT EXIST "%ENV_PATH%" (
  type NUL > "%ENV_PATH%"
  ECHO Notice: %ENV_PATH% not found - Creating an empty file.
)

SET "ENV_PATH=docker\.redis.env"
IF NOT EXIST "%ENV_PATH%" (
  type NUL > "%ENV_PATH%"
  ECHO Notice: %ENV_PATH% not found - Creating an empty file.
)

SET "DATABASE_CACHE_DIR=docker\db\data"
IF NOT EXIST "%DATABASE_CACHE_DIR%" (
  mkdir "%DATABASE_CACHE_DIR%"
  echo Notice: %DATABASE_CACHE_DIR% not found, creating the directory.
)

SET "REDIS_CACHE_DIR=docker\redis\data"
IF NOT EXIST "%REDIS_CACHE_DIR%" (
  mkdir "%REDIS_CACHE_DIR%"
  echo Notice: %REDIS_CACHE_DIR% not found, creating the directory.
)

:: Compose file path (relative to repo root)
SET "COMPOSE_FILE=docker-compose.yaml"

echo.
echo WARNING: This script will DELETE ALL Docker volumes on your system!
echo This is a destructive operation that cannot be undone.
echo.
SET /P CONFIRM="Are you sure you want to continue? (yes/no): "
IF /I NOT "%CONFIRM%"=="yes" (
  echo Operation cancelled.
  EXIT /B 0
)

echo.
echo Stopping any existing docker compose...
%COMPOSE_CMD% -f %COMPOSE_FILE% down

echo.
echo Cleaning up docker resources...
echo Running system prune (this may take a while)...
docker system prune -fa --volumes

echo.
echo Removing all Docker volumes...
FOR /F "tokens=*" %%V IN ('docker volume ls -q') DO (
  echo Removing volume: %%V
  docker volume rm -f "%%V" 2>nul
)

echo.
echo Building docker compose with no cache...
%COMPOSE_CMD% -f %COMPOSE_FILE% build --no-cache

echo.
echo Docker compose rebuild complete.
echo.
SET /P START_NOW="Do you wish to start the docker compose now? (y/n): "
IF /I "%START_NOW%"=="y" (
  echo Starting docker compose...
  %COMPOSE_CMD% -f %COMPOSE_FILE% up --build
) ELSE (
  echo Docker compose build complete. You can start it later with start_compose.bat or '%COMPOSE_CMD% up' command.
)

ENDLOCAL
