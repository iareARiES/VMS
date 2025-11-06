# How to Add New YOLO Models or Edit YOLO Code

## 📁 **Folder Structure for YOLO Models & Code**

```
intrusion-suite/
├── models/                          # 📦 PUT YOUR .ONNX MODEL FILES HERE
│   ├── best.onnx
│   ├── yolo11npRETRAINED.onnx
│   ├── Fire_Event_best.onnx
│   └── your_new_model.onnx         # ← Add new models here
│
└── detection-service/
    └── detectsvc/
        ├── accel/
        │   └── onnx_cpu.py         # ⚙️ EDIT YOLO INFERENCE CODE HERE
        │
        └── registry.py              # 📋 EDIT MODEL REGISTRATION HERE
```

---

## 🆕 **Adding a New YOLO Model**

### **Step 1: Place Model File**
Put your `.onnx` model file in:
```
intrusion-suite/models/your_model_name.onnx
```

### **Step 2: Register the Model**
Edit: `intrusion-suite/detection-service/detectsvc/registry.py`

Find the `auto_register_models()` method (around line 148) and add your model:

```python
def auto_register_models(self):
    """Auto-register models from models directory."""
    model_files = {
        "best.onnx": "face",
        "w600k_mbf.onnx": "face",
        "yolo11npRETRAINED.onnx": "coco",
        "Fire_Event_best.onnx": "fire",
        "your_model_name.onnx": "coco",  # ← ADD YOUR MODEL HERE
    }
```

**Model Types:**
- `"coco"` - For COCO dataset models (person, car, dog, etc.)
- `"face"` - For face detection models
- `"fire"` - For fire/smoke detection models
- Or create your own type

### **Step 3: Define Class Labels**
If your model has custom classes, edit `registry.py` around line 10-40:

```python
CLASS_LABELS = {
    "coco": [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
        # ... add your custom classes here
    ],
    "your_custom_type": [
        "class1", "class2", "class3",  # Your model's classes
    ]
}
```

### **Step 4: Restart Detection Service**
The model will be automatically detected and registered on startup.

---

## ✏️ **Editing YOLO Inference Code**

### **Main YOLO Code File:**
```
intrusion-suite/detection-service/detectsvc/accel/onnx_cpu.py
```

### **What You Can Edit:**

#### **1. Model Loading** (lines 19-89)
```python
def load(self, model_path: Path):
    # Edit here to:
    # - Change ONNX Runtime providers (CPU, GPU, etc.)
    # - Modify input shape detection
    # - Add custom model initialization
```

#### **2. Image Preprocessing** (lines 91-110)
```python
def infer(self, image: np.ndarray):
    # Edit here to:
    # - Change resize method (cv2.resize, letterbox, etc.)
    # - Modify normalization (0-1, 0-255, etc.)
    # - Add custom preprocessing (histogram equalization, etc.)
    # - Change input size (640x640, 1280x1280, etc.)
```

#### **3. YOLO Postprocessing** (lines 119-220)
```python
def _postprocess(self, output: np.ndarray, orig_shape):
    # Edit here to:
    # - Change output format parsing
    # - Add NMS (Non-Maximum Suppression)
    # - Modify coordinate scaling
    # - Add custom filtering
    # - Change confidence calculation
```

---

## 🔧 **Common Edits**

### **Example 1: Add NMS (Non-Maximum Suppression)**
Edit `onnx_cpu.py` in `_postprocess()` method:

```python
import cv2

def _postprocess(self, output, orig_shape):
    # ... existing code ...
    
    # After getting all detections, add NMS:
    boxes = [det.bbox for det in detections]
    confidences = [det.conf for det in detections]
    
    # Apply NMS
    indices = cv2.dnn.NMSBoxes(
        boxes, confidences, 
        score_threshold=0.25,  # Confidence threshold
        nms_threshold=0.45     # IoU threshold for NMS
    )
    
    # Filter detections using NMS indices
    filtered_detections = [detections[i] for i in indices]
    return filtered_detections
```

### **Example 2: Change Input Size**
Edit `onnx_cpu.py` in `infer()` method:

```python
def infer(self, image: np.ndarray):
    # Change from 640x640 to 1280x1280
    h, w = 1280, 1280  # Instead of self.input_shape
    resized = cv2.resize(image, (w, h))
    # ... rest of code
```

### **Example 3: Add Letterbox Resize (Maintain Aspect Ratio)**
Edit `onnx_cpu.py`:

```python
def letterbox_resize(img, target_size):
    """Resize with letterbox (maintain aspect ratio)."""
    h, w = img.shape[:2]
    target_h, target_w = target_size
    
    scale = min(target_h / h, target_w / w)
    new_h, new_w = int(h * scale), int(w * scale)
    
    resized = cv2.resize(img, (new_w, new_h))
    
    # Add padding
    top = (target_h - new_h) // 2
    bottom = target_h - new_h - top
    left = (target_w - new_w) // 2
    right = target_w - new_w - left
    
    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, 
                                cv2.BORDER_CONSTANT, value=(114, 114, 114))
    return padded, scale, (left, top)

def infer(self, image: np.ndarray):
    # Use letterbox instead of regular resize
    resized, scale, (pad_x, pad_y) = letterbox_resize(image, (640, 640))
    # ... rest of code
```

### **Example 4: Support Different YOLO Output Format**
Edit `onnx_cpu.py` in `_postprocess()` method:

```python
def _postprocess(self, output, orig_shape):
    # Add new format handler
    if len(output.shape) == 2 and output.shape[1] == 7:
        # New format: [x1, y1, x2, y2, conf, cls, track_id]
        for det in output:
            x1, y1, x2, y2, conf, cls_idx, track_id = det
            # ... process this format
    # ... existing formats
```

---

## 📝 **Summary**

| Task | File to Edit | Location |
|------|--------------|----------|
| **Add new model file** | Place in folder | `intrusion-suite/models/` |
| **Register new model** | `registry.py` | Line ~148-156 |
| **Edit inference logic** | `onnx_cpu.py` | Lines 91-117 |
| **Edit preprocessing** | `onnx_cpu.py` | Lines 107-110 |
| **Edit postprocessing** | `onnx_cpu.py` | Lines 119-220 |
| **Change model input size** | `onnx_cpu.py` | Line 108 or 100 |
| **Add NMS** | `onnx_cpu.py` | In `_postprocess()` method |
| **Change class labels** | `registry.py` | Lines 10-40 |

---

## 🎯 **Quick Reference**

**To add a new model:**
1. Put `.onnx` file in `intrusion-suite/models/`
2. Edit `registry.py` → `auto_register_models()` → Add model name and type
3. Restart detection service

**To edit YOLO code:**
1. Edit `detection-service/detectsvc/accel/onnx_cpu.py`
2. Modify the section you need (preprocessing, inference, postprocessing)
3. Restart detection service

**Models folder:** `intrusion-suite/models/`  
**YOLO code folder:** `intrusion-suite/detection-service/detectsvc/accel/onnx_cpu.py`

