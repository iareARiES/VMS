"""Dependencies."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path
from app.config import settings
from app.db.models import Base

# Ensure database directory exists
def _ensure_db_dir():
    """Ensure database directory exists."""
    if "sqlite" in settings.db_url:
        # Extract path from sqlite:///path/to/db.sqlite
        db_path_str = settings.db_url.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path_str
    return None

# Database
_db_path = _ensure_db_dir()
if _db_path and not _db_path.startswith("/"):
    # Make path absolute relative to project root
    project_root = Path(__file__).parent.parent.parent
    _db_path = str(project_root / _db_path)

# Build database URL
if "sqlite" in settings.db_url:
    db_url = f"sqlite:///{_db_path}" if _db_path else settings.db_url
else:
    db_url = settings.db_url

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - creates all tables."""
    # Ensure directory exists
    _ensure_db_dir()
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {db_url}")


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

