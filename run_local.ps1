$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'Creating the project virtual environment...'
    py -3 -m venv .venv
}

Write-Host 'Installing/updating AlgoForge dependencies...'
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements-dev.txt

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example. Review it before using external services.'
}

Write-Host 'Applying database migrations...'
& $python -m alembic upgrade head

Write-Host ''
Write-Host 'Starting AlgoForge at http://127.0.0.1:8000'
Write-Host 'Keep this terminal open while using the app. Press Ctrl+C to stop.'
& $python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
