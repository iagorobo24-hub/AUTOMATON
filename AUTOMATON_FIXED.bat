@echo off
title AUTOMATON OpenCode Launcher - FIXED VERSION
chcp 65001 >nul 2>&1
cls
echo.
echo ============================================
echo   AUTOMATON // OpenCode Launcher
echo   Version CORREGIDA
echo ============================================
echo.
echo Verificando requisitos...
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo! Por favor inicia Docker Desktop primero.
    pause
    exit /b 1
)

echo [OK] Docker esta corriendo
echo.
echo Iniciando AUTOMATON con el launcher corregido...
echo.

REM Run PowerShell with execution policy bypass and the fixed script
powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "& '%~dp0launcher_fixed.ps1'"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] AUTOMATON fallo al iniciar.
    echo.
    echo Posibles causas:
    echo 1. No se instalo slowapi: Ejecuta: cd backend ^&^& venv\Scripts\python -m pip install slowapi
    echo 2. Error en codigo Python revisa: backend\app\routers\auth.py
    echo 3. Puerto 8000 o 3001 ocupados
    echo.
    pause
)

echo.
echo AUTOMATON finalizado.
pause
