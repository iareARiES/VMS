"""Database models."""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Event(Base):
    """Event table."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    camera_id = Column(String, default="default")
    model = Column(String)
    type = Column(String)  # intrusion, tripwire, loitering, fire, face_known, face_unknown, general
    zone = Column(String, nullable=True)
    cls = Column(String)  # detected class
    track_id = Column(Integer, nullable=True)
    conf = Column(Float)
    t_start = Column(Float, index=True)
    t_end = Column(Float, nullable=True)
    snapshot_path = Column(String, nullable=True)
    video_ref = Column(String, nullable=True)
    bbox_xyxy = Column(JSON)  # [x1, y1, x2, y2]
    event_metadata = Column(JSON, default={})  # Renamed from 'metadata' (SQLAlchemy reserved)
    created_at = Column(DateTime, server_default=func.now())


class Zone(Base):
    """Zone table."""
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String, unique=True, index=True)
    name = Column(String)
    type = Column(String)  # polygon, tripwire
    points = Column(JSON)  # [[x, y], ...]
    direction = Column(String, nullable=True)  # AtoB, BtoA
    allowed_classes = Column(JSON, default=[])
    min_size_px = Column(Integer, default=0)
    dwell_sec = Column(Float, default=0.0)
    active_schedule = Column(JSON, nullable=True)
    style = Column(JSON, default={"stroke": "#ff0000", "width": 2, "opacity": 0.6})
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Model(Base):
    """Model configuration table."""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String)  # coco, face, fire, custom
    enabled = Column(Boolean, default=True)
    conf = Column(Float, default=0.35)
    iou = Column(Float, default=0.45)
    labels = Column(JSON, default=[])
    enabled_classes = Column(JSON, default={})  # {class_name: bool}
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class User(Base):
    """User table."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")  # admin, operator, viewer
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class SOSLog(Base):
    """SOS trigger log."""
    __tablename__ = "sos_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)  # trigger, cancel
    triggered_by = Column(String)  # user_id or "auto"
    event_id = Column(String, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())

