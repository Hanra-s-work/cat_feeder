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
@REM LAST Modified: 1:33:0 26-11-2025
@REM DESCRIPTION: 
@REM This is the backend server in charge of making the actual website work.
@REM /STOP
@REM COPYRIGHT: (c) Asperguide
@REM PURPOSE: Wrapper script that forwards to the actual implementation in docker\utils\rebuild_from_scratch.bat
@REM // AR
@REM +==== END AsperBackend =================+
@REM 
@REM rebuild_from_scratch.bat - Convenience wrapper for the actual script in docker/utils/
@REM /**
@REM  * @file rebuild_from_scratch.bat
@REM  * @brief Convenience wrapper to launch docker\utils\rebuild_from_scratch.bat from the repository root.
@REM  *
@REM  * This script allows users to run rebuild_from_scratch.bat from the repository root directory
@REM  * while the actual implementation lives in docker\utils\. All command-line arguments
@REM  * are forwarded to the actual script.
@REM  *
@REM  * WARNING: This is a destructive script that removes ALL Docker volumes system-wide.
@REM  * See docker\utils\rebuild_from_scratch.bat for details.
@REM  *
@REM  * Usage:
@REM  *   rebuild_from_scratch.bat [arguments...]
@REM  *
@REM  * Notes:
@REM  *  - This script must be run from the repository root
@REM  *  - All arguments are passed through to docker\utils\rebuild_from_scratch.bat
@REM  */

IF NOT EXIST "docker\utils\rebuild_from_scratch.bat" (
  echo Error: docker\utils\rebuild_from_scratch.bat not found.
  echo Please ensure you are running this script from the repository root.
  EXIT /B 1
)

REM Forward all arguments to the actual implementation
call "docker\utils\rebuild_from_scratch.bat" %*
