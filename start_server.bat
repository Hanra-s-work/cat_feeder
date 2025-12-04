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
@REM FILE: start_server.bat
@REM CREATION DATE: 04-10-2025
@REM LAST Modified: 14:22:22 04-12-2025
@REM DESCRIPTION: 
@REM This is the project in charge of making the connected cat feeder project work.
@REM /STOP
@REM COPYRIGHT: (c) Cat Feeder
@REM PURPOSE: The script to start the server on windows
@REM // AR
@REM +==== END CatFeeder =================+
@REM 
REM Optional args: 1) env location (defaults to current dir), 2) env name (defaults to server_env)
REM Additional args after those two are passed to the Python script
set "SYSTEM_ENV_LOCATION=%~1"
if "%SYSTEM_ENV_LOCATION%"=="" set "SYSTEM_ENV_LOCATION=%CD%"

set "SYSTEM_ENV_NAME=%~2"
if "%SYSTEM_ENV_NAME%"=="" set "SYSTEM_ENV_NAME=server_env"

REM Shift to pass remaining args to Python
shift
shift

if exist "%SYSTEM_ENV_LOCATION%\%SYSTEM_ENV_NAME%\Scripts\activate.bat" (
	call "%SYSTEM_ENV_LOCATION%\%SYSTEM_ENV_NAME%\Scripts\activate.bat"
) else (
	if exist ".\server_env\Scripts\activate.bat" (
		call ".\server_env\Scripts\activate.bat"
	) else (
		make create_environement install_dependencies
		if exist ".\server_env\Scripts\activate.bat" (
			call ".\server_env\Scripts\activate.bat"
		) else (
			echo Error: Unable to create or activate environment
			exit /b 1
		)
	)
)

python .\backend\src\ --host 0.0.0.0 --port 5001 --debug %*

call deactivate
