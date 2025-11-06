"""Main FastAPI application."""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.deps import init_db
from app.routers import models, zones, events, upload, query, sos, system
from app.ws import live, alerts
import httpx


app = FastAPI(
    title="Intrusion Detection Backend",
    version="1.0.0",
    description="Backend API for intrusion detection system"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Sync models from detection service on startup
@app.on_event("startup")
async def sync_models():
    """Sync models from detection service to backend DB."""
    try:
        from app.services.detection_client import detection_client
        from app.db.repo import ModelRepo
        from app.deps import SessionLocal
        
        # Get models from detection service
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.detection_service_url}/detector/models")
            if response.status_code == 200:
                detector_models = response.json()
                
                db = SessionLocal()
                try:
                    for model_data in detector_models:
                        existing = ModelRepo.get_by_name(db, model_data["name"])
                        if not existing:
                            # Create new model record
                            ModelRepo.create(db, {
                                "name": model_data["name"],
                                "type": model_data["type"],
                                "enabled": model_data.get("enabled", False),
                                "conf": model_data.get("conf", 0.35),
                                "iou": model_data.get("iou", 0.45),
                                "labels": model_data.get("labels", []),
                                "enabled_classes": model_data.get("enabled_classes", {})
                            })
                        else:
                            # Update existing - preserve enabled state, only update labels and classes
                            ModelRepo.update(db, model_data["name"], {
                                "labels": model_data.get("labels", []),
                                "enabled_classes": model_data.get("enabled_classes", {})
                                # Note: We don't update 'enabled' here to preserve user's choice
                            })
                finally:
                    db.close()
    except Exception as e:
        print(f"Failed to sync models: {e}")

# Static files (for serving uploaded images, snapshots, etc.)
storage_path = settings.storage_root_path
if storage_path.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# Routers
app.include_router(models.router)
app.include_router(zones.router)
app.include_router(events.router)
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(sos.router)
app.include_router(system.router)

# WebSocket endpoints
@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await live.websocket_live(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await alerts.websocket_alerts(websocket)


@app.get("/")
async def root():
    return {"message": "Intrusion Detection Backend API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port)

