@echo off
REM Setup script for Windows (laptop testing)

echo ==========================================
echo Intrusion Detection System Setup (Windows)
echo ==========================================
echo.

REM Step 1: Check Python
echo Step 1/5: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)
python --version
echo.

REM Step 2: Setup backend
echo Step 2/5: Setting up backend Python environment...
cd backend
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install backend packages
    pause
    exit /b 1
)
deactivate
cd ..
echo ✓ Backend setup complete
echo.

REM Step 3: Setup detection-service
echo Step 3/5: Setting up detection-service Python environment...
cd detection-service
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install detection-service packages
    pause
    exit /b 1
)
deactivate
cd ..
echo ✓ Detection-service setup complete
echo.

REM Step 4: Setup frontend
echo Step 4/5: Setting up frontend (Node.js dependencies)...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install npm packages
        echo Try: npm install --legacy-peer-deps
        pause
        exit /b 1
    )
) else (
    echo node_modules already exists, skipping npm install
)
cd ..
echo ✓ Frontend setup complete
echo.

REM Step 5: Create storage directories
echo Step 5/5: Creating storage directories...
if not exist "storage\videos" mkdir storage\videos
if not exist "storage\snaps" mkdir storage\snaps
if not exist "storage\clips" mkdir storage\clips
if not exist "storage\db" mkdir storage\db
if not exist "models" mkdir models
echo ✓ Storage directories created
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Copy your ONNX model files to: intrusion-suite\models\
echo 2. Start services (see README_WINDOWS.md)
echo.
pause

