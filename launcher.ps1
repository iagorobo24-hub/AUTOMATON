$ErrorActionPreference = "Stop"
$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Push-Location $rootDir
try {
    Write-Host "Starting AUTOMATON SQLModel runtime..." -ForegroundColor Cyan
    Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Gray
    Write-Host "Frontend: http://localhost:5173" -ForegroundColor Gray
    npm.cmd run dev
    exit $LASTEXITCODE
} catch {
    Write-Host "AUTOMATON startup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
