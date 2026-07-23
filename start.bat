@echo off
REM Air Quality Framework - Quick Start Script
REM Starts the FastAPI backend and Next.js frontend

setlocal enabledelayedexpansion

echo.
echo ========================================
echo AirQ Zambia - Quick Start
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python is available
echo.

cd /d %~dp0

echo Choose an option:
echo [1] Install dependencies
echo [2] Start Backend Only
echo [3] Start Frontend Only
echo [4] Start Backend + Frontend
echo [5] Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Installing backend dependencies...
    pip install -r requirements.txt
    echo.
    echo Installing frontend dependencies...
    cd frontend && npm install && cd ..
    echo.
    echo Done! Run option [4] to start.
    pause
)

if "%choice%"=="2" (
    echo.
    echo Starting FastAPI Backend at http://localhost:8000
    echo API docs at http://localhost:8000/docs
    echo.
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
)

if "%choice%"=="3" (
    echo.
    echo Starting Next.js Frontend at http://localhost:3000
    echo.
    cd frontend && npm run dev
)

if "%choice%"=="4" (
    echo Starting Backend in new window...
    start "AirQ Backend" cmd /k "cd /d %cd% && uvicorn api:app --reload --host 0.0.0.0 --port 8000"
    timeout /t 3 /nobreak >nul

    echo Starting Frontend in new window...
    start "AirQ Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"

    echo.
    echo Backend:  http://localhost:8000/docs
    echo Frontend: http://localhost:3000
)

if "%choice%"=="5" exit /b 0
endlocal
