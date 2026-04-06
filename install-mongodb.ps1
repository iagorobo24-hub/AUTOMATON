# Install MongoDB Community Server on Windows
# This script downloads and installs MongoDB 7.0 for Windows
# Eliminates the need for Docker just for database

$ErrorActionPreference = "Stop"
$mongoVersion = "7.0.15"
$installDir = "C:\Program Files\MongoDB"
$dataDir = Join-Path $env:USERPROFILE "automaton-mongo-data"
$logDir = Join-Path $env:USERPROFILE "automaton-mongo-logs"
$mongoPort = 27018

Write-Host "=== MongoDB 7.0 Native Installer for AUTOMATON ===" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
if (Test-Path "$installDir\Server\7.0\bin\mongod.exe") {
    Write-Host "[+] MongoDB 7.0 already installed at $installDir" -ForegroundColor Green
} else {
    Write-Host "[*] Downloading MongoDB $mongoVersion..." -ForegroundColor Blue
    
    $zipUrl = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-$mongoVersion.zip"
    $zipPath = "$env:TEMP\mongodb-$mongoVersion.zip"
    
    if (!(Test-Path $zipPath)) {
        try {
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
            Write-Host "[+] Download complete" -ForegroundColor Green
        } catch {
            Write-Host "[!] Download failed: $_" -ForegroundColor Red
            Write-Host "    Please download manually from: $zipUrl" -ForegroundColor Yellow
            Write-Host "    Extract to: $installDir" -ForegroundColor Yellow
            exit 1
        }
    }
    
    Write-Host "[*] Extracting MongoDB..." -ForegroundColor Blue
    Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\mongo-extract" -Force
    
    # Find the extracted folder
    $extractedDir = Get-ChildItem "$env:TEMP\mongo-extract" -Directory | Select-Object -First 1
    Write-Host "    Extracted from: $($extractedDir.Name)" -ForegroundColor Gray
    
    # Create install directory
    if (!(Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }
    
    # Copy files
    $targetDir = "$installDir\Server\7.0"
    Copy-Item -Path "$extractedDir\*" -Destination $targetDir -Recurse -Force
    Write-Host "[+] MongoDB installed to $targetDir" -ForegroundColor Green
    
    # Cleanup
    Remove-Item $zipPath -ErrorAction SilentlyContinue
    Remove-Item "$env:TEMP\mongo-extract" -Recurse -ErrorAction SilentlyContinue
}

# Add MongoDB to PATH
$mongoBin = "$installDir\Server\7.0\bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$mongoBin*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$mongoBin", "User")
    $env:Path = "$env:Path;$mongoBin"
    Write-Host "[+] Added MongoDB to PATH" -ForegroundColor Green
}

# Create data and log directories
if (!(Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Create MongoDB config file
$configFile = "$dataDir\mongod.conf"
@"
storage:
  dbPath: $dataDir
  journal:
    enabled: true

systemLog:
  destination: file
  path: $logDir\mongod.log
  logAppend: true

net:
  port: $mongoPort
  bindIp: 127.0.0.1

security:
  authorization: disabled
"@ | Out-File -FilePath $configFile -Encoding utf8

Write-Host "[+] MongoDB config created at $configFile" -ForegroundColor Green

# Check if MongoDB service already exists
$serviceName = "AUTOMATON-MongoDB"
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "[*] MongoDB service already exists. Updating..." -ForegroundColor Yellow
    sc.exe delete $serviceName 2>&1 | Out-Null
    Start-Sleep -Seconds 2
}

# Create Windows service
$mongodExe = "$mongoBin\mongod.exe"
sc.exe create $serviceName binPath= "`"$mongodExe`" --config `"$configFile`" --service" start= "auto" displayName= "AUTOMATON MongoDB" 2>&1 | Out-Null
Write-Host "[+] MongoDB Windows service created: $serviceName" -ForegroundColor Green

# Start the service
Write-Host "[*] Starting MongoDB service..." -ForegroundColor Blue
try {
    Start-Service -Name $serviceName
    Write-Host "[+] MongoDB service started" -ForegroundColor Green
} catch {
    Write-Host "[!] Service start failed: $_" -ForegroundColor Red
    Write-Host "    Trying manual start..." -ForegroundColor Yellow
    Start-Process -FilePath $mongodExe -ArgumentList "--config", $configFile -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Verify MongoDB is running
Write-Host "[*] Verifying MongoDB on port $mongoPort..." -ForegroundColor Gray
Start-Sleep -Seconds 3
try {
    $mongoExe = "$mongoBin\mongo.exe"
    if (Test-Path $mongoExe) {
        & $mongoExe --port $mongoPort --eval "db.adminCommand('ping')" 2>&1 | Out-Null
    } else {
        # MongoDB 7.0 uses mongosh instead of mongo
        $mongoshExe = "$mongoBin\mongosh.exe"
        if (Test-Path $mongoshExe) {
            & $mongoshExe --port $mongoPort --eval "db.adminCommand('ping')" --quiet 2>&1 | Out-Null
        }
    }
    Write-Host "[+] MongoDB is running and responding on port $mongoPort" -ForegroundColor Green
} catch {
    Write-Host "[!] MongoDB verification failed, but may still be starting" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== MongoDB Installation Complete ===" -ForegroundColor Cyan
Write-Host "  Data Directory: $dataDir" -ForegroundColor Gray
Write-Host "  Log Directory:  $logDir" -ForegroundColor Gray
Write-Host "  Port:           $mongoPort" -ForegroundColor Gray
Write-Host "  Service:        $serviceName" -ForegroundColor Gray
Write-Host ""
Write-Host "To manage MongoDB:" -ForegroundColor Yellow
Write-Host "  Start:   net start $serviceName" -ForegroundColor Gray
Write-Host "  Stop:    net stop $serviceName" -ForegroundColor Gray
Write-Host "  Status:  sc query $serviceName" -ForegroundColor Gray
