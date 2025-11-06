# YOLO Detection Model Code Structure

## 📁 Directory Structure

```
intrusion-suite/detection-service/
├── detectsvc/
│   ├── main.py                    # 🚀 Main FastAPI app & detection loop
│   ├── config.py                  # ⚙️ Configuration settings
│   ├── registry.py                # 📋 Model registry (manages model metadata)
│   │
│   ├── accel/                     # 🎯 ACCELERATOR MODULE (YOLO Inference)
│   │   ├── base.py                # Base classes (Detection, AcceleratorRunner)
│   │   └── onnx_cpu.py            # ⭐ YOLO ONNX MODEL RUNNER (Main YOLO code!)
│   │
│   └── pipeline/                  # 🔄 Processing Pipeline
│       ├── capture.py             # Video frame capture
│       ├── infer_onnx.py          # Inference pipeline wrapper
│       ├── tracker.py             # Object tracking
│       └── zones.py               # Zone checking
```

---

## 🎯 **Main YOLO Code Location**

### **Primary File: `detectsvc/accel/onnx_cpu.py`**

This is where the **YOLO model inference happens**. It contains:

1. **Model Loading** (`load()` method):
   - Loads ONNX model using ONNX Runtime
   - Parses input shape (e.g., 640x640 for YOLO)
   - Sets up inference session

2. **Image Preprocessing** (`infer()` method):
   - Resizes image to model input size (640x640)
   - Converts to tensor format (normalized 0-1)
   - Prepares input for ONNX Runtime

3. **YOLO Inference** (`infer()` method):
   - Runs model: `session.run()` → Gets raw YOLO output
   - Raw output format: `[num_detections, 6]` or `[num_detections, 85]`

4. **Postprocessing** (`_postprocess()` method):
   - Parses YOLO output format
   - Converts coordinates from model space to original image space
   - Extracts: bounding boxes (x1, y1, x2, y2), confidence, class
   - Creates `Detection` objects

---

## 🔄 **Execution Flow**

```
1. main.py (detection_loop)
   ↓
2. capture.read() → Get frame from camera
   ↓
3. inference_pipeline.infer_frame() → infer_onnx.py
   ↓
4. runner.infer() → onnx_cpu.py (YOLO inference)
   ↓
5. _postprocess() → Convert YOLO output to Detection objects
   ↓
6. tracker.update() → Track objects across frames
   ↓
7. broadcast_detections() → Send to frontend via WebSocket
```

---

## 📝 **Key Code Sections**

### **1. Model Loading** (`onnx_cpu.py` lines 19-89)
```python
def load(self, model_path: Path):
    # Load ONNX model
    self.session = ort.InferenceSession(str(model_path), providers=['CPUExecutionProvider'])
    # Parse input shape (640x640 for YOLO)
    # Set up input/output names
```

### **2. YOLO Inference** (`onnx_cpu.py` lines 91-117)
```python
def infer(self, image: np.ndarray) -> List[Detection]:
    # Preprocess: resize to 640x640, normalize
    resized = cv2.resize(image, (w, h))
    input_tensor = resized.transpose(2, 0, 1).astype(np.float32) / 255.0
    
    # Run YOLO model
    outputs = self.session.run(self.output_names, {self.input_name: input_tensor})
    
    # Postprocess YOLO output
    detections = self._postprocess(outputs[0], image.shape[:2])
    return detections
```

### **3. YOLO Postprocessing** (`onnx_cpu.py` lines 119-220)
```python
def _postprocess(self, output: np.ndarray, orig_shape: Tuple[int, int]):
    # Parse YOLO output format:
    # Format 1: [num_detections, 6] → (x1, y1, x2, y2, conf, cls)
    # Format 2: [num_detections, 85] → (x, y, w, h, conf, class_probs...)
    
    # Scale bounding boxes from model size (640x640) to original image size
    # Extract class names, confidence scores
    # Create Detection objects
```

---

## 🎨 **YOLO Output Formats Supported**

### **Format 1: YOLO v11/v8** (lines 142-169)
```python
# Output: [num_detections, 6]
# Columns: [x1, y1, x2, y2, confidence, class_index]
```

### **Format 2: YOLO v5/v8 (older)** (lines 170-220)
```python
# Output: [num_detections, 85]
# Columns: [x_center, y_center, width, height, objectness, class_probs...]
# Converts center+size to x1,y1,x2,y2 format
```

---

## 🔗 **How It All Connects**

1. **main.py** → Starts detection loop, manages state
2. **infer_onnx.py** → Wraps multiple models, applies filtering
3. **onnx_cpu.py** → **THE YOLO CODE** - actual model inference
4. **tracker.py** → Tracks objects across frames
5. **zones.py** → Checks if detections are in zones

---

## 📍 **Quick Reference**

| Component | File | Purpose |
|-----------|------|---------|
| **YOLO Model Loading** | `accel/onnx_cpu.py:19-89` | Load ONNX model |
| **YOLO Inference** | `accel/onnx_cpu.py:91-117` | Run model on frame |
| **YOLO Postprocessing** | `accel/onnx_cpu.py:119-220` | Parse YOLO output |
| **Detection Loop** | `main.py:221-310` | Main processing loop |
| **Model Management** | `pipeline/infer_onnx.py` | Manage multiple models |

---

## 💡 **To Modify YOLO Behavior**

- **Change preprocessing**: Edit `onnx_cpu.py:107-110`
- **Change postprocessing**: Edit `onnx_cpu.py:119-220`
- **Change input size**: Model uses its native size (usually 640x640)
- **Add NMS**: Currently no NMS - model output is used as-is
- **Change confidence filtering**: Edit `infer_onnx.py:78` (user configurable)

---

## 🎯 **Summary**

**The main YOLO code is in:**
- **`intrusion-suite/detection-service/detectsvc/accel/onnx_cpu.py`**

This file handles:
- ✅ Loading YOLO ONNX models
- ✅ Preprocessing images for YOLO
- ✅ Running YOLO inference
- ✅ Postprocessing YOLO output to bounding boxes

The rest of the codebase manages the pipeline, tracking, and UI integration.

