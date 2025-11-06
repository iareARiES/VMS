# Storage and Database Setup

## Storage Structure

The system uses the following storage structure:

```
intrusion-suite/
├── storage/
│   ├── videos/      # Uploaded video files for analysis
│   ├── snaps/       # Event snapshots (JPG images)
│   ├── clips/       # Video clips extracted from events
│   └── db/          # SQLite database file
│       └── events.sqlite
└── models/          # ONNX model files
    ├── best.onnx
    ├── w600k_mbf.onnx
    ├── yolo11npRETRAINED.onnx
    └── Fire_Event_best.onnx
```

## Database

### Database Type
- **SQLite** (default) - stored at `storage/db/events.sqlite`
- Can be changed to PostgreSQL by updating `DB_URL` in `.env`

### Database Schema

The database contains the following tables:

1. **events** - Detection events
   - `event_id`, `camera_id`, `model`, `type`, `zone`, `cls`, `track_id`
   - `conf`, `t_start`, `t_end`
   - `snapshot_path`, `video_ref`, `bbox_xyxy`, `metadata`

2. **zones** - Zone configurations
   - `zone_id`, `name`, `type` (polygon/tripwire)
   - `points`, `allowed_classes`, `min_size_px`, `dwell_sec`
   - `active_schedule`, `style`

3. **models** - Model configurations
   - `name`, `type`, `enabled`, `conf`, `iou`
   - `labels`, `enabled_classes`

4. **users** - User accounts (for future auth)
   - `username`, `email`, `hashed_password`, `role`

5. **sos_logs** - SOS trigger history
   - `action`, `triggered_by`, `event_id`, `timestamp`

## Initialization

### Automatic Initialization

The database and storage directories are automatically created:

1. **Storage directories**: Created by `StorageService` when backend starts
2. **Database**: Created by `init_db()` when backend starts (in `app/main.py`)

### Manual Initialization

You can manually initialize storage and database:

```bash
# Option 1: Run the Python script
cd intrusion-suite
python3 scripts/init_storage_db.py

# Option 2: Use the setup script (includes this)
bash scripts/setup_pi.sh
```

### Database Path Configuration

The database path is configured in `.env`:

```bash
DB_URL=sqlite:///storage/db/events.sqlite
```

Or use absolute path:
```bash
DB_URL=sqlite:////home/pi/intrusion-suite/storage/db/events.sqlite
```

## Storage Service

The `StorageService` class (in `backend/app/services/storage.py`) automatically:
- Creates storage directories on initialization
- Manages file paths for videos, snapshots, and clips
- Handles file uploads and deletions

## Database Access

### Using the Database

The database is accessed through SQLAlchemy ORM:

```python
from app.deps import get_db
from app.db.repo import EventRepo

# In a route handler
def my_route(db: Session = Depends(get_db)):
    events = EventRepo.list(db, cls="person", limit=10)
    return events
```

### Database Repositories

Use the repository classes for database operations:
- `EventRepo` - Event CRUD operations
- `ZoneRepo` - Zone CRUD operations
- `ModelRepo` - Model configuration operations

## Backup and Maintenance

### Backup Database

```bash
# Backup SQLite database
cp storage/db/events.sqlite storage/db/events.sqlite.backup

# Or use sqlite3
sqlite3 storage/db/events.sqlite ".backup storage/db/events.sqlite.backup"
```

### Clean Old Files

```bash
# Remove old snapshots (older than 30 days)
find storage/snaps -name "*.jpg" -mtime +30 -delete

# Remove old clips (older than 7 days)
find storage/clips -name "*.mp4" -mtime +7 -delete
```

### Database Size

Check database size:
```bash
ls -lh storage/db/events.sqlite
```

## Troubleshooting

### Database Not Created

If the database isn't created automatically:
1. Check that `storage/db/` directory exists
2. Check file permissions: `chmod 755 storage/db/`
3. Manually initialize: `python3 scripts/init_storage_db.py`

### Storage Directory Errors

If you get "directory not found" errors:
1. Ensure storage directories exist: `mkdir -p storage/{videos,snaps,clips,db}`
2. Check permissions: `chmod -R 755 storage/`
3. Verify `STORAGE_ROOT` in `.env` points to correct path

### Database Locked

If you see "database is locked" errors:
- SQLite doesn't handle concurrent writes well
- Consider switching to PostgreSQL for production
- Or ensure only one process accesses the database at a time

## Production Recommendations

For production deployment:

1. **Use PostgreSQL** instead of SQLite:
   ```bash
   DB_URL=postgresql://user:password@localhost/intrusion_db
   ```

2. **Set up regular backups**:
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup_script.sh
   ```

3. **Monitor storage usage**:
   ```bash
   du -sh storage/*
   ```

4. **Clean old files automatically**:
   - Set up cron job to remove files older than X days
   - Or implement retention policy in the application

