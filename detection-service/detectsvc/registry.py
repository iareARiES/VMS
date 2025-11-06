"""Model registry with class toggle support."""
from typing import Dict, List, Optional, Set
from pathlib import Path
import json
from detectsvc.config import settings


# COCO class names (YOLO standard - all 80 classes)
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]

# Note: "drone" is not in standard COCO, but may be in custom trained models
# If yolo11npRETRAINED.onnx includes drone, it will be detected automatically

# Security-relevant classes (subset of COCO + custom)
SECURITY_CLASSES = [
    "person", "car", "truck", "bus", "motorcycle", "bicycle",
    "dog", "cat", "cow", "horse", "sheep",
    "cell phone", "laptop", "backpack", "handbag", "suitcase",
    "knife", "gun"  # Note: gun not in COCO, may need custom model
]

# Face detection classes
FACE_CLASSES = ["face"]

# Fire/smoke classes
FIRE_CLASSES = ["fire", "smoke"]


class ModelRegistry:
    """Model registry with class toggle support."""
    
    def __init__(self):
        self.models: Dict[str, Dict] = {}
        self.models_root = settings.models_root_path
        self.models_root.mkdir(parents=True, exist_ok=True)
    
    def register_model(
        self,
        name: str,
        model_type: str,
        path: Optional[Path] = None,
        labels: Optional[List[str]] = None,
        enabled_classes: Optional[Dict[str, bool]] = None
    ):
        """Register a model."""
        if path is None:
            path = self.models_root / name
        
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Determine labels based on model type
        if labels is None:
            if model_type == "coco":
                labels = COCO_CLASSES
            elif model_type == "face":
                labels = FACE_CLASSES
            elif model_type == "fire":
                labels = FIRE_CLASSES
            else:
                labels = []
        
        # Initialize enabled_classes if not provided - all classes enabled by default
        if enabled_classes is None:
            enabled_classes = {cls: True for cls in labels}
        else:
            # Ensure all labels have entries in enabled_classes
            for cls in labels:
                if cls not in enabled_classes:
                    enabled_classes[cls] = True
        
        self.models[name] = {
            "name": name,
            "type": model_type,
            "path": str(path),
            "labels": labels,
            "enabled": False,
            "conf": 0.35,
            "iou": 0.45,
            "enabled_classes": enabled_classes,
            "runner": None  # Will be set when loaded
        }
    
    def get_model(self, name: str) -> Optional[Dict]:
        """Get model config."""
        return self.models.get(name)
    
    def list_models(self) -> List[Dict]:
        """List all registered models."""
        return list(self.models.values())
    
    def update_model(
        self,
        name: str,
        enabled: Optional[bool] = None,
        conf: Optional[float] = None,
        iou: Optional[float] = None,
        enabled_classes: Optional[Dict[str, bool]] = None
    ):
        """Update model settings."""
        if name not in self.models:
            raise ValueError(f"Model not found: {name}")
        
        model = self.models[name]
        if enabled is not None:
            model["enabled"] = enabled
        if conf is not None:
            model["conf"] = conf
        if iou is not None:
            model["iou"] = iou
        if enabled_classes is not None:
            # Merge with existing
            model["enabled_classes"].update(enabled_classes)
    
    def get_enabled_models(self) -> List[Dict]:
        """Get all enabled models."""
        return [m for m in self.models.values() if m["enabled"]]
    
    def is_class_enabled(self, model_name: str, class_name: str) -> bool:
        """Check if a class is enabled for a model."""
        model = self.models.get(model_name)
        if not model:
            return False
        if not model["enabled"]:
            return False
        return model["enabled_classes"].get(class_name, True)  # Default to enabled
    
    def get_all_classes(self) -> Set[str]:
        """Get all unique class names across all models."""
        all_classes = set()
        for model in self.models.values():
            all_classes.update(model["labels"])
        return all_classes
    
    def auto_register_models(self):
        """Auto-register models from models directory."""
        model_files = {
            "best.onnx": "face",
            "w600k_mbf.onnx": "face",
            "yolo11npRETRAINED.onnx": "coco",
            "Fire_Event_best.onnx": "fire",
            "Fire_Event_best.pt": "fire"
        }
        
        for filename, model_type in model_files.items():
            path = self.models_root / filename
            if path.exists():
                try:
                    self.register_model(filename, model_type, path)
                except Exception as e:
                    print(f"Failed to register {filename}: {e}")


# Global registry instance
registry = ModelRegistry()

