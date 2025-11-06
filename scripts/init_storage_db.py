#!/usr/bin/env python3
"""
Initialize storage directories and database.
Run this script to ensure all storage directories exist and database is initialized.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def init_storage_directories():
    """Create all storage directories."""
    storage_root = project_root / "storage"
    
    directories = [
        storage_root / "videos",
        storage_root / "snaps",
        storage_root / "clips",
        storage_root / "db",
    ]
    
    print("Creating storage directories...")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # Create models directory if it doesn't exist
    models_dir = project_root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {models_dir}")
    
    return storage_root

def init_database():
    """Initialize database schema."""
    try:
        # Import after ensuring we're in the right directory
        from backend.app.deps import init_db
        from backend.app.config import settings
        
        print("\nInitializing database...")
        init_db()
        print(f"  ✓ Database initialized at: {settings.db_url}")
        return True
    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        print("  Note: Database will be created automatically when backend starts")
        return False

def main():
    """Main initialization function."""
    print("=" * 50)
    print("Storage and Database Initialization")
    print("=" * 50)
    print()
    
    # Initialize storage
    storage_root = init_storage_directories()
    
    # Initialize database
    db_initialized = init_database()
    
    print()
    print("=" * 50)
    print("Initialization Complete!")
    print("=" * 50)
    print()
    print("Storage locations:")
    print(f"  Videos: {storage_root / 'videos'}")
    print(f"  Snapshots: {storage_root / 'snaps'}")
    print(f"  Clips: {storage_root / 'clips'}")
    print(f"  Database: {storage_root / 'db'}")
    print(f"  Models: {project_root / 'models'}")
    print()
    
    if not db_initialized:
        print("Note: Database will be created automatically when you start the backend.")
        print("      Run: cd backend && source .venv/bin/activate && uvicorn app.main:app")
    else:
        print("Database is ready!")
    print()

if __name__ == "__main__":
    main()

