#!/usr/bin/env python3
"""Test raw inference speed of YOLO models."""

import time
import numpy as np
import cv2
from pathlib import Path
import sys
import os

# Add the detection service to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "detection-service"))

try:
    from detectsvc.accel.onnx_cpu import ONNXCPURunner
    from detectsvc.registry import registry
except ImportError as e:
    print(f"❌ Could not import detection modules: {e}")
    print("Make sure you're running from the intrusion-suite directory")
    sys.exit(1)

def create_test_frame(width=640, height=640):
    """Create a test frame for inference."""
    # Create a synthetic test image (random noise + some shapes)
    frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    # Add some shapes to make it more realistic
    cv2.rectangle(frame, (100, 100), (200, 200), (255, 0, 0), -1)
    cv2.circle(frame, (400, 400), 50, (0, 255, 0), -1)
    cv2.rectangle(frame, (300, 100), (500, 300), (0, 0, 255), 2)
    
    return frame

def benchmark_model(model_path, model_name, num_frames=100):
    """Benchmark a single model."""
    print(f"\n🧪 Testing {model_name}")
    print(f"📁 Model: {model_path}")
    
    if not Path(model_path).exists():
        print(f"❌ Model file not found: {model_path}")
        return None
    
    try:
        # Load model
        print("⏳ Loading model...")
        runner = ONNXCPURunner()
        runner.load(Path(model_path))
        
        # Set dummy class names
        runner.class_names = ["class_0", "class_1", "class_2"]
        
        # Create test frame
        test_frame = create_test_frame()
        print(f"📐 Test frame: {test_frame.shape}")
        
        # Warmup (first inference is usually slower)
        print("🔥 Warming up...")
        for _ in range(5):
            runner.infer(test_frame)
        
        # Benchmark
        print(f"⚡ Running {num_frames} inferences...")
        start_time = time.time()
        
        for i in range(num_frames):
            detections = runner.infer(test_frame)
            if i == 0:
                print(f"🎯 First inference: {len(detections)} detections")
        
        end_time = time.time()
        elapsed = end_time - start_time
        fps = num_frames / elapsed
        
        print(f"✅ Results:")
        print(f"   🚀 FPS: {fps:.1f}")
        print(f"   ⏱️  Total time: {elapsed:.2f}s")
        print(f"   📊 Avg time per frame: {(elapsed/num_frames)*1000:.1f}ms")
        
        return fps
        
    except Exception as e:
        print(f"❌ Error benchmarking {model_name}: {e}")
        return None

def main():
    """Run inference speed test."""
    print("🏃‍♂️ YOLO Inference Speed Test")
    print("="*50)
    
    # Find model directory
    models_dir = Path(__file__).parent.parent / "models"
    if not models_dir.exists():
        print(f"❌ Models directory not found: {models_dir}")
        return
    
    # Find available models
    model_files = list(models_dir.glob("*.onnx"))
    if not model_files:
        print(f"❌ No ONNX models found in {models_dir}")
        return
    
    print(f"📂 Found {len(model_files)} models in {models_dir}")
    
    results = {}
    
    # Test each model
    for model_file in model_files:
        model_name = model_file.stem
        fps = benchmark_model(str(model_file), model_name)
        if fps:
            results[model_name] = fps
    
    # Summary
    print("\n" + "="*50)
    print("📊 PERFORMANCE SUMMARY")
    print("="*50)
    
    if results:
        for model_name, fps in sorted(results.items(), key=lambda x: x[1], reverse=True):
            print(f"🥇 {model_name:<20} {fps:>8.1f} FPS")
        
        avg_fps = sum(results.values()) / len(results)
        best_fps = max(results.values())
        
        print(f"\n📈 Average FPS: {avg_fps:.1f}")
        print(f"🚀 Best FPS: {best_fps:.1f}")
        
        if best_fps > 60:
            print("🎉 EXCELLENT! Your system achieves native-script performance!")
        elif best_fps > 30:
            print("✅ GOOD! Solid performance for real-time detection.")
        else:
            print("⚠️  Consider optimizing or using a smaller model.")
    else:
        print("❌ No successful benchmarks")
    
    print("\n💡 Tips:")
    print("   - Higher FPS = better performance")
    print("   - Test with real camera feed might be different")
    print("   - GPU acceleration would be even faster")

if __name__ == "__main__":
    main()
