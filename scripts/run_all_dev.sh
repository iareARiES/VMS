#!/bin/bash
# Run all services in development mode

# Create tmux session or run in separate terminals
echo "Starting services..."
echo "Backend: http://localhost:8000"
echo "Detection Service: http://localhost:8010"
echo "Frontend: http://localhost:3000"

# Terminal 1: Detection Service
cd detection-service
source .venv/bin/activate
uvicorn detectsvc.main:app --host 0.0.0.0 --port 8010 &
DETECT_PID=$!

# Terminal 2: Backend
cd ../backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Terminal 3: Frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Services started. PIDs:"
echo "  Detection: $DETECT_PID"
echo "  Backend: $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"

# Wait for interrupt
trap "kill $DETECT_PID $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait

