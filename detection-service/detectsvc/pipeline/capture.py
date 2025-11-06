"""Video capture module."""
import cv2
from typing import Optional, Union
from pathlib import Path


class VideoCapture:
    """Video capture wrapper."""
    
    def __init__(self, source: Union[str, int, Path]):
        self.source = source
        self.cap = None
    
    def open(self):
        """Open capture with maximum performance optimizations."""
        try:
            if isinstance(self.source, (str, Path)):
                source_str = str(self.source)
                # Try to convert string "0" to int for camera
                if source_str == "0" or source_str.isdigit():
                    self.cap = cv2.VideoCapture(int(source_str))
                else:
                    self.cap = cv2.VideoCapture(source_str)
            else:
                self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open video source: {self.source}. Camera may not be available or already in use.")
            
            # Maximum performance optimizations
            try:
                # Minimal buffer for lowest latency (like native scripts)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # High FPS for cameras
                if isinstance(self.source, int) or (isinstance(self.source, str) and source_str.isdigit()):
                    self.cap.set(cv2.CAP_PROP_FPS, 60)  # Try 60 FPS first
                    
                # Optimize threading and backend
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                
                # Disable auto-exposure for consistent timing (if supported)
                try:
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure
                except:
                    pass
                    
            except:
                pass  # Some backends don't support these optimizations
                
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Error initializing video capture: {str(e)}")
    
    def read(self) -> Optional[tuple]:
        """Read frame with maximum speed (like native OpenCV scripts)."""
        if self.cap is None:
            return None
        
        # Native OpenCV approach: direct read() for maximum speed
        # This is exactly how you'd do it in a traditional Python script
        ret, frame = self.cap.read()
        
        if ret and frame is not None:
            return frame
        
        return None
    
    def release(self):
        """Release capture."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def get_fps(self) -> float:
        """Get FPS."""
        if self.cap:
            return self.cap.get(cv2.CAP_PROP_FPS)
        return 30.0
    
    def get_size(self) -> tuple:
        """Get frame size."""
        if self.cap:
            w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (w, h)
        return (640, 480)

