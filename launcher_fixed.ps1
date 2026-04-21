# AUTOMATON Launcher - Fixed Version
$ErrorActionPreference = "Stop"

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "   AUTOMATON // OpenCode Launcher" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$ElectronDir = Join-Path $RootDir "electron"

# Puerto configuration
$BackendPort = 8000
$FrontendPort = 3001
$MongoPort = 27017

# Colores
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Blue"

function Test-Port {
    param($Port)
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $false  # Puerto libre
    } catch {
        return $true   # Puerto ocupado
    }
}

function Wait-ForService {
    param($Url, $Name, $TimeoutSeconds = 60)
    Write-Host "Esperando $Name en $Url..." -ForegroundColor $Yellow
    $timer = [Diagnostics.Stopwatch]::StartNew()
    while ($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ $Name listo!" -ForegroundColor $Green
                return $true
            }
        } catch {}
        Start-Sleep -Milliseconds 500
    }
    Write-Host "✗ Timeout esperando $Name" -ForegroundColor $Red
    return $false
}

# 1. Verificar Docker y MongoDB
Write-Host "[1/5] Verificando MongoDB..." -ForegroundColor $Blue
try {
    $dockerCheck = docker ps --format "{{.Names}}" | Select-String "mongodb"
    if (-not $dockerCheck) {
        Write-Host "Iniciando MongoDB..." -ForegroundColor $Yellow
        docker-compose -f ".devops/docker-compose.yml" up -d mongodb
        Start-Sleep -Seconds 5
    }
    
    if (Test-Port $MongoPort) {
        Write-Host "✓ MongoDB corriendo" -ForegroundColor $Green
    } else {
        Write-Host "✗ MongoDB no disponible en puerto $MongoPort" -ForegroundColor $Red
        exit 1
    }
} catch {
    Write-Host "✗ Error con MongoDB: $_" -ForegroundColor $Red
    exit 1
}

# 2. Verificar Backend Python y dependencias
Write-Host "[2/5] Verificando Backend..." -ForegroundColor $Blue
try {
    Set-Location $BackendDir
    
    # Verificar que existe venv
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "Creando entorno virtual..." -ForegroundColor $Yellow
        python -m venv venv
    }
    
    # Verificar slowapi instalado
    $venvPython = Join-Path $BackendDir "venv\Scripts\python.exe"
    $hasSlowapi = & $venvPython -c "import slowapi; print('OK')" 2>&1
    if ($hasSlowapi -ne "OK") {
        Write-Host "Instalando slowapi..." -ForegroundColor $Yellow
        & $venvPython -m pip install slowapi -q
    }
    
    # Limpiar procesos anteriores
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*main:app*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 2
    
} catch {
    Write-Host "✗ Error preparando backend: $_" -ForegroundColor $Red
}

# 3. Iniciar Backend
Write-Host "[3/5] Iniciando Backend API..." -ForegroundColor $Blue
try {
    $env:PYTHONPATH = $BackendDir
    $backendJob = Start-Job -ScriptBlock {
        param($dir, $port)
        Set-Location $dir
        & "$dir\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port $port --reload
    } -ArgumentList $BackendDir, $BackendPort
    
    if (-not (Wait-ForService "http://localhost:$BackendPort/health" "Backend" 30)) {
        Write-Host "✗ Backend no inició correctamente" -ForegroundColor $Red
        Write-Host "Mostrando errores del backend:" -ForegroundColor $Yellow
        Receive-Job $backendJob
        exit 1
    }
} catch {
    Write-Host "✗ Error iniciando backend: $_" -ForegroundColor $Red
    exit 1
}

# 4. Iniciar Frontend
Write-Host "[4/5] Iniciando Frontend..." -ForegroundColor $Blue
try {
    Set-Location $FrontendDir
    
    # Instalar dependencias si no existen
    if (-not (Test-Path "node_modules")) {
        Write-Host "Instalando dependencias npm..." -ForegroundColor $Yellow
        npm install 2>&1 | Out-Null
    }
    
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        npm start
    } -ArgumentList $FrontendDir
    
    if (-not (Wait-ForService "http://localhost:$FrontendPort" "Frontend" 60)) {
        Write-Host "⚠ Frontend tardó en iniciar, continuando..." -ForegroundColor $Yellow
    }
} catch {
    Write-Host "✗ Error iniciando frontend: $_" -ForegroundColor $Red
}

# 5. Iniciar Electron
Write-Host "[5/5] Iniciando Electron..." -ForegroundColor $Blue
try {
    Set-Location $ElectronDir
    
    if (-not (Test-Path "node_modules")) {
        Write-Host "Instalando dependencias Electron..." -ForegroundColor $Yellow
        npm install 2>&1 | Out-Null
    }
    
    Write-Host "Lanzando aplicación de escritorio..." -ForegroundColor $Green
    npm start
} catch {
    Write-Host "✗ Error iniciando Electron: $_" -ForegroundColor $Red
}

# Cleanup
Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Limpiando procesos..." -ForegroundColor Yellow
Get-Job | Remove-Job -Force
Write-Host "✓ AUTOMATON finalizado" -ForegroundColor Green
