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
@REM FILE: start_compose.bat
@REM CREATION DATE: 11-10-2025
@REM LAST Modified: 3:11:19 04-12-2025
@REM DESCRIPTION: 
@REM This is the project in charge of making the connected cat feeder project work.
@REM /STOP
@REM COPYRIGHT: (c) Cat Feeder
@REM PURPOSE: Wrapper script that forwards to the actual implementation in docker/utils/start_compose.bat
@REM // AR
@REM +==== END CatFeeder =================+
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

