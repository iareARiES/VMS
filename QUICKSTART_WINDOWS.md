# Quick Start - Windows (Laptop Testing)

## Prerequisites

Make sure you have:
- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed
- ✅ Virtual environments created (`.venv` folders in `backend/` and `detection-service/`)
- ✅ Dependencies installed (`pip install -e .` in each service)

## Step 1: Add Model Files

Copy your ONNX model files to `intrusion-suite\models\`:
- `best.onnx`
- `w600k_mbf.onnx`
- `yolo11npRETRAINED.onnx`
- `Fire_Event_best.onnx`

## Step 2: Start Services

### Easy Way (Opens 3 Windows Automatically):
```powershell
.\scripts\start_windows.ps1
```

### Manual Way (3 Separate Terminals):

**Terminal 1 - Detection Service:**
```powershell
cd detection-service
.\.venv\Scripts\Activate.ps1
uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010
```

**Terminal 2 - Backend:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend:**
```powershell
cd frontend
npm run dev
```

## Step 3: Access Dashboard

Open your browser to: **http://localhost:3000**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Detection Service: http://localhost:8010

## Troubleshooting

**Python not found?**
- Install Python 3.9+ from python.org
- Make sure to check "Add Python to PATH" during installation

**Port already in use?**
- Stop other services using ports 3000, 8000, or 8010
- Or change ports in `.env`

**Module not found?**
- Make sure virtual environments are activated
- Reinstall: `pip install -e .` in each service directory

## Troubleshooting

**Services won't start?**
- Make sure virtual environments are activated
- Check that ports 3000, 8000, 8010 are not in use
- Verify Python and Node.js are installed correctly

**Models not detected?**
- Ensure model files are in `intrusion-suite\models\` folder
- Check model file names match: `best.onnx`, `yolo11npRETRAINED.onnx`, etc.

