# Automaton Local Orchestrator Launcher
Write-Host "--- AUTOMATON ECOSYSTEM STARTUP ---" -ForegroundColor Cyan

# 1. Check for Docker
if (!(Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Docker Desktop is not running. Please start it first." -ForegroundColor Yellow
}

# 2. Start Infrastructure
Write-Host "[*] Starting MongoDB Infrastructure..." -ForegroundColor Blue
docker-compose -f .devops/docker-compose.yml up -d

# 3. Seed Database
Write-Host "[*] Seeding Genesis Fleet..." -ForegroundColor Blue
cd backend
if (!(Test-Path venv)) {
    Write-Host "[*] Creating Python Virtual Environment..." -ForegroundColor Gray
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
}
.\venv\Scripts\python app/core/seed.py
cd ..

# 4. Start Backend
Write-Host "[*] Starting Backend API (Port 8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"

# 5. Start Frontend
Write-Host "[*] Starting Frontend UI (Port 3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-WindowStyle Hidden", "-Command", "cd frontend; npm start"

# 6. Launch Desktop Window (Electron)
Write-Host "[*] Launching AUTOMATON Desktop Native..." -ForegroundColor Cyan
cd desktop
if (!(Test-Path node_modules)) {
    Write-Host "[*] Installing Desktop Dependencies..." -ForegroundColor Gray
    npm install
}
npm start
cd ..

Write-Host "--- SYSTEM INITIALIZED ---" -ForegroundColor Cyan
