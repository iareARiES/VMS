# Models Directory

Place your ONNX model files here:

- `best.onnx` - Face detection (WIDER FACE)
- `w600k_mbf.onnx` - Face recognition embeddings
- `yolo11npRETRAINED.onnx` - COCO general detection (all 80 classes)
- `Fire_Event_best.onnx` - Fire/smoke detection

The detection service will auto-register these models on startup.

## Supported Classes (YOLO COCO)

The `yolo11npRETRAINED.onnx` model supports all 80 COCO classes:

**People & Animals:**
- person, bicycle, motorcycle, car, bus, truck
- bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

**Vehicles:**
- airplane, train, boat

**Electronics:**
- cell phone, laptop, mouse, remote, keyboard, tv

**Bags & Luggage:**
- backpack, handbag, suitcase, tie

**Other Security-Relevant:**
- knife, scissors, bottle, cup, etc.

All classes can be toggled ON/OFF individually in the Models page of the dashboard.

