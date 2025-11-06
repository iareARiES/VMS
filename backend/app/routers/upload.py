"""Upload router."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from pathlib import Path

from app.deps import get_db
from app.services.storage import storage_service
from app.services.detection_client import detection_client
from app.db.repo import ZoneRepo, ModelRepo


router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload video for analysis."""
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    # Save file
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = await storage_service.save_upload(await file.read(), filename)
    
    # Get active models and zones
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
    
    # Request analysis from detection service
    try:
        result = await detection_client.analyze_file(
            file_path=str(file_path),
            models=model_configs,
            zones=zone_configs
        )
        return {
            "job_id": result.get("job_id"),
            "file_path": str(file_path),
            "message": "Video uploaded and queued for analysis"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image for analysis."""
    if not file.filename or not any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']):
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    # Save file
    import aiofiles
    from app.config import settings
    
    uploads_dir = settings.storage_root_path / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = uploads_dir / filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Get active models
    models = ModelRepo.list(db)
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
    
    if not model_configs:
        raise HTTPException(status_code=400, detail="No models enabled. Please enable at least one model.")
    
    # Request analysis from detection service
    try:
        from app.config import settings
        import httpx
        
        # Send image to detection service for analysis
        async with httpx.AsyncClient() as client:
            try:
                with open(file_path, 'rb') as f:
                    files = {"file": (filename, f, file.content_type)}
                    response = await client.post(
                        f"{settings.detection_service_url}/detector/analyze-image",
                        files=files,
                        data={"models": str(model_configs)},
                        timeout=30.0
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "detections": result.get("detections", []),
                        "annotated_image": result.get("annotated_image"),
                        "original_image": f"/storage/uploads/{filename}"
                    }
            except httpx.HTTPStatusError:
                # Detection service doesn't have image endpoint yet
                pass
            except Exception:
                pass
        
        # Fallback: return basic response
        return {
            "detections": [],
            "message": "Image uploaded. Detection service image analysis endpoint coming soon."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")