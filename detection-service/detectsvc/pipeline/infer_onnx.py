"""ONNX inference pipeline."""
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict
from detectsvc.accel.onnx_cpu import ONNXCPURunner
from detectsvc.accel.base import Detection
from detectsvc.registry import registry


class InferencePipeline:
    """Inference pipeline with class filtering."""
    
    def __init__(self):
        self.runners: Dict[str, ONNXCPURunner] = {}
        self._debug_counter = 0
    
    def load_model(self, model_name: str, model_path: str):
        """Load a model."""
        runner = ONNXCPURunner()
        runner.load(Path(model_path))
        
        # Set class names from registry
        model = registry.get_model(model_name)
        if model:
            runner.class_names = model["labels"]
        
        self.runners[model_name] = runner
    
    def unload_model(self, model_name: str):
        """Unload a model."""
        if model_name in self.runners:
            del self.runners[model_name]
    
    def unload_all(self):
        """Unload all models."""
        self.runners.clear()
    
    def infer_frame_fast(
        self,
        frame: np.ndarray,
        enabled_models: List[Dict]
    ) -> List[Detection]:
        """Run raw inference with minimal overhead - maximum speed."""
        all_detections = []
        
        # Streamlined processing - no safety checks, minimal overhead
        for model_config in enabled_models:
            model_name = model_config["name"]
            
            # Skip if not loaded (minimal check)
            if model_name not in self.runners:
                continue
            
            runner = self.runners[model_name]
            
            # Raw inference - no try/catch for maximum speed
            detections = runner.infer(frame)
            
            # Filter by confidence AND enabled classes
            conf_threshold = model_config.get("conf", 0.25)  # Lower default for max detections
            enabled_classes = model_config.get("enabled_classes", {})
            
            raw_count = len(detections)
            filtered_count = 0
            
            for det in detections:
                # Check confidence threshold
                if det.conf < conf_threshold:
                    continue
                
                # Check if class is enabled (if enabled_classes is provided, use it; otherwise allow all)
                if enabled_classes:
                    is_enabled = enabled_classes.get(det.cls, False)
                    if not is_enabled:
                        continue
                
                det.model_name = model_name
                all_detections.append(det)
                filtered_count += 1
            
            # Debug logging (occasionally)
            self._debug_counter += 1
            if self._debug_counter % 100 == 0:  # Every 100 frames
                enabled_list = [cls for cls, enabled in enabled_classes.items() if enabled] if enabled_classes else ["all"]
                print(f"[{model_name}] Raw: {raw_count}, After filter: {filtered_count}, Enabled classes: {enabled_list}, Conf threshold: {conf_threshold}")
        
        return all_detections
    
    def infer_frame(
        self,
        frame: np.ndarray,
        enabled_models: List[Dict]
    ) -> List[Detection]:
        """Run inference on frame with class filtering (full mode)."""
        all_detections = []
        
        # Only process models that are both enabled AND loaded
        enabled_model_names = {m["name"] for m in enabled_models}
        
        for model_config in enabled_models:
            model_name = model_config["name"]
            
            # Double-check: only run if model is loaded
            if model_name not in self.runners:
                continue
            
            # Ensure model is actually enabled (safety check)
            if model_name not in enabled_model_names:
                continue
            
            runner = self.runners[model_name]
            conf_threshold = model_config.get("conf", 0.35)
            enabled_classes = model_config.get("enabled_classes", {})
            
            # Run inference
            try:
                detections = runner.infer(frame)
            except Exception as e:
                print(f"Error running inference for {model_name}: {e}")
                continue
            
            # Debug: log detection counts
            raw_count = len(detections)
            filtered_count = 0
            
            # Filter by confidence and enabled classes
            for det in detections:
                if det.conf < conf_threshold:
                    continue
                
                # Check if class is enabled
                # If enabled_classes is explicitly provided (even if empty), only allow explicitly True classes
                # If enabled_classes is empty/None, default to True (backward compatibility)
                if enabled_classes:
                    is_enabled = enabled_classes.get(det.cls, False)  # Default to False if class not in dict
                else:
                    is_enabled = True  # Backward compatibility: if no enabled_classes provided, allow all
                
                if not is_enabled:
                    continue
                
                # Add model name to detection
                det.model_name = model_name
                all_detections.append(det)
                filtered_count += 1
            
            # Debug logging (only log occasionally to avoid spam)
            self._debug_counter += 1
            if self._debug_counter % 30 == 0:  # Log every 30 frames
                enabled_list = [cls for cls, enabled in enabled_classes.items() if enabled] if enabled_classes else ["all"]
                print(f"[{model_name}] Raw detections: {raw_count}, After filtering: {filtered_count}, Enabled classes: {enabled_list}")
        
        return all_detections

