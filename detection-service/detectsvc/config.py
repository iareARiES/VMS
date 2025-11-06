"""Detection service configuration."""
from pydantic_settings import BaseSettings
from pathlib import Path


def _resolve_path(path_str: str) -> Path:
    """Resolve path - make absolute if relative, handle both Windows and Linux."""
    path = Path(path_str)
    if not path.is_absolute():
        # Make relative to project root
        project_root = Path(__file__).parent.parent.parent
        path = project_root / path
    return path.resolve()


class Settings(BaseSettings):
    """Detection service settings."""
    
    # Server
    detect_host: str = "0.0.0.0"
    detect_port: int = 8010
    
    # Models
    models_root: str = "models"  # Relative to project root, override in .env
    
    # Inference - Maximum performance settings
    infer_device: str = "onnx_cpu"  # onnx_cpu, hailo, coral
    target_fps: int = 120  # Maximum FPS for native script-like performance
    frame_skip: int = 1  # Process every frame (no skipping for maximum responsiveness)
    min_sleep_time: float = 0.0001  # Ultra-minimal sleep time (0.1ms) 
    
    # Performance mode flags
    raw_inference_mode: bool = True  # Skip tracking, zones, WebSocket for max speed
    cache_enabled_models: bool = True  # Cache model list to avoid registry lookups
    
    # Storage
    storage_root: str = "storage"  # Relative to project root, override in .env
    snap_max_per_event: int = 10
    
    @property
    def models_root_path(self) -> Path:
        """Get models root as Path object."""
        return _resolve_path(self.models_root)
    
    @property
    def storage_root_path(self) -> Path:
        """Get storage root as Path object."""
        return _resolve_path(self.storage_root)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

