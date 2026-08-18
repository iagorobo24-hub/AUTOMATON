@echo off
TITLE AUTOMATON Launcher
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo   AUTOMATON // SQLModel Runtime
echo ============================================
echo.

powershell.exe -NoProfile -File "%~dp0launcher.ps1"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: AUTOMATON no se pudo iniciar.
    pause
    exit /b %errorlevel%
)
