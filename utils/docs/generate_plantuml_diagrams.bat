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
@REM FILE: generate_plantuml_diagrams.bat
@REM CREATION DATE: 02-12-2025
@REM LAST Modified: 3:16:18 04-12-2025
@REM DESCRIPTION: 
@REM This is the project in charge of making the connected cat feeder project work.
@REM /STOP
@REM COPYRIGHT: (c) Cat Feeder
@REM PURPOSE: The batch file in charge of rendering plantUML diagrams to a more common format such as png, svg, pdf etc
@REM // AR
@REM +==== END CatFeeder =================+
@REM 

setlocal enabledelayedexpansion

REM Configuration
set PORT=8082
set CONTAINER_NAME=plantuml
set IMAGE_NAME=plantuml/plantuml-server:jetty
set DOCS_DIR=.
set SERVER_URL=http://127.0.0.1:%PORT%

echo ================================================================
echo    PlantUML Diagram Generator - Cat Feeder Backend
echo ================================================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running or not installed
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Stop and remove existing container
echo [1/5] Stopping existing PlantUML container...
docker ps -a --format "{{.Names}}" | findstr /x "%CONTAINER_NAME%" >nul 2>&1
if not errorlevel 1 (
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker container rm %CONTAINER_NAME% >nul 2>&1
    echo [OK] Stopped and removed existing container
) else (
    echo [OK] No existing container found
)
echo.

REM Pull latest image
echo [2/5] Pulling latest PlantUML server image...
docker pull %IMAGE_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to pull image
    pause
    exit /b 1
)
echo [OK] Image pulled successfully
echo.

REM Start new container
echo [3/5] Starting PlantUML server container...
docker run -d -p %PORT%:8080 --name %CONTAINER_NAME% %IMAGE_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to start container
    pause
    exit /b 1
)
echo [OK] Container started on port %PORT%
echo.

REM Wait for server to be ready
echo [4/5] Waiting for PlantUML server to be ready...
set /a attempts=0
:wait_loop
set /a attempts+=1
if %attempts% gtr 30 (
    echo [ERROR] Server failed to start within 30 seconds
    pause
    exit /b 1
)
curl -s "%SERVER_URL%/svg/" >nul 2>&1
if errorlevel 1 (
    echo|set /p="."
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
echo.
echo [OK] Server is ready
echo.

REM Generate diagrams
echo [5/5] Generating diagrams from PlantUML files...
echo.

REM Change to docs directory
cd /d "%~dp0%DOCS_DIR%"
if errorlevel 1 (
    echo [ERROR] Cannot find manual_documentation directory
    pause
    exit /b 1
)

set /a total=0
set /a success=0
set /a failed=0

REM Count total files
for /r %%f in (*.puml) do set /a total+=1

REM Process all .puml files
set /a current=0
for /r %%f in (*.puml) do (
    set /a current+=1
    set "file=%%f"
    set "dir=%%~dpf"
    set "base=%%~nf"
    
    echo [!current!/%total%] Processing: %%~nxf
    
    REM Generate PNG
    curl -s -X POST --data-binary @"!file!" "%SERVER_URL%/png/" -o "!dir!!base!.png" >nul 2>&1
    if errorlevel 1 (
        echo   [FAIL] PNG failed
        set /a failed+=1
    ) else (
        echo   [OK] PNG created
        
        REM Generate SVG
        curl -s -X POST --data-binary @"!file!" "%SERVER_URL%/svg/" -o "!dir!!base!.svg" >nul 2>&1
        if errorlevel 1 (
            echo   [FAIL] SVG failed
            set /a failed+=1
        ) else (
            echo   [OK] SVG created
            
            REM Generate PDF (if supported)
            curl -s -X POST --data-binary @"!file!" "%SERVER_URL%/pdf/" -o "!dir!!base!.pdf" >nul 2>&1
            if errorlevel 1 (
                echo   [WARN] PDF not supported by server
            ) else (
                REM Check if it's a valid PDF
                findstr /c:"PDF" "!dir!!base!.pdf" >nul 2>&1
                if errorlevel 1 (
                    echo   [WARN] PDF not supported by server
                    del "!dir!!base!.pdf" >nul 2>&1
                ) else (
                    echo   [OK] PDF created
                )
            )
            
            set /a success+=1
        )
    )
)

echo.
echo ================================================================
echo    Generation Summary
echo ================================================================
echo [OK] Successfully processed: %success%/%total%
if %failed% gtr 0 (
    echo [FAIL] Failed: %failed%/%total%
)
echo.
echo All diagrams have been generated in manual_documentation\
echo PlantUML server is running on %SERVER_URL%
echo To stop: docker stop %CONTAINER_NAME%
echo.
pause
