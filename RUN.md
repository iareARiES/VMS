# 🚀 How to Run the System

## Quick Start (Easiest Method)

Open PowerShell in the `intrusion-suite` folder and run:

```powershell
.\scripts\start_windows.ps1
```

This will automatically open **3 separate terminal windows**:
1. **Detection Service** (port 8010)
2. **Backend API** (port 8000)
3. **Frontend** (port 3000)

Then open your browser to: **http://localhost:3000**

---

## Manual Method (3 Separate Terminals)

If you prefer to run each service manually:

### Terminal 1 - Detection Service:
```powershell
cd E:\RapberryPi\intrusion-suite\detection-service
.\.venv\Scripts\Activate.ps1
uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010
```

### Terminal 2 - Backend API:
```powershell
cd E:\RapberryPi\intrusion-suite\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Terminal 3 - Frontend:
```powershell
cd E:\RapberryPi\intrusion-suite\frontend
npm run dev
```

---

## Access Points

Once all services are running:

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Detection Service**: http://localhost:8010

---

## What to Expect

1. **Detection Service** will show:
   ```
   Detection Service starting on port 8010...
   Models registered. They will be loaded when detection starts.
   ```

2. **Backend** will show:
   ```
   Backend API starting on port 8000...
   Database initialized at: sqlite:///...
   ```

3. **Frontend** will show:
   ```
   Frontend starting on port 3000...
   VITE ready in XXX ms
   ```

---

## Stopping Services

Press `Ctrl+C` in each terminal window to stop the services.

---

## Troubleshooting

**Port already in use?**
- Stop other applications using ports 3000, 8000, or 8010
- Or kill the process: `netstat -ano | findstr :8010` then `taskkill /PID <PID> /F`

**Virtual environment not found?**
- Make sure `.venv` folders exist in `backend/` and `detection-service/`
- If missing, create them: `python -m venv .venv`

**Module not found errors?**
- Activate virtual environment: `.\.venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -e .`

**Models not detected?**
- Check that model files are in `intrusion-suite\models\` folder
- Verify file names: `best.onnx`, `yolo11npRETRAINED.onnx`, etc.

