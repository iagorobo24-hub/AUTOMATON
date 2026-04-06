@echo off
TITLE AUTOMATON Test - Full Startup
echo.
echo ============================================
echo   AUTOMATON // TEST LAUNCHER
echo ============================================
echo.
echo Starting AUTOMATON...
echo.
powershell.exe -ExecutionPolicy Bypass -NoLogo -NoProfile -Command "& { Set-Location '%~dp0'; . .\launcher.ps1 }"
echo.
echo Launcher exited.
pause
