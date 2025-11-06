# Directory Structure Guide

This document explains the project structure and which parts to edit for different purposes.

## Project Root

```
intrusion-suite/
├── backend/              # FastAPI backend service
├── detection-service/    # YOLO/ONNX detection service
├── frontend/            # React frontend application
├── models/              # YOLO ONNX model files
├── storage/             # Data storage (videos, snaps, clips, database)
├── scripts/             # Utility scripts
├── docker-compose.yml   # Docker orchestration
├── requirements.txt     # Python dependencies for RPI
└── .env                 # Environment configuration (create this)
```

## Backend (`backend/`)

### Purpose
FastAPI backend that handles:
- REST API endpoints
- WebSocket connections
- Database operations
- File storage management
- Communication with detection service

### Key Files to Edit

**`backend/app/config.py`**
- **Edit for:** Changing server ports, database URLs, storage paths
- **What it does:** Configuration settings (ports, database, detection service URL)
- **Example changes:**
  ```python
  backend_port: int = 8000  # Change port
  db_url: str = "sqlite:///storage/db/events.sqlite"  # Change database
  ```

**`backend/app/main.py`**
- **Edit for:** Adding new API routes, middleware, startup/shutdown logic
- **What it does:** Main FastAPI application entry point
- **Example changes:** Add new routers, configure CORS, add middleware

**`backend/app/routers/`**
- **Edit for:** Adding new API endpoints
- **Files:**
  - `events.py` - Event management endpoints
  - `models.py` - Model management endpoints
  - `zones.py` - Zone management endpoints
  - `query.py` - Query/search endpoints
  - `upload.py` - File upload endpoints
  - `sos.py` - SOS/alert endpoints
  - `system.py` - System information endpoints

**`backend/app/db/models.py`**
- **Edit for:** Changing database schema, adding new tables/fields
- **What it does:** SQLAlchemy database models
- **Example changes:** Add new columns, create new tables

**`backend/app/db/repo.py`**
- **Edit for:** Changing database queries, adding new database operations
- **What it does:** Database repository pattern implementation

**`backend/app/services/`**
- **Edit for:** Business logic, external service integration
- **Files:**
  - `detection_client.py` - Client for detection service communication
  - `storage.py` - File storage operations

**`backend/app/ws/`**
- **Edit for:** WebSocket message handling
- **Files:**
  - `alerts.py` - Alert WebSocket handling
  - `live.py` - Live detection feed WebSocket handling

## Detection Service (`detection-service/`)

### Purpose
YOLO/ONNX inference service that handles:
- Video frame capture
- Object detection inference
- Zone detection
- Object tracking
- Event generation

### Key Files to Edit

**`detection-service/detectsvc/config.py`**
- **Edit for:** Changing detection settings, FPS, device selection
- **What it does:** Detection service configuration
- **Example changes:**
  ```python
  target_fps: int = 12  # Change target FPS
  infer_device: str = "onnx_cpu"  # Change inference device
  ```

**`detection-service/detectsvc/main.py`**
- **Edit for:** Adding new API endpoints, changing service behavior
- **What it does:** Main detection service FastAPI application
- **Example changes:** Add new detection endpoints, modify startup logic

**`detection-service/detectsvc/pipeline/capture.py`**
- **Edit for:** Changing video source, camera settings, frame capture logic
- **What it does:** Video frame capture from camera/files
- **Example changes:** Change camera index, modify resolution, add filters

**`detection-service/detectsvc/pipeline/infer_onnx.py`**
- **Edit for:** Changing inference logic, model loading, post-processing
- **What it does:** ONNX model inference and result processing
- **Example changes:** Modify confidence thresholds, change NMS settings

**`detection-service/detectsvc/pipeline/zones.py`**
- **Edit for:** Changing zone detection logic, zone validation
- **What it does:** Zone-based detection filtering

**`detection-service/detectsvc/pipeline/tracker.py`**
- **Edit for:** Changing object tracking algorithm, tracking parameters
- **What it does:** Object tracking across frames

**`detection-service/detectsvc/registry.py`**
- **Edit for:** Changing model registration, model discovery
- **What it does:** Model file discovery and registration

**`detection-service/detectsvc/accel/onnx_cpu.py`**
- **Edit for:** Optimizing CPU inference, changing ONNX runtime settings
- **What it does:** CPU-based ONNX inference implementation

## Frontend (`frontend/`)

### Purpose
React application providing:
- User interface
- Zone drawing and editing
- Model management
- Event viewing
- Live detection feed
- Settings and configuration

### Key Files to Edit

**`frontend/src/pages/`**
- **Edit for:** Adding new pages, modifying page layouts
- **Files:**
  - `Dashboard.tsx` - Main dashboard page
  - `Events.tsx` - Events list page
  - `Zones.tsx` - Zone management page
  - `Models.tsx` - Model management page
  - `Settings.tsx` - Settings page
  - `Health.tsx` - System health page

