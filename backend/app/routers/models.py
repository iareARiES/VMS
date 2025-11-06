"""Models router."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import shutil
import uuid

from app.deps import get_db
from app.db.repo import ModelRepo
from app.config import settings
from app.services.detection_client import detection_client


router = APIRouter(prefix="/api/models", tags=["models"])


class ModelResponse(BaseModel):
    """Model response."""
    name: str
    type: str
    enabled: bool
    conf: float
    iou: float
    labels: List[str]
    enabled_classes: dict


class ModelUpdate(BaseModel):
    """Model update request."""
    enabled: Optional[bool] = None
    conf: Optional[float] = None
    iou: Optional[float] = None
    enabled_classes: Optional[dict] = None


@router.get("", response_model=List[ModelResponse])
async def list_models(db: Session = Depends(get_db)):
    """List all models."""
    models = ModelRepo.list(db)
    return [
        ModelResponse(
            name=m.name,
            type=m.type,
            enabled=m.enabled,
            conf=m.conf,
            iou=m.iou,
            labels=m.labels or [],
            enabled_classes=m.enabled_classes or {}
        )
        for m in models
    ]


@router.post("")
async def upload_model(
    file: UploadFile = File(...),
    type: str = "custom",
    db: Session = Depends(get_db)
):
    """Upload new model."""
    if not file.filename.endswith(('.onnx', '.pt', '.pth')):
        raise HTTPException(status_code=400, detail="Invalid model file format")
    
    # Save to models directory
    models_dir = settings.models_root_path
    models_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = models_dir / file.filename
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Create model record
    model_data = {
        "name": file.filename,
        "type": type,
        "enabled": False,
        "conf": 0.35,
        "iou": 0.45,
        "labels": [],
        "enabled_classes": {}
    }
    
    model = ModelRepo.create(db, model_data)
    return {"name": model.name, "type": model.type, "message": "Model uploaded"}


@router.put("/{model_name}")
async def update_model(
    model_name: str,
    update: ModelUpdate,
    db: Session = Depends(get_db)
):
    """Update model settings."""
    update_data = update.dict(exclude_unset=True)
    model = ModelRepo.update(db, model_name, update_data)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Sync update to detection service
    try:
        await detection_client.update_model_config(
            model_name,
            enabled=model.enabled,
            conf=model.conf,
            iou=model.iou,
            enabled_classes=model.enabled_classes or {}
        )
    except Exception as e:
        print(f"Failed to sync model update to detection service: {e}")
    
    return {
        "name": model.name,
        "enabled": model.enabled,
        "conf": model.conf,
        "iou": model.iou,
        "enabled_classes": model.enabled_classes
    }


@router.delete("/{model_name}")
async def delete_model(
    model_name: str,
    db: Session = Depends(get_db)
):
    """Delete model."""
    model = ModelRepo.get_by_name(db, model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Delete file
    models_dir = Path(settings.models_root)
    file_path = models_dir / model_name
    if file_path.exists():
        file_path.unlink()
    
    # Delete from DB
    db.delete(model)
    db.commit()
    
    return {"message": "Model deleted"}

