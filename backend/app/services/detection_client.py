"""Detection service HTTP client."""
import httpx
from typing import Dict, Any, Optional, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DetectionClient:
    """Client for detection service API."""
    
    def __init__(self):
        self.base_url = settings.detection_service_url
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
    
    async def start(
        self,
        source: Dict[str, str],
        models: List[Dict[str, Any]],
        zones: Optional[List[Dict[str, Any]]] = None,
        zones_version: str = "1"
    ) -> Dict[str, Any]:
        """Start detection stream."""
        try:
            response = await self.client.post(
                "/detector/start",
                json={
                    "source": source,
                    "models": models,
                    "zones": zones or [],
                    "zones_version": zones_version
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            error_detail = "Unknown error"
            try:
                error_json = e.response.json()
                error_detail = error_json.get("detail", error_json.get("error", error_text))
            except:
                error_detail = error_text or str(e)
            logger.error(f"Detection service returned error: {e.response.status_code} - {error_detail}")
            # Re-raise with more details
            raise httpx.HTTPStatusError(
                message=f"Detection service error: {error_detail}",
                request=e.request,
                response=e.response
            )
        except httpx.RequestError as e:
            logger.error(f"Request to detection service failed: {e}")
            raise
    
    async def stop(self) -> Dict[str, Any]:
        """Stop detection."""
        response = await self.client.post("/detector/stop")
        response.raise_for_status()
        return response.json()
    
    async def status(self) -> Dict[str, Any]:
        """Get detection status."""
        response = await self.client.get("/detector/status")
        response.raise_for_status()
        return response.json()
    
    async def analyze_file(
        self,
        file_path: str,
        models: List[Dict[str, Any]],
        zones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze video file."""
        response = await self.client.post(
            "/detector/analyze-file",
            json={
                "file_path": file_path,
                "models": models,
                "zones": zones
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def snapshot(self) -> Dict[str, Any]:
        """Take snapshot."""
        response = await self.client.post("/detector/snapshot")
        response.raise_for_status()
        return response.json()
    
    async def update_model_config(
        self,
        model_name: str,
        enabled: Optional[bool] = None,
        conf: Optional[float] = None,
        iou: Optional[float] = None,
        enabled_classes: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """Update model configuration in detection service."""
        # Note: Detection service updates are done via /detector/start
        # This is a placeholder for future direct model config endpoint
        return {"status": "ok"}
    
    async def close(self):
        """Close client."""
        await self.client.aclose()


# Singleton instance
detection_client = DetectionClient()

