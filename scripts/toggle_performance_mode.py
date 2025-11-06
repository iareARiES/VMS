#!/usr/bin/env python3
"""Toggle between ultra performance mode and normal mode."""

import sys
from pathlib import Path

def toggle_performance_mode():
    """Toggle raw_inference_mode in config.py"""
    
    # Get config file path
    config_path = Path(__file__).parent.parent / "detection-service" / "detectsvc" / "config.py"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return
    
    # Read current config
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Check current mode
    if "raw_inference_mode: bool = True" in content:
        # Switch to normal mode
        new_content = content.replace(
            "raw_inference_mode: bool = True  # Skip tracking, zones, WebSocket for max speed",
            "raw_inference_mode: bool = False  # Enable full processing (tracking, zones, WebSocket)"
        )
        mode_name = "NORMAL MODE"
        features = "✅ Object tracking\n✅ Zone detection\n✅ WebSocket updates\n✅ Full UI functionality"
        performance = "Moderate FPS with full features"
        
    elif "raw_inference_mode: bool = False" in content:
        # Switch to ultra performance mode
        new_content = content.replace(
            "raw_inference_mode: bool = False  # Enable full processing (tracking, zones, WebSocket)",
            "raw_inference_mode: bool = True  # Skip tracking, zones, WebSocket for max speed"
        )
        mode_name = "ULTRA PERFORMANCE MODE"
        features = "🚀 Raw inference only\n🚀 Maximum CPU utilization\n🚀 Minimal overhead\n🚀 Native script speed"
        performance = "80-120+ FPS raw inference"
        
    else:
        print("❌ Could not detect current performance mode in config")
        return
    
    # Write updated config
    with open(config_path, 'w') as f:
        f.write(new_content)
    
    print(f"🔄 Switched to: {mode_name}")
    print(f"📊 Expected performance: {performance}")
    print(f"🎯 Features:")
    print(features)
    print()
    print("⚠️  Restart the detection service to apply changes:")
    print("   Ctrl+C in the detection service terminal, then restart")

if __name__ == "__main__":
    toggle_performance_mode()
