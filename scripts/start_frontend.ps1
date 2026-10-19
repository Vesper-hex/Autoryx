# Starts Autoryx Frontend Vite dev server on port 5173
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $RootDir "frontend"

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Starting Autoryx Developer Frontend" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

Set-Location $FrontendDir

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "Launching Vite dev server on http://localhost:5173 ..." -ForegroundColor Green
npm run dev
