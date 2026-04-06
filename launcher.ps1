# Automaton QwenCLI Launcher v2
# Improved reliability with better process management and error handling
# Ports: Backend=8002, Frontend=3001, MongoDB=27017, MongoExpress=8082

$ErrorActionPreference = "Continue"

$BACKEND_PORT = 8002
$FRONTEND_PORT = 3001
$MONGO_PORT = 27017
$MONGOEXPRESS_PORT = 8082

Write-Host "=== AUTOMATON QwenCLI ECOSYSTEM STARTUP ===" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$desktopDir = Join-Path $rootDir "desktop"

$BGProcs = @()

function Cleanup {
    Write-Host ""
    Write-Host "[*] Shutting down AUTOMATON QwenCLI services..." -ForegroundColor Yellow
    foreach ($proc in $BGProcs) {
        try {
            if ($proc -and !$proc.HasExited) {
                $proc | Stop-Process -Force -ErrorAction SilentlyContinue
                Write-Host "    Stopped process $($proc.Id)" -ForegroundColor Gray
            }
        } catch {}
    }
    # Also kill any orphaned processes on our ports
    foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
        try {
            $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
            foreach ($conn in $conns) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        } catch {}
    }
    try { Stop-Process -Name "electron" -Force -ErrorAction SilentlyContinue } catch {}
    Write-Host "[+] All services stopped." -ForegroundColor Green
}

Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup } | Out-Null

function Wait-ForPort {
    param([int]$Port, [int]$TimeoutSeconds, [string]$Name)
    $start = Get-Date
    $lastMsg = 0
    while ($true) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("127.0.0.1", $Port)
            $tcp.Close()
            Write-Host "[+] $Name ready on port $Port" -ForegroundColor Green
            return $true
        } catch {}
        $elapsed = [int]((Get-Date) - $start).TotalSeconds
        if ($elapsed -ge $TimeoutSeconds) {
            Write-Host "[!] $Name failed to start within ${TimeoutSeconds}s" -ForegroundColor Red
            return $false
        }
        Start-Sleep -Seconds 2
        if (($elapsed - $lastMsg) -ge 10) {
            Write-Host "    ...waiting ${elapsed}s/${TimeoutSeconds}s" -ForegroundColor Gray
            $lastMsg = $elapsed
        }
    }
}

# STEP 0: Kill existing services
Write-Host "[0/6] Cleaning up existing services..." -ForegroundColor Gray
foreach ($port in @($BACKEND_PORT, $FRONTEND_PORT)) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        foreach ($conn in $conns) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
try { 
    Get-Process | Where-Object { $_.Name -eq "electron" } | Stop-Process -Force -ErrorAction SilentlyContinue 
} catch {}
Start-Sleep -Seconds 2
Write-Host "[+] Cleanup complete" -ForegroundColor Green

# STEP 1: Check Docker
Write-Host "[1/6] Checking Docker..." -ForegroundColor Blue
try {
    $dockerStatus = docker ps --format "{{.Names}}" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
    Write-Host "[+] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[!] Docker Desktop is not running. Please start it first." -ForegroundColor Red
    Read-Host "Press ENTER to continue or Ctrl+C to cancel"
}

# STEP 2: Start MongoDB
Write-Host "[2/6] Starting MongoDB..." -ForegroundColor Blue
docker-compose -f (Join-Path $rootDir ".devops\docker-compose.yml") up -d 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "[+] MongoDB started" -ForegroundColor Green

# STEP 3: Seed DB
Write-Host "[3/6] Seeding database..." -ForegroundColor Blue
Push-Location $backendDir
if (!(Test-Path "venv\Scripts\python.exe")) {
    Write-Host "    Creating Python venv..." -ForegroundColor Gray
    python -m venv venv
}
if (!(Test-Path "venv\Scripts\uvicorn.exe")) {
    Write-Host "    Installing backend deps..." -ForegroundColor Gray
    .\venv\Scripts\pip.exe install -r requirements.txt 2>&1 | Out-Null
}
.\venv\Scripts\python.exe app/core/seed.py 2>&1 | Out-Null
Pop-Location
Write-Host "[+] Database seeded" -ForegroundColor Green

