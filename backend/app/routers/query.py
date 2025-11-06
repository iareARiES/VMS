"""Query router (chatbot)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import re
from datetime import datetime, timedelta

from app.deps import get_db
from app.db.repo import EventRepo


router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    """Query request."""
    query: str
    t_start: Optional[float] = None
    t_end: Optional[float] = None


class QueryResult(BaseModel):
    """Query result."""
    event_id: str
    cls: str
    conf: float
    t_start: float
    snapshot_path: Optional[str]
    bbox_xyxy: List[float]
    zone: Optional[str]


@router.post("", response_model=List[QueryResult])
async def query_events(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Chatbot query - parse query string and return matching events."""
    query = request.query.lower()
    
    # Extract object class from query
    # Common patterns: "find me person", "show cars", "detect fire", etc.
    class_keywords = {
        "person": "person", "human": "person", "people": "person",
        "car": "car", "vehicle": "car", "automobile": "car",
        "dog": "dog", "dogs": "dog",
        "cat": "cat", "cats": "cat",
        "cow": "cow", "cattle": "cow",
        "phone": "cell phone", "mobile": "cell phone", "smartphone": "cell phone",
        "laptop": "laptop", "computer": "laptop",
        "drone": "drone", "uav": "drone",
        "bag": "handbag", "suitcase": "suitcase", "luggage": "suitcase",
        "fire": "fire", "smoke": "smoke",
        "face": "face"
    }
    
    detected_class = None
    for keyword, class_name in class_keywords.items():
        if keyword in query:
            detected_class = class_name
            break
    
    # Extract time range from query if not provided
    t_start = request.t_start
    t_end = request.t_end
    
    if not t_start or not t_end:
        # Try to parse relative times: "last hour", "today", "yesterday"
        now = datetime.now().timestamp()
        if "last hour" in query or "past hour" in query:
            t_start = now - 3600
            t_end = now
        elif "today" in query:
            today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
            t_start = today_start
            t_end = now
        elif "yesterday" in query:
            yesterday = datetime.now() - timedelta(days=1)
            t_start = yesterday.replace(hour=0, minute=0, second=0).timestamp()
            t_end = yesterday.replace(hour=23, minute=59, second=59).timestamp()
    
    # Query events
    events = EventRepo.list(
        db=db,
        cls=detected_class,
        t_start=t_start,
        t_end=t_end,
        limit=100
    )
    
    return [
        QueryResult(
            event_id=e.event_id,
            cls=e.cls,
            conf=e.conf,
            t_start=e.t_start,
            snapshot_path=e.snapshot_path,
            bbox_xyxy=e.bbox_xyxy or [],
            zone=e.zone
        )
        for e in events
    ]

