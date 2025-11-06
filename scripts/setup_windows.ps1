# PowerShell setup script for Windows (laptop testing)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Intrusion Detection System Setup (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Step 1/5: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.9+ from python.org" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Setup backend
Write-Host "Step 2/5: Setting up backend Python environment..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install backend packages" -ForegroundColor Red
    exit 1
}
deactivate
Set-Location ..
Write-Host "✓ Backend setup complete" -ForegroundColor Green
Write-Host ""

# Step 3: Setup detection-service
Write-Host "Step 3/5: Setting up detection-service Python environment..." -ForegroundColor Yellow
Set-Location detection-service

if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install detection-service packages" -ForegroundColor Red
    exit 1
}
deactivate
Set-Location ..
Write-Host "✓ Detection-service setup complete" -ForegroundColor Green
Write-Host ""

# Step 4: Setup frontend
Write-Host "Step 4/5: Setting up frontend (Node.js dependencies)..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages (this may take a few minutes)..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install npm packages" -ForegroundColor Red
        Write-Host "Try: npm install --legacy-peer-deps" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "node_modules already exists, skipping npm install" -ForegroundColor Green
}
Set-Location ..
Write-Host "✓ Frontend setup complete" -ForegroundColor Green
Write-Host ""

# Step 5: Create storage directories
Write-Host "Step 5/5: Creating storage directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "storage\videos" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\snaps" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\clips" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\db" | Out-Null
New-Item -ItemType Directory -Force -Path "models" | Out-Null
Write-Host "✓ Storage directories created" -ForegroundColor Green
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy your ONNX model files to: intrusion-suite\models\" -ForegroundColor White
Write-Host "2. Start services (see README_WINDOWS.md or run scripts/start_windows.ps1)" -ForegroundColor White
Write-Host ""

