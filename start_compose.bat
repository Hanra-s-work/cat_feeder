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
@REM LAST Modified: 1:30:2 26-11-2025
@REM DESCRIPTION: 
@REM This is the backend server in charge of making the actual website work.
@REM /STOP
@REM COPYRIGHT: (c) Asperguide
@REM PURPOSE: Wrapper script that forwards to the actual implementation in docker/utils/start_compose.bat
@REM // AR
@REM +==== END AsperBackend =================+
@REM 
@REM start_compose.bat - Convenience wrapper for the actual script in docker/utils/
@REM /**
@REM  * @file start_compose.bat
@REM  * @brief Convenience wrapper to launch docker/utils/start_compose.bat from the repository root.
@REM  *
@REM  * This script allows users to run start_compose.bat from the repository root directory
@REM  * while the actual implementation lives in docker/utils/. All command-line arguments
@REM  * are forwarded to the actual script.
@REM  *
@REM  * Usage:
@REM  *   start_compose.bat [arguments...]
@REM  *
@REM  * Notes:
@REM  *  - This script must be run from the repository root
@REM  *  - All arguments are passed through to docker\utils\start_compose.bat
@REM  */

IF NOT EXIST "docker\utils\start_compose.bat" (
  echo Error: docker\utils\start_compose.bat not found.
  echo Please ensure you are running this script from the repository root.
  EXIT /B 1
)

REM Forward all arguments to the actual implementation
call "docker\utils\start_compose.bat" %*

