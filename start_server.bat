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
@REM .........##.##...#####.........
@REM /STOP
@REM PROJECT: AsperBackend
@REM FILE: start_server.bat
@REM CREATION DATE: 04-10-2025
@REM LAST Modified: 23:37:33 18-11-2025
@REM DESCRIPTION: 
@REM This is the backend server in charge of making the actual website work.
@REM /STOP
@REM COPYRIGHT: (c) Asperguide
@REM PURPOSE: The script to start the server on windows
@REM // AR
@REM +==== END AsperBackend =================+
@REM 
REM Optional args: 1) env location (defaults to current dir), 2) env name (defaults to server_env)
set "SYSTEM_ENV_LOCATION=%~1"
if "%SYSTEM_ENV_LOCATION%"=="" set "SYSTEM_ENV_LOCATION=%CD%"

set "SYSTEM_ENV_NAME=%~2"
if "%SYSTEM_ENV_NAME%"=="" set "SYSTEM_ENV_NAME=server_env"

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

python .\backend\src\ --host 0.0.0.0 --port 5000 --debug

call deactivate
