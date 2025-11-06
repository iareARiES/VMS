# Raspberry Pi Setup Guide

Complete setup instructions for running the Intrusion Detection System on Raspberry Pi with Linux Bookworm OS.

## Prerequisites

- Raspberry Pi 4 or newer (recommended: 4GB+ RAM)
- Raspberry Pi OS (Bookworm) or Debian Bookworm
- MicroSD card (32GB+ recommended)
- Camera module or USB webcam (optional, for live detection)
- Internet connection for initial setup

## System Requirements

- Python 3.9 or higher
- Node.js 18+ and npm
- At least 2GB free disk space
- Stable internet connection

## Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

## Step 2: Install System Dependencies

```bash
# Install Python and build tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Node.js 18+ (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install system libraries required for OpenCV and ONNX
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libgfortran5 \
    libgomp1 \
    libblas-dev \
    liblapack-dev \
    build-essential \
    cmake \
    pkg-config

# Install SQLite (if not already installed)
sudo apt install -y sqlite3

# Install Git (if not already installed)
sudo apt install -y git
```

## Step 3: Clone Repository

```bash
# Navigate to your desired installation directory
cd ~

# Clone the repository (or copy your project files)
git clone <your-repo-url> intrusion-suite
cd intrusion-suite
```

## Step 4: Install Python Dependencies

```bash
# Install all Python requirements
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

**Note:** If you encounter issues with `onnxruntime` on Raspberry Pi, you may need to use the CPU-only version:
```bash
pip3 install onnxruntime==1.16.0
```

## Step 5: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Step 6: Initialize Storage and Database

```bash
# Create storage directories and initialize database
python3 scripts/init_storage_db.py
```

This will create:
- `storage/videos/` - Video recordings
- `storage/snaps/` - Snapshot images
- `storage/clips/` - Event clips
- `storage/db/` - SQLite database
- `models/` - YOLO model files

## Step 7: Add YOLO Models

Place your ONNX model files in the `models/` directory:
- `best.onnx` - Face detection
- `w600k_mbf.onnx` - Face recognition
- `yolo11npRETRAINED.onnx` - General object detection
- `Fire_Event_best.onnx` - Fire/smoke detection

**Note:** Model files are large and should be obtained separately. They are not included in the repository.

## Step 8: Configure Environment (Optional)

Create a `.env` file in the project root if you need custom settings:

```bash
# Backend configuration
DB_URL=sqlite:///storage/db/events.sqlite
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DETECTION_SERVICE_URL=http://localhost:8010

# Detection service configuration
DETECT_HOST=0.0.0.0
DETECT_PORT=8010
INFER_DEVICE=onnx_cpu
TARGET_FPS=12
MODELS_ROOT=models
STORAGE_ROOT=storage
```

## Step 9: Test Installation

### Test Detection Service
```bash
cd detection-service
python3 -m uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010
```

In another terminal, test the service:
```bash
curl http://localhost:8010/health
```

### Test Backend
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In another terminal, test the backend:
```bash
curl http://localhost:8000/health
```

### Test Frontend
```bash
cd frontend
npm run dev
```

Open your browser to `http://<raspberry-pi-ip>:3000`

## Step 10: Run in Production Mode

### Option 1: Using systemd (Recommended)

Create systemd service files:

**`/etc/systemd/system/intrusion-backend.service`**
```ini
[Unit]
Description=Intrusion Detection Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/intrusion-suite/backend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/intrusion-detection.service`**
```ini
[Unit]
Description=Intrusion Detection Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/intrusion-suite/detection-service
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/intrusion-frontend.service`**
```ini
[Unit]
Description=Intrusion Detection Frontend
After=network.target intrusion-backend.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/intrusion-suite/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run preview
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable intrusion-backend intrusion-detection intrusion-frontend
sudo systemctl start intrusion-backend intrusion-detection intrusion-frontend

# Check status
sudo systemctl status intrusion-backend
sudo systemctl status intrusion-detection
sudo systemctl status intrusion-frontend
```

### Option 2: Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Step 11: Access the Application

- **Frontend UI:** `http://<raspberry-pi-ip>:3000`
- **Backend API:** `http://<raspberry-pi-ip>:8000`
- **API Documentation:** `http://<raspberry-pi-ip>:8000/docs`
- **Detection Service:** `http://<raspberry-pi-ip>:8010`

## Troubleshooting

### Port Already in Use
If ports 8000, 8010, or 3000 are already in use:
```bash
# Find process using the port
sudo lsof -i :8000
sudo lsof -i :8010
sudo lsof -i :3000

# Kill the process or change ports in .env file
```

### Permission Issues
```bash
# Ensure storage directories are writable
chmod -R 755 storage/
chmod -R 755 models/
```

### ONNX Runtime Issues
If you encounter ONNX runtime errors:
```bash
# Reinstall onnxruntime with CPU support
pip3 uninstall onnxruntime
pip3 install onnxruntime==1.16.0
```

### Memory Issues
If the system runs out of memory:
- Reduce `TARGET_FPS` in detection service config
- Use smaller model files
- Close unnecessary applications
- Consider adding swap space

### Camera Not Detected
```bash
# List available cameras
ls -l /dev/video*

# Test camera with v4l2
v4l2-ctl --list-devices
```

## Performance Optimization

For better performance on Raspberry Pi:

1. **Reduce FPS:** Set `TARGET_FPS=8` or lower in `.env`
2. **Use smaller models:** Prefer smaller ONNX models
3. **Enable GPU acceleration:** If using Raspberry Pi 5, consider GPU acceleration
4. **Close unnecessary services:** Disable unused system services

See `PERFORMANCE_OPTIMIZATIONS.md` and `ULTRA_PERFORMANCE_MODE.md` for more details.

## Next Steps

- Configure detection zones in the UI
- Upload and enable YOLO models
- Set up camera sources
- Configure alert settings
- Review `DIRECTORY_STRUCTURE.md` to understand the codebase

## Support

For issues and troubleshooting, see `TROUBLESHOOTING.md`.

