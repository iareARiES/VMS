"""ONNX CPU inference runner."""
import onnxruntime as ort
import numpy as np
from pathlib import Path
from typing import List, Tuple
from detectsvc.accel.base import AcceleratorRunner, Detection


class ONNXCPURunner(AcceleratorRunner):
    """ONNX Runtime CPU runner."""
    
    def __init__(self):
        self.session = None
        self.input_name = None
        self.input_shape = None
        self.output_names = None
        self.class_names = []
    
    def load(self, model_path: Path):
        """Load ONNX model with MAXIMUM performance optimizations."""
        # Ultra-aggressive ONNX Runtime optimization for raw speed
        sess_options = ort.SessionOptions()
        sess_options.enable_cpu_mem_arena = True
        sess_options.enable_mem_pattern = True
        sess_options.enable_mem_reuse = True
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL  # Changed to parallel for max speed
        sess_options.inter_op_num_threads = 0  # Use all available threads
        sess_options.intra_op_num_threads = 0  # Use all available threads
        sess_options.log_severity_level = 3  # Disable logging for speed
        sess_options.enable_profiling = False  # Disable profiling
        
        # Ultra-optimized CPU provider settings
        providers = [('CPUExecutionProvider', {
            'arena_extend_strategy': 'kSameAsRequested',
            'enable_cpu_mem_arena': True,
            'memory_pattern_optimization': True,
            'use_arena': True,
        })]
        
        self.session = ort.InferenceSession(
            str(model_path),
            sess_options=sess_options,
            providers=providers
        )
        
        # Get input/output info
        self.input_name = self.session.get_inputs()[0].name
        input_shape = self.session.get_inputs()[0].shape
        
        def safe_int(value, default=640):
            """Safely convert value to int, handling None, strings, and negative values."""
            if value is None:
                return default
            if isinstance(value, str):
                return default
            try:
                int_val = int(value)
                return int_val if int_val > 0 else default
            except (ValueError, TypeError):
                return default
        
        # Debug: Print input shape to understand the format
        print(f"Model {model_path.name} input shape: {input_shape} (type: {type(input_shape)})")
        
        # Handle dynamic shapes (None, -1, or strings) - use default 640x640 for YOLO models
        # ONNX shapes are typically: [batch, channels, height, width] or [batch, height, width, channels]
        # Common formats:
        # - YOLO: [1, 3, 640, 640] or [batch, 3, H, W]
        # - Some models: [1, H, W, 3]
        h, w = 640, 640  # Default
        
        if len(input_shape) >= 4:
            # Format: [batch, channels, height, width] or [batch, height, width, channels]
            # Try indices 2,3 first (most common: [batch, channels, H, W])
            h1 = safe_int(input_shape[2], 0)
            w1 = safe_int(input_shape[3], 0)
            
            # Try indices 1,2 as alternative (for [batch, H, W, channels])
            h2 = safe_int(input_shape[1], 0)
            w2 = safe_int(input_shape[2], 0)
            
            # Choose the pair that makes more sense (both should be reasonable image dimensions)
            if h1 > 0 and w1 > 0 and h1 < 2000 and w1 < 2000:
                h, w = h1, w1
            elif h2 > 0 and w2 > 0 and h2 < 2000 and w2 < 2000:
                h, w = h2, w2
            else:
                # Fallback: try to find any two reasonable dimensions
                for i in range(len(input_shape)):
                    val = safe_int(input_shape[i], 0)
                    if 100 <= val <= 2000:
                        if h == 640:
                            h = val
                        elif w == 640:
                            w = val
                            break
        elif len(input_shape) >= 2:
            # Format: [height, width]
            h = safe_int(input_shape[0], 640)
            w = safe_int(input_shape[1], 640)
        
        # Ensure integers and validate
        h = int(h) if h > 0 else 640
        w = int(w) if w > 0 else 640
        self.input_shape = (h, w)
        print(f"Model {model_path.name} using input shape: {self.input_shape} (H, W)")
        
        self.output_names = [output.name for output in self.session.get_outputs()]
    
    def infer(self, image: np.ndarray) -> List[Detection]:
        """Run inference."""
        if self.session is None:
            raise RuntimeError("Model not loaded")
        
        if self.input_shape is None:
            raise RuntimeError("Input shape not set")
        
        # Preprocess - ensure w and h are integers
        h, w = self.input_shape
        w = int(w)
        h = int(h)
        
        if w <= 0 or h <= 0:
            raise ValueError(f"Invalid input shape: ({h}, {w})")
        
        # Ultra-optimized preprocessing for maximum inference speed
        # Use INTER_NEAREST for fastest resize (slight quality trade-off for speed)
        resized = cv2.resize(image, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Fastest possible normalization: pre-allocate and use in-place operations
        input_tensor = np.empty((1, 3, h, w), dtype=np.float32)
        input_tensor[0] = resized.transpose(2, 0, 1).astype(np.float32) * (1.0/255.0)
        
        # Run inference - direct call for maximum speed
        outputs = self.session.run(None, {self.input_name: input_tensor})  # None = all outputs
        
        # Postprocess (YOLO format)
        detections = self._postprocess(outputs[0], image.shape[:2])
        return detections
    
    def _postprocess(
        self,
        output: np.ndarray,
        orig_shape: Tuple[int, int]
    ) -> List[Detection]:
        """Postprocess YOLO output."""
        detections = []
        orig_h, orig_w = orig_shape
        
        # Handle different output formats
        if len(output.shape) == 3:
            output = output[0]  # Remove batch dimension if present
        
        # Calculate scaling factors from model input to original image
        model_h, model_w = self.input_shape
        if model_w <= 0 or model_h <= 0:
            print(f"Warning: Invalid model input shape {self.input_shape}, using defaults")
            model_w, model_h = 640, 640
        
        scale_x = orig_w / model_w
        scale_y = orig_h / model_h
        
        # YOLO v11/v8 output format: [num_detections, 6] (x1, y1, x2, y2, conf, cls)
        if len(output.shape) == 2 and output.shape[1] == 6:
            for det in output:
                x1, y1, x2, y2, conf, cls_idx = det
                # No hard-coded threshold - let all detections pass through
                # User's configured confidence threshold will filter later
                cls_idx_int = int(cls_idx)
                if cls_idx_int < len(self.class_names):
                    cls_name = self.class_names[cls_idx_int]
                else:
                    cls_name = f"class_{cls_idx_int}"
                
                # Scale bbox from model input size to original image size
                x1_scaled = float(x1) * scale_x
                y1_scaled = float(y1) * scale_y
                x2_scaled = float(x2) * scale_x
                y2_scaled = float(y2) * scale_y
                
                # Ensure coordinates are within image bounds
                x1_scaled = max(0, min(x1_scaled, orig_w))
                y1_scaled = max(0, min(y1_scaled, orig_h))
                x2_scaled = max(0, min(x2_scaled, orig_w))
                y2_scaled = max(0, min(y2_scaled, orig_h))
                
                detections.append(Detection(
                    cls=cls_name,
                    conf=float(conf),
                    bbox=(x1_scaled, y1_scaled, x2_scaled, y2_scaled)
                ))
        elif len(output.shape) == 2 and output.shape[1] > 6:
            # YOLO format: [num_detections, 85] (x, y, w, h, conf, class_probs...)
            # Or [num_detections, 84] (x, y, w, h, class_probs...)
            num_classes = output.shape[1] - 5  # Subtract x, y, w, h, conf
            
            for det in output:
                x_center, y_center, w, h, conf = det[:5]
                
                # No hard-coded threshold - let all detections pass through
                # User's configured confidence threshold will filter later
                # Get class with highest probability
                class_probs = det[5:]
                cls_idx = int(np.argmax(class_probs))
                cls_conf = float(class_probs[cls_idx])
                final_conf = float(conf) * cls_conf
                
                if cls_idx < len(self.class_names):
                    cls_name = self.class_names[cls_idx]
                else:
                    cls_name = f"class_{cls_idx}"
                
                # Convert center+size to x1,y1,x2,y2 (coordinates are in model input space)
                x1 = x_center - w / 2
                y1 = y_center - h / 2
                x2 = x_center + w / 2
                y2 = y_center + h / 2
                
                # Scale to original image size
                model_h, model_w = self.input_shape
                if model_w <= 0 or model_h <= 0:
                    model_w, model_h = 640, 640
                
                scale_x = orig_w / model_w
                scale_y = orig_h / model_h
                
                x1_scaled = float(x1) * scale_x
                y1_scaled = float(y1) * scale_y
                x2_scaled = float(x2) * scale_x
                y2_scaled = float(y2) * scale_y
                
                # Ensure coordinates are within image bounds
                x1_scaled = max(0, min(x1_scaled, orig_w))
                y1_scaled = max(0, min(y1_scaled, orig_h))
                x2_scaled = max(0, min(x2_scaled, orig_w))
                y2_scaled = max(0, min(y2_scaled, orig_h))
                
                detections.append(Detection(
                    cls=cls_name,
                    conf=final_conf,
                    bbox=(x1_scaled, y1_scaled, x2_scaled, y2_scaled)
                ))
        
        return detections
    
    def get_input_shape(self) -> Tuple[int, int]:
        """Get input shape."""
        return self.input_shape if self.input_shape else (640, 640)


# Import cv2 for preprocessing
import cv2

