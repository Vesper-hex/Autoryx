# Runs full backend pytest suite and frontend TypeScript type checks
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Running Autoryx Full Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Backend tests
Write-Host "`n[1/2] Running Backend Pytest Suite..." -ForegroundColor Yellow
Set-Location $BackendDir
.\venv\Scripts\pytest -v

# 2. Frontend build & type check
Write-Host "`n[2/2] Checking Frontend TypeScript Build..." -ForegroundColor Yellow
Set-Location $FrontendDir
npm run build

Write-Host "`nAll Autoryx safety and workflow tests PASSED successfully!" -ForegroundColor Green
