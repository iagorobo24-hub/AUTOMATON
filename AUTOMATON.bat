@echo off
TITLE AUTOMATON OpenCode Launcher
echo.
echo ============================================
echo   AUTOMATON // OpenCode Launcher
echo ============================================
echo.
echo Starting AUTOMATON...
echo.
echo Checking prerequisites...
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running! Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Set execution policy for this session and run PowerShell
echo Launching PowerShell script...
powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "& {Set-Location '%~dp0'; & '%~dp0launcher.ps1'}"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to launch AUTOMATON. Check the logs above.
    pause
)

echo.
echo AUTOMATON session ended.
pause