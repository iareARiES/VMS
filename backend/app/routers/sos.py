"""SOS router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.deps import get_db
from app.db.models import SOSLog


router = APIRouter(prefix="/api/sos", tags=["sos"])


class SOSRequest(BaseModel):
    """SOS request."""
    action: str  # trigger, cancel
    event_id: Optional[str] = None


class SOSResponse(BaseModel):
    """SOS response."""
    status: str
    message: str
    timestamp: float


@router.post("", response_model=SOSResponse)
async def sos_action(
    request: SOSRequest,
    db: Session = Depends(get_db)
):
    """Trigger or cancel SOS."""
    import time
    
    if request.action not in ["trigger", "cancel"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Log SOS action
    log = SOSLog(
        action=request.action,
        triggered_by="manual",  # TODO: get from auth
        event_id=request.event_id
    )
    db.add(log)
    db.commit()
    
    # TODO: Trigger GPIO signal, webhook, email, etc.
    
    return SOSResponse(
        status=request.action,
        message=f"SOS {request.action}ed",
        timestamp=time.time()
    )

