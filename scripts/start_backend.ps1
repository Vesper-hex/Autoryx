# Starts Autoryx Backend with persistent background worker on port 8000
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Autoryx Automation Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location $BackendDir

if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
}

Write-Host "Launching FastAPI Server on http://127.0.0.1:8000 ..." -ForegroundColor Green
.\venv\Scripts\python run.py
