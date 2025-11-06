# Installation Guide for Raspberry Pi

## Prerequisites

- Raspberry Pi 4 or 5 (recommended) or Raspberry Pi 3B+
- Raspberry Pi OS (Debian-based) or Ubuntu
- Python 3.9 or higher
- At least 4GB RAM (8GB recommended)
- MicroSD card with at least 16GB free space

## Step 1: Install System Dependencies

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and build tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config

# Install OpenCV system libraries (important for Raspberry Pi)
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev

# Install Node.js and npm (for frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install FFmpeg (for video processing)
sudo apt-get install -y ffmpeg
```

## Step 2: Clone/Download Project

```bash
cd ~
# If using git:
# git clone <your-repo-url> intrusion-suite
# OR extract your project files to ~/intrusion-suite
cd intrusion-suite
```

## Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r ../requirements-backend.txt

# OR install from pyproject.toml
pip install -e .

# Deactivate
deactivate
```

## Step 4: Setup Detection Service

```bash
cd ../detection-service

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r ../requirements-detection.txt

# OR install from pyproject.toml
pip install -e .

# Deactivate
deactivate
```

## Step 5: Setup Frontend

```bash
cd ../frontend

# Install Node.js dependencies
npm install

# If you encounter peer dependency issues:
# npm install --legacy-peer-deps
```

## Step 6: Create Storage Directories

```bash
cd ..
mkdir -p storage/videos storage/snaps storage/clips storage/db
mkdir -p models
```

## Step 7: Add Your YOLO Models

Copy your `.onnx` model files to:
```bash
cp /path/to/your/models/*.onnx models/
```

## Step 8: Configure Environment (Optional)

```bash
# Create .env file if needed
cp .env.example .env
nano .env  # Edit with your settings
```

## Step 9: Test Installation

### Test Backend:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Should see: "Application startup complete"
# Press Ctrl+C to stop
deactivate
```

### Test Detection Service:
```bash
cd detection-service
source .venv/bin/activate
uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010
# Should see: "Application startup complete"
# Press Ctrl+C to stop
deactivate
```

### Test Frontend:
```bash
cd frontend
npm run dev
# Should start on http://localhost:5173
# Press Ctrl+C to stop
```

## Step 10: Run All Services

### Option 1: Using the provided script
```bash
bash scripts/run_all_dev.sh
```

### Option 2: Manual (3 separate terminals)

**Terminal 1 - Detection Service:**
```bash
cd ~/intrusion-suite/detection-service
source .venv/bin/activate
uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010
```

**Terminal 2 - Backend:**
```bash
cd ~/intrusion-suite/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd ~/intrusion-suite/frontend
npm run dev
```

## Troubleshooting

### Issue: ONNX Runtime installation fails
```bash
# Try installing specific version that works on ARM
pip install onnxruntime==1.16.3
```

### Issue: OpenCV import errors
```bash
# Make sure system OpenCV is installed
sudo apt-get install libopencv-dev python3-opencv

# OR use headless version
pip uninstall opencv-python
pip install opencv-python-headless
```

### Issue: NumPy installation slow/fails
```bash
# Install NumPy with pre-built wheels
pip install --upgrade pip
pip install numpy --only-binary :all:
```

### Issue: Out of memory during installation
```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue: Slow inference performance
- Use lighter models (smaller input size)
- Reduce target_fps in config.py
- Consider using frame_skip > 1
- Close unnecessary applications

## Performance Optimization for Raspberry Pi

1. **Use lighter models**: Prefer YOLOv8n (nano) over larger variants
2. **Reduce input size**: Use 416x416 instead of 640x640 if possible
3. **Enable GPU acceleration** (Pi 5 only):
   ```bash
   # Install GPU-accelerated ONNX Runtime (if available)
   pip install onnxruntime-gpu
   ```

## System Service Setup (Optional)

To run services automatically on boot, see:
- `deploy/systemd/intrusion-backend.service`
- `deploy/systemd/intrusion-detection.service`
- `deploy/systemd/intrusion-frontend.service`

## Notes

- First-time installation may take 30-60 minutes
- Model loading may be slow on first run
- Consider using a fast microSD card (Class 10 or better)
- For production, consider using an external SSD via USB 3.0

