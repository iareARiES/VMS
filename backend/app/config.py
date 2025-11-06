"""Backend configuration."""
from pydantic_settings import BaseSettings
from pathlib import Path
import os


def _resolve_path(path_str: str) -> Path:
    """Resolve path - make absolute if relative, handle both Windows and Linux."""
    path = Path(path_str)
    if not path.is_absolute():
        # Make relative to project root
        project_root = Path(__file__).parent.parent.parent
        path = project_root / path
    return path.resolve()


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_env: str = "prod"
    # Default paths - will be overridden by .env or auto-detected
    storage_root: str = "storage"
    models_root: str = "models"
    
    @property
    def storage_root_path(self) -> Path:
        """Get storage root as Path object."""
        return _resolve_path(self.storage_root)
    
    @property
    def models_root_path(self) -> Path:
        """Get models root as Path object."""
        return _resolve_path(self.models_root)
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Database
    db_url: str = "sqlite:///storage/db/events.sqlite"
    
    # Security
    jwt_secret: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    
    # Detection Service
    detection_service_url: str = "http://localhost:8010"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

