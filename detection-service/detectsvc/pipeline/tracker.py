"""Object tracking (simplified ByteTrack)."""
from typing import List, Dict, Optional
from detectsvc.accel.base import Detection
import time


class Track:
    """Track object."""
    def __init__(self, track_id: int, detection: Detection, timestamp: float):
        self.track_id = track_id
        self.detection = detection
        self.first_seen = timestamp
        self.last_seen = timestamp
        self.hits = 1
        self.age = 0
    
    def update(self, detection: Detection, timestamp: float):
        """Update track."""
        self.detection = detection
        self.last_seen = timestamp
        self.hits += 1
        self.age += 1


class SimpleTracker:
    """Simple object tracker."""
    
    def __init__(self):
        self.tracks: Dict[int, Track] = {}
        self.next_id = 1
        self.max_age = 30  # frames
    
    def update(
        self,
        detections: List[Detection],
        timestamp: float
    ) -> List[Detection]:
        """Update tracks with new detections."""
        # Simple IoU-based matching
        # In production, use ByteTrack or OCSort
        
        updated_detections = []
        
        for det in detections:
            # Find best matching track
            best_track = None
            best_iou = 0.1  # Lower IoU threshold for better tracking of fast-moving objects
            
            for track_id, track in self.tracks.items():
                iou = self._calculate_iou(det.bbox, track.detection.bbox)
                if iou > best_iou and det.cls == track.detection.cls:
                    best_iou = iou
                    best_track = track
            
            if best_track:
                best_track.update(det, timestamp)
                det.track_id = best_track.track_id
            else:
                # New track
                track_id = self.next_id
                self.next_id += 1
                track = Track(track_id, det, timestamp)
                self.tracks[track_id] = track
                det.track_id = track_id
            
            updated_detections.append(det)
        
        # Remove old tracks (based on frame age, not time)
        to_remove = []
        for track_id, track in self.tracks.items():
            # Remove tracks that haven't been seen for max_age frames
            # Simple check: if track age is too high
            if track.age > self.max_age * 2:  # Give tracks more time
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
        
        return updated_detections
    
    def _calculate_iou(self, bbox1, bbox2) -> float:
        """Calculate IoU between two bboxes."""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union

