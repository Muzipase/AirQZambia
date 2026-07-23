# AirQ Zambia - Quick Start Script
# Starts the FastAPI backend and Next.js frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AirQ Zambia - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "Python found: $pythonCheck" -ForegroundColor Green
Write-Host ""

$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

Write-Host "[1] Install dependencies" -ForegroundColor White
Write-Host "[2] Start Backend Only" -ForegroundColor White
Write-Host "[3] Start Frontend Only" -ForegroundColor White
Write-Host "[4] Start Backend + Frontend" -ForegroundColor White
Write-Host "[5] Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        pip install -r requirements.txt
        Push-Location frontend; npm install; Pop-Location
        Write-Host "Done!" -ForegroundColor Green
    }
    "2" {
        uvicorn api:app --reload --host 0.0.0.0 --port 8000
    }
    "3" {
        Push-Location frontend; npm run dev; Pop-Location
    }
    "4" {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; uvicorn api:app --reload --host 0.0.0.0 --port 8000"
        Start-Sleep -Seconds 3
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; npm run dev"
        Write-Host "Backend:  http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    }
    "5" { exit 0 }
}
