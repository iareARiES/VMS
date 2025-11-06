"""Events router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.deps import get_db
from app.db.repo import EventRepo


router = APIRouter(prefix="/api/events", tags=["events"])


class EventResponse(BaseModel):
    """Event response."""
    event_id: str
    camera_id: str
    model: str
    type: str
    zone: Optional[str]
    cls: str
    track_id: Optional[int]
    conf: float
    t_start: float
    t_end: Optional[float]
    snapshot_path: Optional[str]
    video_ref: Optional[str]
    bbox_xyxy: List[float]


class EventCreate(BaseModel):
    """Event creation request."""
    event_id: str
    camera_id: str = "default"
    model: str
    type: str
    zone: Optional[str] = None
    cls: str
    track_id: Optional[int] = None
    conf: float
    t_start: float
    t_end: Optional[float] = None
    snapshot_path: Optional[str] = None
    video_ref: Optional[str] = None
    bbox_xyxy: List[float] = []


@router.post("/create")
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
    event_data = {
        "event_id": event.event_id,
        "camera_id": event.camera_id,
        "model": event.model,
        "type": event.type,
        "zone": event.zone,
        "cls": event.cls,
        "track_id": event.track_id,
        "conf": event.conf,
        "t_start": event.t_start,
        "t_end": event.t_end,
        "snapshot_path": event.snapshot_path,
        "video_ref": event.video_ref,
        "bbox_xyxy": event.bbox_xyxy
    }
    created = EventRepo.create(db, event_data)
    return EventResponse(
        event_id=created.event_id,
        camera_id=created.camera_id,
        model=created.model,
        type=created.type,
        zone=created.zone,
        cls=created.cls,
        track_id=created.track_id,
        conf=created.conf,
        t_start=created.t_start,
        t_end=created.t_end,
        snapshot_path=created.snapshot_path,
        video_ref=created.video_ref,
        bbox_xyxy=created.bbox_xyxy or []
    )


@router.get("", response_model=List[EventResponse])
async def list_events(
    zone: Optional[str] = Query(None),
    cls: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    t_start: Optional[float] = Query(None),
    t_end: Optional[float] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List events with filters."""
    events = EventRepo.list(
        db=db,
        zone=zone,
        cls=cls,
        model=model,
        t_start=t_start,
        t_end=t_end,
        limit=limit,
        offset=offset
    )
    
    return [
        EventResponse(
            event_id=e.event_id,
            camera_id=e.camera_id,
            model=e.model,
            type=e.type,
            zone=e.zone,
            cls=e.cls,
            track_id=e.track_id,
            conf=e.conf,
            t_start=e.t_start,
            t_end=e.t_end,
            snapshot_path=e.snapshot_path,
            video_ref=e.video_ref,
            bbox_xyxy=e.bbox_xyxy or []
        )
        for e in events
    ]