**`frontend/src/components/`**
- **Edit for:** Adding new UI components, modifying existing components
- **Key components:**
  - `LiveView.tsx` - Live video feed display
  - `ZoneEditor.tsx` - Zone drawing/editing interface
  - `ModelSelector.tsx` - Model selection dropdown
  - `RightSidebar.tsx` - Right sidebar with detection info
  - `LeftSidebar.tsx` - Navigation sidebar
  - `TopBar.tsx` - Top navigation bar
  - `BottomBar.tsx` - Bottom status bar
  - `Chatbot.tsx` - Chatbot interface
  - `SOSButton.tsx` - SOS button component

**`frontend/src/api/`**
- **Edit for:** Changing API calls, WebSocket connections
- **Files:**
  - `backend.ts` - REST API client
  - `sockets.ts` - WebSocket client

**`frontend/vite.config.ts`**
- **Edit for:** Changing build settings, proxy configuration
- **What it does:** Vite build configuration

**`frontend/package.json`**
- **Edit for:** Adding new npm dependencies
- **What it does:** Node.js dependencies and scripts

## Configuration Files

### `.env` (Create in project root)
- **Edit for:** Environment-specific settings
- **What it does:** Overrides default configuration
- **Example:**
  ```
  DB_URL=sqlite:///storage/db/events.sqlite
  BACKEND_PORT=8000
  DETECTION_SERVICE_URL=http://localhost:8010
  TARGET_FPS=12
  ```

### `docker-compose.yml`
- **Edit for:** Docker container configuration, port mappings, volumes
- **What it does:** Docker orchestration configuration

## Storage (`storage/`)

### Structure
```
storage/
├── db/
│   └── events.sqlite    # SQLite database (auto-created)
├── videos/              # Full video recordings
├── snaps/               # Snapshot images
└── clips/               # Event video clips
```

- **Edit for:** Manual database operations, file management
- **Note:** These directories are auto-created. Don't edit database directly.

## Models (`models/`)

### Purpose
Stores YOLO ONNX model files

- **Edit for:** Adding/removing model files
- **Supported models:**
  - `best.onnx` - Face detection
  - `w600k_mbf.onnx` - Face recognition
  - `yolo11npRETRAINED.onnx` - General object detection
  - `Fire_Event_best.onnx` - Fire/smoke detection

## Scripts (`scripts/`)

### Utility Scripts

**`scripts/init_storage_db.py`**
- **Edit for:** Changing storage initialization logic
- **What it does:** Creates storage directories and initializes database

**`scripts/enable_models.py`**
- **Edit for:** Changing model enabling logic
- **What it does:** Enables/disables models in the system

**`scripts/test_inference_speed.py`**
- **Edit for:** Changing performance test parameters
- **What it does:** Tests inference speed

**`scripts/toggle_performance_mode.py`**
- **Edit for:** Changing performance mode settings
- **What it does:** Toggles performance optimization modes

## Common Editing Tasks

### Adding a New API Endpoint

1. **Backend:** Add route in `backend/app/routers/` or create new router file
2. **Frontend:** Add API call in `frontend/src/api/backend.ts`
3. **Frontend:** Add UI component/page if needed

### Changing Detection Behavior

1. **Detection Service:** Edit `detection-service/detectsvc/pipeline/infer_onnx.py`
2. **Configuration:** Update `detection-service/detectsvc/config.py`
3. **Backend:** Update detection client if API changes needed

### Adding a New Model Type

1. **Models:** Place ONNX file in `models/` directory
2. **Detection Service:** Model auto-discovered via `detection-service/detectsvc/registry.py`
3. **Frontend:** Model appears in `ModelSelector` component automatically

### Changing Database Schema

1. **Backend:** Edit `backend/app/db/models.py`
2. **Backend:** Update `backend/app/db/repo.py` if query logic changes
3. **Migration:** Delete old database file to recreate schema (or implement migrations)

### Changing UI Layout

1. **Frontend:** Edit component files in `frontend/src/components/`
2. **Frontend:** Edit page files in `frontend/src/pages/`
3. **Frontend:** Modify CSS files (`.css` files next to components)

### Changing Ports

1. **Backend:** Edit `backend/app/config.py` or `.env` file
2. **Detection Service:** Edit `detection-service/detectsvc/config.py` or `.env` file
3. **Frontend:** Edit `frontend/vite.config.ts` for dev server port
4. **Docker:** Edit `docker-compose.yml` for container ports

## Best Practices

1. **Don't edit:** Files in `__pycache__/`, `node_modules/`, `.egg-info/` (auto-generated)
2. **Do edit:** Configuration files, source code, documentation
3. **Test changes:** Always test in development mode before production
4. **Backup:** Backup database and important files before major changes
5. **Version control:** Commit changes frequently with descriptive messages

## Architecture Rules

- **No cross-imports:** Backend, detection-service, and frontend are isolated
- **Shared contracts:** Use API contracts, not shared code
- **Backend:** Never imports ONNX or loads models directly
- **Detection Service:** Never touches database directly
- **Frontend:** Never writes files directly to storage

