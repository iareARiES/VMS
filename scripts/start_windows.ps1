# Start all services on Windows (for testing)

Write-Host "Starting Intrusion Detection System..." -ForegroundColor Cyan
Write-Host ""

# Check if services are already running
$detectProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*detectsvc.main*" }
$backendProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.main*" }

if ($detectProcess -or $backendProcess) {
    Write-Host "Warning: Services may already be running!" -ForegroundColor Yellow
    Write-Host "Press Ctrl+C in each terminal to stop services" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Opening 3 PowerShell windows for services..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1: Detection Service (port 8010)" -ForegroundColor Yellow
Write-Host "Terminal 2: Backend API (port 8000)" -ForegroundColor Yellow
Write-Host "Terminal 3: Frontend (port 3000)" -ForegroundColor Yellow
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Terminal 1: Detection Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\detection-service'; .\.venv\Scripts\Activate.ps1; Write-Host 'Detection Service starting on port 8010...' -ForegroundColor Green; uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010"

Start-Sleep -Seconds 2

# Terminal 2: Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; .\.venv\Scripts\Activate.ps1; Write-Host 'Backend API starting on port 8000...' -ForegroundColor Green; uvicorn app.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# Terminal 3: Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; Write-Host 'Frontend starting on port 3000...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "Services are starting in separate windows." -ForegroundColor Green
Write-Host ""
Write-Host "Access the dashboard at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Detection Service at: http://localhost:8010" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this script (services will continue running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

