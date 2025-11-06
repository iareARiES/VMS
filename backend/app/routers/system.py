"""System router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import psutil
import platform
import httpx
import asyncio

from app.deps import get_db
from app.services.detection_client import detection_client


router = APIRouter(prefix="/api/system", tags=["system"])


class SystemHealth(BaseModel):
    """System health response."""
    cpu_percent: float
    ram_percent: float
    temp_c: Optional[float] = None
    fps: Optional[float] = None
    queue_depth: int = 0


@router.get("/health", response_model=SystemHealth)
async def get_health(db: Session = Depends(get_db)):
    """Get system health."""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    
    # Try to get detection service status
    fps = None
    temp_c = None
    try:
        status = await detection_client.status()
        fps = status.get("fps")
        temp_c = status.get("temp_c")
    except Exception:
        pass
    
    # Try to get CPU temperature (Raspberry Pi)
    if temp_c is None:
        try:
            if platform.system() == "Linux":
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    temp_c = float(f.read().strip()) / 1000.0
        except Exception:
            pass
    
    return SystemHealth(
        cpu_percent=cpu_percent,
        ram_percent=ram.percent,
        temp_c=temp_c,
        fps=fps,
        queue_depth=0
    )


@router.post("/detection/start")
async def start_detection():
    """Start detection service for live preview."""
    try:
        from app.db.repo import ModelRepo, ZoneRepo
        from app.deps import SessionLocal
        
        db = SessionLocal()
        try:
            models = ModelRepo.list(db)
            zones = ZoneRepo.list(db)
            
            model_configs = [
                {
                    "name": m.name,
                    "enabled": m.enabled,
                    "conf": m.conf,
                    "iou": m.iou,
                    "enabled_classes": m.enabled_classes or {}
                }
                for m in models if m.enabled
            ]
            
            # Check if any models are enabled
            if not model_configs:
                raise HTTPException(
                    status_code=400,
                    detail="No models enabled. Please enable at least one model in the Models page."
                )
            
            zone_configs = [
                {
                    "zone_id": z.zone_id,
                    "name": z.name,
                    "type": z.type,
                    "points": z.points,
                    "allowed_classes": z.allowed_classes or [],
                    "min_size_px": z.min_size_px,
                    "dwell_sec": z.dwell_sec
                }
                for z in zones
            ]
            
            # If detection is already running, stop it to apply new model set
            try:
                status = await detection_client.status()
                if status.get("running", False):
                    try:
                        await detection_client.stop()
                        await asyncio.sleep(0.2)
                    except Exception:
                        # Best-effort stop
                        pass
            except Exception:
                # If status check fails, continue to try starting
                pass
            
            # Start detection with webcam (0) or test video
            try:
                result = await detection_client.start(
                    source={"type": "usb", "uri": "0"},  # Webcam
                    models=model_configs,
                    zones=zone_configs,
                    zones_version="1"
                )
                return result
            except httpx.HTTPStatusError as e:
                # Get error details from detection service
                error_detail = "Unknown error"
                try:
                    error_json = e.response.json()
                    error_detail = error_json.get("detail", error_json.get("error", str(e)))
                except:
                    # Try to extract from error message
                    error_msg = str(e)
                    if "Detection service error:" in error_msg:
                        error_detail = error_msg.split("Detection service error:")[-1].strip()
                    else:
                        error_detail = error_msg
                
                # If detection is already running, force-restart with new models
                if "already running" in error_detail.lower() or e.response.status_code == 400:
                    try:
                        await detection_client.stop()
                        await asyncio.sleep(0.2)
                        result = await detection_client.start(
                            source={"type": "usb", "uri": "0"},
                            models=model_configs,
                            zones=zone_configs,
                            zones_version="1"
                        )
                        return result
                    except Exception:
                        pass
                
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=error_detail
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Cannot connect to detection service: {str(e)}"
                )
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error starting detection: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to start detection: {str(e)}")


@router.post("/detection/stop")
async def stop_detection():
    """Stop detection service."""
    try:
        result = await detection_client.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop detection: {str(e)}")
