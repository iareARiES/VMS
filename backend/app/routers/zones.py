"""Zones router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.deps import get_db
from app.db.repo import ZoneRepo


router = APIRouter(prefix="/api/zones", tags=["zones"])


class ZoneRequest(BaseModel):
    """Zone request."""
    zone_id: Optional[str] = None
    name: str
    type: str  # polygon, tripwire
    points: List[List[float]]
    direction: Optional[str] = None
    allowed_classes: List[str] = []
    min_size_px: int = 0
    dwell_sec: float = 0.0
    active_schedule: Optional[dict] = None
    style: dict = {"stroke": "#ff0000", "width": 2, "opacity": 0.6}


class ZoneResponse(BaseModel):
    """Zone response."""
    zone_id: str
    name: str
    type: str
    points: List[List[float]]
    direction: Optional[str]
    allowed_classes: List[str]
    min_size_px: int
    dwell_sec: float
    active_schedule: Optional[dict]
    style: dict


@router.get("", response_model=List[ZoneResponse])
async def list_zones(db: Session = Depends(get_db)):
    """List all zones."""
    zones = ZoneRepo.list(db)
    return [
        ZoneResponse(
            zone_id=z.zone_id,
            name=z.name,
            type=z.type,
            points=z.points,
            direction=z.direction,
            allowed_classes=z.allowed_classes or [],
            min_size_px=z.min_size_px,
            dwell_sec=z.dwell_sec,
            active_schedule=z.active_schedule,
            style=z.style or {"stroke": "#ff0000", "width": 2, "opacity": 0.6}
        )
        for z in zones
    ]


@router.post("", response_model=ZoneResponse)
async def create_zone(zone: ZoneRequest, db: Session = Depends(get_db)):
    """Create zone."""
    import uuid
    
    zone_data = zone.dict()
    if not zone_data.get("zone_id"):
        zone_data["zone_id"] = f"zone_{uuid.uuid4().hex[:8]}"
    
    created = ZoneRepo.create(db, zone_data)
    return ZoneResponse(
        zone_id=created.zone_id,
        name=created.name,
        type=created.type,
        points=created.points,
        direction=created.direction,
        allowed_classes=created.allowed_classes or [],
        min_size_px=created.min_size_px,
        dwell_sec=created.dwell_sec,
        active_schedule=created.active_schedule,
        style=created.style or {"stroke": "#ff0000", "width": 2, "opacity": 0.6}
    )


@router.put("/{zone_id}", response_model=ZoneResponse)
async def update_zone(zone_id: str, zone: ZoneRequest, db: Session = Depends(get_db)):
    """Update zone."""
    zone_data = zone.dict(exclude={"zone_id"})
    updated = ZoneRepo.update(db, zone_id, zone_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    return ZoneResponse(
        zone_id=updated.zone_id,
        name=updated.name,
        type=updated.type,
        points=updated.points,
        direction=updated.direction,
        allowed_classes=updated.allowed_classes or [],
        min_size_px=updated.min_size_px,
        dwell_sec=updated.dwell_sec,
        active_schedule=updated.active_schedule,
        style=updated.style or {"stroke": "#ff0000", "width": 2, "opacity": 0.6}
    )


@router.delete("/{zone_id}")
async def delete_zone(zone_id: str, db: Session = Depends(get_db)):
    """Delete zone."""
    success = ZoneRepo.delete(db, zone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"message": "Zone deleted"}

