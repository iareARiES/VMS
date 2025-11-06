# WebSocket Topics

## Backend WebSocket Endpoints

### `/ws/live`
Real-time detection frame stream (relayed from detection-service).

**Message Format:**
```json
{
  "ts": 1730874321.23,
  "frame_idx": 1205,
  "boxes": [
    {
      "id": 42,
      "cls": "person",
      "conf": 0.87,
      "xyxy": [100, 200, 300, 400],
      "zone": "Zone1",
      "event": "intrusion_start|ongoing|end"
    }
  ],
  "fps": 11.8
}
```

### `/ws/alerts`
High-level event notifications (debounced).

**Message Format:**
```json
{
  "event_id": "e_abc",
  "type": "intrusion",
  "zone": "Restricted",
  "cls": "person",
  "track_id": 42,
  "t_start": 1730874321.2,
  "snapshot": "/snaps/e_abc.jpg"
}
```

### `/ws/system`
System telemetry (CPU, RAM, FPS, temperature).

**Message Format:**
```json
{
  "cpu_percent": 45.2,
  "ram_percent": 62.1,
  "temp_c": 61.0,
  "fps": 11.8,
  "queue_depth": 2
}
```

## Detection Service WebSocket Endpoints

### `/ws/detections`
Raw detection stream (minimal JSON frames).

### `/ws/alerts`
Event notifications from detection engine.

