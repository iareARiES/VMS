"""Database repository."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .models import Event, Zone, Model, User, SOSLog


class EventRepo:
    """Event repository."""
    
    @staticmethod
    def create(db: Session, event_data: Dict[str, Any]) -> Event:
        """Create event."""
        event = Event(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def get_by_id(db: Session, event_id: str) -> Optional[Event]:
        """Get event by ID."""
        return db.query(Event).filter(Event.event_id == event_id).first()
    
    @staticmethod
    def list(
        db: Session,
        zone: Optional[str] = None,
        cls: Optional[str] = None,
        model: Optional[str] = None,
        t_start: Optional[float] = None,
        t_end: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """List events with filters."""
        query = db.query(Event)
        
        if zone:
            query = query.filter(Event.zone == zone)
        if cls:
            query = query.filter(Event.cls == cls)
        if model:
            query = query.filter(Event.model == model)
        if t_start:
            query = query.filter(Event.t_start >= t_start)
        if t_end:
            query = query.filter(Event.t_start <= t_end)
        
        return query.order_by(Event.t_start.desc()).limit(limit).offset(offset).all()


class ZoneRepo:
    """Zone repository."""
    
    @staticmethod
    def create(db: Session, zone_data: Dict[str, Any]) -> Zone:
        """Create zone."""
        zone = Zone(**zone_data)
        db.add(zone)
        db.commit()
        db.refresh(zone)
        return zone
    
    @staticmethod
    def get_by_id(db: Session, zone_id: str) -> Optional[Zone]:
        """Get zone by ID."""
        return db.query(Zone).filter(Zone.zone_id == zone_id).first()
    
    @staticmethod
    def list(db: Session) -> List[Zone]:
        """List all zones."""
        return db.query(Zone).all()
    
    @staticmethod
    def update(db: Session, zone_id: str, zone_data: Dict[str, Any]) -> Optional[Zone]:
        """Update zone."""
        zone = ZoneRepo.get_by_id(db, zone_id)
        if not zone:
            return None
        
        for key, value in zone_data.items():
            setattr(zone, key, value)
        
        db.commit()
        db.refresh(zone)
        return zone
    
    @staticmethod
    def delete(db: Session, zone_id: str) -> bool:
        """Delete zone."""
        zone = ZoneRepo.get_by_id(db, zone_id)
        if not zone:
            return False
        
        db.delete(zone)
        db.commit()
        return True


class ModelRepo:
    """Model repository."""
    
    @staticmethod
    def create(db: Session, model_data: Dict[str, Any]) -> Model:
        """Create model config."""
        model = Model(**model_data)
        db.add(model)
        db.commit()
        db.refresh(model)
        return model
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Model]:
        """Get model by name."""
        return db.query(Model).filter(Model.name == name).first()
    
    @staticmethod
    def list(db: Session) -> List[Model]:
        """List all models."""
        return db.query(Model).all()
    
    @staticmethod
    def update(db: Session, name: str, model_data: Dict[str, Any]) -> Optional[Model]:
        """Update model."""
        model = ModelRepo.get_by_name(db, name)
        if not model:
            return None
        
        for key, value in model_data.items():
            setattr(model, key, value)
        
        db.commit()
        db.refresh(model)
        return model

