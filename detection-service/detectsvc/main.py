"""Detection service main FastAPI app."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import time
import json
import uuid
from pathlib import Path

from detectsvc.config import settings
from detectsvc.registry import registry
from detectsvc.pipeline.capture import VideoCapture
from detectsvc.pipeline.infer_onnx import InferencePipeline
from detectsvc.pipeline.tracker import SimpleTracker
from detectsvc.pipeline.zones import ZoneChecker


app = FastAPI(
    title="Detection Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
inference_pipeline = InferencePipeline()
tracker = SimpleTracker()
zone_checker = None
capture = None
is_running = False
frame_count = 0
start_time = None

# WebSocket connections
ws_connections: List[WebSocket] = []
alert_connections: List[WebSocket] = []


# Auto-register models on startup
@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    registry.auto_register_models()
    
    # Initialize all classes as enabled by default for each model
    for model in registry.list_models():
        # Ensure all labels have enabled_classes entries
        labels = model.get("labels", [])
        enabled_classes = model.get("enabled_classes", {})
        for label in labels:
            if label not in enabled_classes:
                enabled_classes[label] = True
        registry.update_model(model["name"], enabled_classes=enabled_classes)
    
    # Don't load models on startup - they'll be loaded when detection starts
    # This prevents loading all models when only some are enabled
    print("Models registered. They will be loaded when detection starts.")


class StartRequest(BaseModel):
    """Start detection request."""
    source: Dict[str, str]
    models: List[Dict]
    zones: List[Dict] = []
    zones_version: str = "1"


class ZoneConfig(BaseModel):
    """Zone configuration."""
    zone_id: str
    name: str
    type: str
    points: List[List[float]]
    allowed_classes: List[str] = []
    min_size_px: int = 0
    dwell_sec: float = 0.0


@app.post("/detector/start")
async def start_detection(request: StartRequest):
    """Start detection stream."""
    global capture, is_running, zone_checker, frame_count, start_time
    
    try:
        if is_running:
            raise HTTPException(status_code=400, detail="Detection already running")
        
        # Update model configs
        for model_config in request.models:
            registry.update_model(
                model_config["name"],
                enabled=model_config.get("enabled", False),
                conf=model_config.get("conf", 0.35),
                iou=model_config.get("iou", 0.45),
                enabled_classes=model_config.get("enabled_classes", {})
            )
        
        # Get enabled models
        enabled_models = registry.get_enabled_models()
        if not enabled_models:
            raise HTTPException(status_code=400, detail="No models enabled. Please enable at least one model.")
        
        # Log enabled models and their class configurations
        enabled_names = [m["name"] for m in enabled_models]
        print(f"Enabled models: {enabled_names}")
        for m in enabled_models:
            enabled_classes = m.get("enabled_classes", {})
            if enabled_classes:
                selected = [cls for cls, enabled in enabled_classes.items() if enabled]
                print(f"  - {m['name']}: {len(selected)} classes selected: {selected if selected else 'NONE (all filtered)'}")
            else:
                print(f"  - {m['name']}: No class restrictions (all classes enabled)")
        
        # Force a clean slate: unload all existing runners before loading the new set
        print("Unloading all existing model runners before loading enabled set...")
        inference_pipeline.unload_all()
        
        # Load enabled models that aren't already loaded
        for model in enabled_models:
            model_name = model["name"]
            if model_name not in inference_pipeline.runners:
                try:
                    if not Path(model["path"]).exists():
                        raise HTTPException(status_code=404, detail=f"Model file not found: {model['path']}")
                    print(f"Loading model: {model_name}")
                    inference_pipeline.load_model(model_name, model["path"])
                except HTTPException:
                    raise
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"Failed to load model {model_name}: {error_trace}")
                    raise HTTPException(status_code=500, detail=f"Failed to load model {model_name}: {str(e)}")
            else:
                print(f"Model {model_name} already loaded")
        
        # Reset tracker for a clean start
        global tracker
        tracker = SimpleTracker()

        # Initialize capture
        source_uri = request.source.get("uri", "0")
        try:
            capture = VideoCapture(source_uri)
            capture.open()  # This raises RuntimeError if it fails
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to open video source: {source_uri}. Please check camera connection. Error: {str(e)}")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Failed to initialize capture: {error_trace}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize video capture: {str(e)}")
        
        # Initialize zone checker with zones from request
        zone_checker = ZoneChecker(request.zones)
        
        is_running = True
        frame_count = 0
        start_time = time.time()
        
        # Start detection loop
        asyncio.create_task(detection_loop())
        
        return {"status": "started", "models": [m["name"] for m in enabled_models]}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in start_detection: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to start detection: {str(e)}")


@app.post("/detector/stop")
async def stop_detection():
    """Stop detection."""
    global capture, is_running
    
    is_running = False
    if capture:
        capture.release()
        capture = None
    
    return {"status": "stopped"}


@app.get("/detector/status")
async def get_status():
    """Get detection status."""
    global frame_count, start_time
    
    fps = 0.0
    if start_time and frame_count > 0:
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0.0
    
    # Get CPU temperature (Raspberry Pi)
    temp_c = None
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_c = float(f.read().strip()) / 1000.0
    except Exception:
        pass
    
    return {
        "running": is_running,
        "fps": fps,
        "models": [m["name"] for m in registry.get_enabled_models()],
        "temp_c": temp_c
    }


async def detection_loop():
    """Main detection loop - maximum raw inference performance."""
    global frame_count, capture, is_running
    
    # Performance tracking
    loop_count = 0
    perf_start = time.time()
    
    # Cache enabled models to avoid repeated registry lookups (major bottleneck)
    cached_enabled_models = []
    cache_refresh_counter = 0
    cache_refresh_interval = 100  # Refresh every 100 frames
    
    while is_running and capture:
        # Refresh model cache occasionally instead of every iteration
        if cache_refresh_counter % cache_refresh_interval == 0:
            cached_enabled_models = registry.get_enabled_models()
            if not cached_enabled_models:
                await asyncio.sleep(0.01)
                cache_refresh_counter += 1
                continue
        
        cache_refresh_counter += 1
        
        try:
            # Read frame - native OpenCV style
            frame = capture.read()
            if frame is None:
                continue  # No sleep - keep trying at max speed
            
            frame_count += 1
            loop_count += 1
            
            # Skip frames if needed 
            if settings.frame_skip > 1 and frame_count % settings.frame_skip != 0:
                continue
            
            # PURE INFERENCE MODE - Skip all non-essential processing for max speed
            if settings.raw_inference_mode:
                # Only run inference - skip tracking, zones, but keep lightweight WebSocket
                detections = inference_pipeline.infer_frame_fast(frame, cached_enabled_models)
                
                # Lightweight WebSocket broadcast (minimal overhead)
                if ws_connections:  # Only if there are connections
                    frame_h, frame_w = frame.shape[:2]
                    frame_data = {
                        "ts": time.time(),
                        "frame_idx": frame_count,
                        "boxes": [{
                            "id": 0,
                            "cls": det.cls,
                            "conf": det.conf,
                            "xyxy": list(det.bbox),
                            "model": getattr(det, 'model_name', None)
                        } for det in detections],
                        "fps": 0.0,
                        "width": frame_w,
                        "height": frame_h
                    }
                    # Fire-and-forget broadcast (non-blocking)
                    asyncio.create_task(broadcast_detections(frame_data))
                
                # Performance logging (very minimal)
                if loop_count % 500 == 0:  # Every 500 frames
                    elapsed = time.time() - perf_start
                    fps = loop_count / elapsed if elapsed > 0 else 0
                    print(f"RAW INFERENCE FPS: {fps:.1f}")
                
                # Ultra-minimal sleep (almost zero overhead)
                if loop_count % 10 == 0:  # Only sleep every 10th frame
                    await asyncio.sleep(0.0001)
            else:
                # Full processing mode (original behavior)
                timestamp = time.time()
                detections = inference_pipeline.infer_frame(frame, cached_enabled_models)
                
                # Track objects
                tracked = tracker.update(detections, timestamp)
                
                # Check zones
                frame_h, frame_w = frame.shape[:2]
                frame_data = {
                    "ts": timestamp,
                    "frame_idx": frame_count,
                    "boxes": [],
                    "fps": 0.0,
                    "width": frame_w,
                    "height": frame_h
                }
                
                for det in tracked:
                    zone_info = zone_checker.check_detection(det) if zone_checker else None
                    
                    box_data = {
                        "id": getattr(det, 'track_id', 0),
                        "cls": det.cls,
                        "conf": det.conf,
                        "xyxy": list(det.bbox),
                        "model": getattr(det, 'model_name', None),
                        "zone": zone_info["zone_name"] if zone_info else None,
                        "event": zone_info["type"] if zone_info else None
                    }
                    frame_data["boxes"].append(box_data)
                
                # Calculate FPS
                if start_time:
                    elapsed = timestamp - start_time
                    frame_data["fps"] = frame_count / elapsed if elapsed > 0 else 0.0
                
                # Broadcast to WebSocket (fire-and-forget)
                asyncio.create_task(broadcast_detections(frame_data))
                
                # Minimal sleep
                await asyncio.sleep(settings.min_sleep_time)
                
        except Exception as e:
            # Minimal error handling for maximum speed
            if frame_count % 100 == 0:  # Only log every 100 errors
                print(f"Detection error: {e}")
            continue


async def broadcast_detections(data: dict):
    """Broadcast to WebSocket connections."""
    disconnected = []
    for ws in ws_connections:
        try:
            await ws.send_json(data)
        except Exception:
            disconnected.append(ws)
    
    for ws in disconnected:
        ws_connections.remove(ws)


@app.websocket("/ws/detections")
async def websocket_detections(websocket: WebSocket):
    """Detection stream WebSocket."""
    await websocket.accept()
    ws_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        ws_connections.remove(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """Alerts WebSocket."""
    await websocket.accept()
    alert_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        alert_connections.remove(websocket)


class AnalyzeFileRequest(BaseModel):
    """Analyze file request."""
    file_path: str
    models: List[Dict] = []
    zones: List[Dict] = []


@app.post("/detector/analyze-file")
async def analyze_file(request: AnalyzeFileRequest):
    """Analyze video file (batch processing)."""
    file_path = request.file_path
    models = request.models
    zones = request.zones
    
    if not file_path or not Path(file_path).exists():
        return {"error": "File not found"}
    
    # Update model configs
    for model_config in models:
        registry.update_model(
            model_config["name"],
            enabled=model_config.get("enabled", False),
            conf=model_config.get("conf", 0.35),
            iou=model_config.get("iou", 0.45),
            enabled_classes=model_config.get("enabled_classes", {})
        )
    
    # Update zone checker
    global zone_checker
    zone_checker = ZoneChecker(zones)
    
    # Load enabled models
    enabled_models = registry.get_enabled_models()
    if not enabled_models:
        return {"error": "No models enabled. Please enable at least one model."}
    
    for model in enabled_models:
        # Check if model is already loaded
        if model["name"] not in inference_pipeline.runners:
            try:
                inference_pipeline.load_model(model["name"], model["path"])
            except Exception as e:
                print(f"Failed to load model {model['name']}: {e}")
                return {"error": f"Failed to load model {model['name']}: {str(e)}"}
    
    # Process video file
    job_id = str(uuid.uuid4())
    asyncio.create_task(process_video_file(file_path, enabled_models, zones, job_id))
    
    return {"job_id": job_id, "status": "processing", "message": "Video analysis started"}


async def process_video_file(
    file_path: str,
    enabled_models: List[Dict],
    zones: List[Dict],
    job_id: str
):
    """Process video file asynchronously."""
    import httpx
    
    capture = VideoCapture(file_path)
    capture.open()
    
    frame_count = 0
    events = []
    backend_url = "http://localhost:8000"
    
    try:
        while True:
            frame = capture.read()
            if frame is None:
                break
            
            frame_count += 1
            timestamp = time.time()
            
            # Run inference
            detections = inference_pipeline.infer_frame(frame, enabled_models)
            
            # Track objects
            tracked = tracker.update(detections, timestamp)
            
            # Check zones and generate events (create events for all detections, not just zone intrusions)
            for det in tracked:
                zone_info = zone_checker.check_detection(det) if zone_checker else None
                
                event_data = {
                    "event_id": f"{job_id}_{frame_count}_{det.track_id if hasattr(det, 'track_id') else frame_count}",
                    "camera_id": "file",
                    "model": det.model_name if hasattr(det, 'model_name') else (enabled_models[0]["name"] if enabled_models else "unknown"),
                    "type": zone_info.get("type", "general") if zone_info else "general",
                    "zone": zone_info.get("zone_name") if zone_info else None,
                    "cls": det.cls,
                    "track_id": det.track_id if hasattr(det, 'track_id') else None,
                    "conf": det.conf,
                    "t_start": timestamp,
                    "bbox_xyxy": list(det.bbox)
                }
                events.append(event_data)
                
                # Send event to backend
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            f"{backend_url}/api/events/create",
                            json=event_data,
                            timeout=5.0
                        )
                except Exception as e:
                    print(f"Failed to send event to backend: {e}")
            
            # Save snapshot periodically
            if events and frame_count % 30 == 0:
                try:
                    import cv2
                    snap_dir = settings.storage_root_path / "snaps"
                    snap_dir.mkdir(parents=True, exist_ok=True)
                    snap_path = snap_dir / f"{job_id}_frame_{frame_count}.jpg"
                    cv2.imwrite(str(snap_path), frame)
                except Exception as e:
                    print(f"Failed to save snapshot: {e}")
    
    finally:
        capture.release()
    
    print(f"Video processing complete: {len(events)} events found")
    return {"job_id": job_id, "events": len(events)}


@app.post("/detector/snapshot")
async def take_snapshot():
    """Take snapshot from current stream."""
    global capture
    if not capture or not is_running:
        return {"error": "No active stream"}
    
    frame = capture.read()
    if frame is None:
        return {"error": "Failed to capture frame"}
    
    # Save snapshot
    import cv2
    from pathlib import Path
    snap_dir = settings.storage_root_path / "snaps"
    snap_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"snap_{int(time.time())}.jpg"
    file_path = snap_dir / filename
    
    cv2.imwrite(str(file_path), frame)
    
    return {"path": str(file_path)}


@app.get("/detector/models")
async def list_detector_models():
    """List all registered models in detection service."""
    models = registry.list_models()
    return [
        {
            "name": m["name"],
            "type": m["type"],
            "enabled": m["enabled"],
            "conf": m["conf"],
            "iou": m["iou"],
            "labels": m["labels"],
            "enabled_classes": m["enabled_classes"]
        }
        for m in models
    ]


@app.get("/")
async def root():
    return {"service": "detection-service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.detect_host, port=settings.detect_port)

