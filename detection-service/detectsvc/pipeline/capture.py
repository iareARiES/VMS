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
        """Open capture with low-latency settings."""
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
            
            # Optimize for low latency: reduce buffer size
            # Set buffer size to 1 to minimize latency (always get latest frame)
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except:
                pass  # Some backends don't support this
            
            # Try to set FPS if it's a camera
            try:
                if isinstance(self.source, int) or (isinstance(self.source, str) and source_str.isdigit()):
                    self.cap.set(cv2.CAP_PROP_FPS, 30)  # Request 30 FPS from camera
            except:
                pass  # Some cameras don't support FPS setting
                
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Error initializing video capture: {str(e)}")
    
    def read(self) -> Optional[tuple]:
        """Read latest frame (drops old frames to reduce latency)."""
        if self.cap is None:
            return None
        
        # For low latency: grab frames until we get the latest one
        # This ensures we always process the most recent frame, not a buffered one
        ret = False
        frame = None
        
        # Grab frames to clear buffer (get latest frame)
        # Grab 2-3 times to ensure we get the latest frame
        for _ in range(2):
            if self.cap.grab():
                ret, frame = self.cap.retrieve()
            else:
                break
        
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

