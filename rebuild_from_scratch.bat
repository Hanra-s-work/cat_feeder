@echo off
@REM 
@REM +==== BEGIN CatFeeder =================+
@REM LOGO: 
@REM ..............(..../\\
@REM ...............)..(.')
@REM ..............(../..)
@REM ...............\\(__)|
@REM Inspired by Joan Stark
@REM source https://www.asciiart.eu/
@REM animals/cats
@REM /STOP
@REM PROJECT: CatFeeder
@REM FILE: rebuild_from_scratch.bat
@REM CREATION DATE: 26-11-2025
@REM LAST Modified: 14:24:27 04-12-2025
@REM DESCRIPTION: 
@REM This is the project in charge of making the connected cat feeder project work.
@REM /STOP
@REM COPYRIGHT: (c) Cat Feeder
@REM PURPOSE: Wrapper script that forwards to the actual implementation in docker\utils\rebuild_from_scratch.bat
@REM // AR
@REM +==== END CatFeeder =================+
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
