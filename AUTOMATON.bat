@echo off
TITLE AUTOMATON OpenCode Launcher
echo.
echo ============================================
echo   AUTOMATON // OpenCode Launcher
echo ============================================
echo.
echo Starting AUTOMATON...
echo.

REM Set execution policy for this session
powershell -ExecutionPolicy Bypass -NoProfile -Command "Set-Location '%~dp0'; & { .\launcher.ps1 }"

pause