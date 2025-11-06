#!/bin/bash
# Setup script for Raspberry Pi

# Exit on error, but show what failed
set -e

echo "=========================================="
echo "Intrusion Detection System Setup"
echo "=========================================="
echo ""

# Step 1: Install system dependencies
echo "Step 1/5: Installing system dependencies..."
echo "This will update package list and install:"
echo "  - Python 3, pip, venv"
echo "  - Node.js and npm"
echo "  - FFmpeg (for video processing)"
echo "  - OpenCV libraries"
echo ""

# Update package list
echo "Updating package list..."
sudo apt-get update || {
    echo "ERROR: Failed to update package list"
    exit 1
}

# Install system packages
echo "Installing system packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    ffmpeg \
    libopencv-dev \
    python3-opencv || {
    echo "ERROR: Failed to install system packages"
    exit 1
}

echo "✓ System dependencies installed"
echo ""

# Step 2: Setup backend
echo "Step 2/5: Setting up backend Python environment..."
cd "$(dirname "$0")/../backend" || {
    echo "ERROR: Cannot find backend directory"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv || {
        echo "ERROR: Failed to create virtual environment"
        exit 1
    }
else
    echo "Virtual environment already exists, skipping creation"
fi

# Activate and install
echo "Installing backend dependencies..."
source .venv/bin/activate
pip install --upgrade pip || {
    echo "ERROR: Failed to upgrade pip"
    exit 1
}

pip install -e . || {
    echo "ERROR: Failed to install backend packages"
    echo "Make sure you're in the intrusion-suite directory"
    exit 1
}

echo "✓ Backend setup complete"
echo ""

# Step 3: Setup detection-service
echo "Step 3/5: Setting up detection-service Python environment..."
cd "../detection-service" || {
    echo "ERROR: Cannot find detection-service directory"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv || {
        echo "ERROR: Failed to create virtual environment"
        exit 1
    }
else
    echo "Virtual environment already exists, skipping creation"
fi

# Activate and install
echo "Installing detection-service dependencies..."
source .venv/bin/activate
pip install --upgrade pip || {
    echo "ERROR: Failed to upgrade pip"
    exit 1
}

pip install -e . || {
    echo "ERROR: Failed to install detection-service packages"
    exit 1
}

echo "✓ Detection-service setup complete"
echo ""

# Step 4: Setup frontend
echo "Step 4/5: Setting up frontend (Node.js dependencies)..."
cd "../frontend" || {
    echo "ERROR: Cannot find frontend directory"
    exit 1
}

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages (this may take a few minutes)..."
    npm install || {
        echo "ERROR: Failed to install npm packages"
        echo "Try: npm install --legacy-peer-deps"
        exit 1
    }
else
    echo "node_modules already exists, skipping npm install"
    echo "To reinstall, delete node_modules and run this script again"
fi

echo "✓ Frontend setup complete"
echo ""

# Step 5: Initialize storage and database
echo "Step 5/5: Initializing storage directories and database..."
cd ".." || exit 1

# Create storage directories
mkdir -p storage/videos
mkdir -p storage/snaps
mkdir -p storage/clips
mkdir -p storage/db
mkdir -p models

echo "✓ Storage directories created"

# Initialize database (if backend is set up)
if [ -d "backend/.venv" ]; then
    echo "Initializing database schema..."
    cd backend
    source .venv/bin/activate
    python3 -c "from app.deps import init_db; init_db()" 2>/dev/null || {
        echo "  Note: Database will be created automatically when backend starts"
    }
    cd ..
    echo "✓ Database initialization attempted"
else
    echo "  Note: Database will be initialized when backend starts"
fi

echo ""

# Summary
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy your ONNX model files to: intrusion-suite/models/"
echo "   - best.onnx (face detection)"
echo "   - w600k_mbf.onnx (face recognition)"
echo "   - yolo11npRETRAINED.onnx (COCO detection)"
echo "   - Fire_Event_best.onnx (fire/smoke)"
echo ""
echo "2. Configure environment (optional):"
echo "   cp .env.example .env"
echo "   # Edit .env with your settings"
echo ""
echo "3. Start services in development mode:"
echo "   bash scripts/run_all_dev.sh"
echo ""
echo "Or start manually in separate terminals:"
echo "   Terminal 1: cd detection-service && source .venv/bin/activate && uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010"
echo "   Terminal 2: cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "   Terminal 3: cd frontend && npm run dev"
echo ""

