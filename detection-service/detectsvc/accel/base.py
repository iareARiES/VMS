"""Base accelerator interface."""
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
from pathlib import Path


class Detection:
    """Single detection."""
    def __init__(
        self,
        cls: str,
        conf: float,
        bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    ):
        self.cls = cls
        self.conf = conf
        self.bbox = bbox
        self.track_id = None  # Will be set by tracker
        self.model_name = None  # Will be set by inference pipeline


class AcceleratorRunner(ABC):
    """Base class for inference runners."""
    
    @abstractmethod
    def load(self, model_path: Path):
        """Load model."""
        pass
    
    @abstractmethod
    def infer(self, image: np.ndarray) -> List[Detection]:
        """Run inference on image (BGR format)."""
        pass
    
    @abstractmethod
    def get_input_shape(self) -> Tuple[int, int]:
        """Get expected input shape (height, width)."""
        pass