# STEP 4: Start Backend
Write-Host "[4/6] Starting Backend API (port $BACKEND_PORT)..." -ForegroundColor Blue
$uvicorn = Join-Path $backendDir "venv\Scripts\python.exe"
$uvArgs = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $BACKEND_PORT.ToString(), "--reload")
$uvProc = Start-Process -FilePath $uvicorn -ArgumentList $uvArgs -WorkingDirectory $backendDir -WindowStyle Hidden -PassThru
$BGProcs += $uvProc
Write-Host "    Backend PID: $($uvProc.Id)" -ForegroundColor Gray

if (!(Wait-ForPort -Port $BACKEND_PORT -TimeoutSeconds 30 -Name "Backend API")) {
    Write-Host "[!] Backend failed. Exiting." -ForegroundColor Red
    Cleanup
    exit 1
}

# STEP 5: Start Frontend
Write-Host "[5/6] Starting Frontend UI (port $FRONTEND_PORT)..." -ForegroundColor Blue
Push-Location $frontendDir
if (!(Test-Path "node_modules")) {
    Write-Host "    Installing frontend deps (this may take a while)..." -ForegroundColor Gray
    npm install --legacy-peer-deps 2>&1 | Out-Null
}
Pop-Location

# Use npm run start which respects the craco.config.js
$env:BROWSER = "none"
$env:PORT = $FRONTEND_PORT.ToString()
$feProc = Start-Process -FilePath "npm" -ArgumentList "run", "start" -WorkingDirectory $frontendDir -WindowStyle Hidden -PassThru
$BGProcs += $feProc
Remove-Item env:BROWSER -ErrorAction SilentlyContinue
Remove-Item env:PORT -ErrorAction SilentlyContinue
Write-Host "    Frontend PID: $($feProc.Id)" -ForegroundColor Gray

# Wait for frontend - CRACO takes longer to compile
Write-Host "    Waiting for frontend to compile..." -ForegroundColor Gray
$feReady = Wait-ForPort -Port $FRONTEND_PORT -TimeoutSeconds 180 -Name "Frontend UI"
if (!$feReady) {
    Write-Host "[!] Frontend timed out after 180s" -ForegroundColor Red
    Cleanup
    exit 1
}
# Additional wait for webpack to finish initial compilation
Write-Host "    Waiting for webpack compilation..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# STEP 6: Launch Electron
Write-Host "[6/6] Launching AUTOMATON Desktop..." -ForegroundColor Cyan
$electronExe = Join-Path $desktopDir "node_modules\electron\dist\electron.exe"
if (!(Test-Path $electronExe)) {
    Write-Host "    Electron not found. Installing..." -ForegroundColor Yellow
    Push-Location $desktopDir
    npm install 2>&1 | Out-Null
    Pop-Location
    if (!(Test-Path $electronExe)) {
        Write-Host "[!!] Electron installation failed" -ForegroundColor Red
        Cleanup
        exit 1
    }
}

Push-Location $desktopDir
$elProc = Start-Process -FilePath $electronExe -ArgumentList "." -PassThru
Pop-Location
$BGProcs += $elProc
Write-Host "[+] Electron launched (PID: $($elProc.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "=== SYSTEM INITIALIZED ===" -ForegroundColor Cyan
Write-Host "  App is running. Close the Electron window to stop all services." -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:$FRONTEND_PORT" -ForegroundColor Cyan
Write-Host "  Backend:   http://localhost:$BACKEND_PORT" -ForegroundColor Green
Write-Host "  Mongo:     localhost:$MONGO_PORT" -ForegroundColor Blue
Write-Host "  Mongo UI:  http://localhost:$MONGOEXPRESS_PORT" -ForegroundColor Blue
Write-Host ""

# Wait for Electron to exit
try {
    while (!$elProc.HasExited) {
        Start-Sleep -Seconds 1
        $elProc.Refresh()
    }
} catch {}

Cleanup
Write-Host "[+] AUTOMATON shutdown complete" -ForegroundColor Green
