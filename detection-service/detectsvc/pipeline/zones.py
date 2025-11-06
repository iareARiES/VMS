"""Zone detection (point-in-polygon, tripwire)."""
from typing import List, Dict, Optional, Tuple
from detectsvc.accel.base import Detection
import numpy as np


def point_in_polygon(point: Tuple[float, float], polygon: List[List[float]]) -> bool:
    """Check if point is inside polygon."""
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def bbox_center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """Get bbox center."""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


class ZoneChecker:
    """Zone intrusion checker."""
    
    def __init__(self, zones: List[Dict]):
        self.zones = zones
    
    def check_detection(self, detection: Detection) -> Optional[Dict]:
        """Check if detection is in any zone."""
        center = bbox_center(detection.bbox)
        
        for zone in self.zones:
            zone_type = zone.get("type", "polygon")
            points = zone.get("points", [])
            allowed_classes = zone.get("allowed_classes", [])
            
            if not points:
                continue
            
            # Check class filter
            if allowed_classes and detection.cls not in allowed_classes:
                continue
            
            # Check zone type
            if zone_type == "polygon":
                if point_in_polygon(center, points):
                    return {
                        "zone_id": zone.get("zone_id"),
                        "zone_name": zone.get("name"),
                        "type": "intrusion"
                    }
            elif zone_type == "tripwire":
                # Check if bbox crosses tripwire (simplified)
                if len(points) >= 2:
                    # Check if detection crosses line between first two points
                    if self._crosses_line(detection.bbox, points[0], points[1]):
                        return {
                            "zone_id": zone.get("zone_id"),
                            "zone_name": zone.get("name"),
                            "type": "tripwire"
                        }
        
        return None
    
    def _crosses_line(
        self,
        bbox: Tuple[float, float, float, float],
        p1: List[float],
        p2: List[float]
    ) -> bool:
        """Check if bbox crosses line segment."""
        # Simplified: check if bbox center is near line
        center = bbox_center(bbox)
        x, y = center
        
        x1, y1 = p1
        x2, y2 = p2
        
        # Distance from point to line segment
        A = x - x1
        B = y - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return False
        
        param = dot / len_sq
        
        if param < 0 or param > 1:
            return False
        
        xx = x1 + param * C
        yy = y1 + param * D
        
        dx = x - xx
        dy = y - yy
        dist = np.sqrt(dx * dx + dy * dy)
        
        # Threshold: within 50 pixels
        return dist < 50

