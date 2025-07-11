@echo off
title NeoMag Server Launcher

echo Starting NeoMag Server...
echo.

REM Change directory to the script's location (project root)
cd /D "%~dp0"

REM Activate virtual environment if it exists
set VENV_PATH=server\venv\Scripts\activate.bat
if exist "%VENV_PATH%" (
    echo Activating Python virtual environment...
    call %VENV_PATH%
    echo.

    REM Check if dependencies are already installed to speed up launch
    set LOCK_FILE=server\venv\.packages_installed
    if exist "%LOCK_FILE%" (
        echo Dependencies are assumed to be installed. Skipping check.
        echo (To force re-installation, delete the file: %LOCK_FILE%)
        echo.
    ) else (
        echo Installing/Verifying dependencies from server/requirements.txt...
        pip install -r server/requirements.txt
        echo.
        echo Creating lock file to speed up next launch...
        echo Installed on %DATE% %TIME% > "%LOCK_FILE%"
        echo.
    )
) else (
    echo WARNING: Virtual environment not found at %VENV_PATH%.
    echo Assuming Python dependencies are installed globally.
    echo Installing/Verifying dependencies globally...
    pip install -r server/requirements.txt
    echo.
)

echo =================================================================
echo Launching Uvicorn server...
echo URL: http://127.0.0.1:8001
echo Mode: Auto-reload enabled
echo Press CTRL+C in this window to stop the server.
echo =================================================================
echo.

uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload

echo.
echo Server has been shut down.
pause 