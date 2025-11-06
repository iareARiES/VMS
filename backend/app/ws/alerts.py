"""Alerts WebSocket endpoint."""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
from app.ws.live import ConnectionManager


alert_manager = ConnectionManager()


async def websocket_alerts(websocket: WebSocket):
    """Alerts WebSocket."""
    await alert_manager.connect(websocket)
    try:
        while True:
            # Placeholder: relay alerts from detection service
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        alert_manager.disconnect(websocket)

