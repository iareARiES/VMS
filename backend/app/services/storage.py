"""File storage management."""
from pathlib import Path
from typing import Optional
import aiofiles
import shutil
from app.config import settings


class StorageService:
    """Storage service for snapshots, clips, videos."""
    
    def __init__(self):
        self.storage_root = settings.storage_root_path
        self.videos_dir = self.storage_root / "videos"
        self.snaps_dir = self.storage_root / "snaps"
        self.clips_dir = self.storage_root / "clips"
        
        # Create directories
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.snaps_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir.mkdir(parents=True, exist_ok=True)
    
    def get_video_path(self, filename: str) -> Path:
        """Get video file path."""
        return self.videos_dir / filename
    
    def get_snapshot_path(self, filename: str) -> Path:
        """Get snapshot file path."""
        return self.snaps_dir / filename
    
    def get_clip_path(self, filename: str) -> Path:
        """Get clip file path."""
        return self.clips_dir / filename
    
    async def save_upload(self, file_content: bytes, filename: str) -> Path:
        """Save uploaded file."""
        file_path = self.get_video_path(filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        return file_path
    
    def delete_file(self, file_path: Path) -> bool:
        """Delete file."""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False


storage_service = StorageService()

