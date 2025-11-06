#!/usr/bin/env python3
"""
Enable default models in the database.
Run this after starting the backend to enable models for detection.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

def enable_default_models():
    """Enable default models in database."""
    try:
        from app.db.repo import ModelRepo
        from app.deps import SessionLocal
        
        db = SessionLocal()
        try:
            # Get all models
            all_models = ModelRepo.list(db)
            
            if not all_models:
                print("No models found in database.")
                print("Make sure the backend has started and synced models from detection service.")
                return False
            
            print(f"Found {len(all_models)} models in database:")
            for model in all_models:
                print(f"  - {model.name} (type: {model.type}, enabled: {model.enabled})")
            
            # Enable best.onnx (face detection) by default
            enabled_count = 0
            for model in all_models:
                if model.name == "best.onnx" and not model.enabled:
                    ModelRepo.update(db, model.name, {"enabled": True})
                    print(f"\nEnabled: {model.name}")
                    enabled_count += 1
                elif not any(m.enabled for m in all_models):
                    # If no models are enabled, enable the first one
                    ModelRepo.update(db, model.name, {"enabled": True})
                    print(f"\nEnabled: {model.name} (first available)")
                    enabled_count += 1
                    break
            
            if enabled_count == 0:
                # Check if any are already enabled
                enabled_models = [m for m in all_models if m.enabled]
                if enabled_models:
                    print(f"\nModels already enabled: {', '.join(m.name for m in enabled_models)}")
                else:
                    print("\nNo models were enabled. Please enable at least one model in the UI.")
            
            db.commit()
            return enabled_count > 0
            
        finally:
            db.close()
    except Exception as e:
        print(f"Error enabling models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Enable Models in Database")
    print("=" * 50)
    print()
    
    success = enable_default_models()
    
    print()
    print("=" * 50)
    if success:
        print("Success! Models enabled.")
        print("You can now start detection.")
    else:
        print("Note: Make sure the backend is running first.")
        print("The backend will sync models from the detection service on startup.")
    print("=" * 50)

