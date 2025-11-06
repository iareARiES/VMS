"""Live WebSocket endpoint."""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
import json
import asyncio
import websockets
from app.config import settings


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.detection_ws = None
        self.relay_task = None
    
    async def connect(self, websocket: WebSocket):
        """Connect client."""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Start relay task if this is the first connection
        if len(self.active_connections) == 1 and not self.relay_task:
            self.relay_task = asyncio.create_task(self._relay_detections())
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect client."""
        self.active_connections.discard(websocket)
        
        # Stop relay if no connections
        if len(self.active_connections) == 0 and self.relay_task:
            self.relay_task.cancel()
            self.relay_task = None
            if self.detection_ws:
                asyncio.create_task(self.detection_ws.close())
                self.detection_ws = None
    
    async def _relay_detections(self):
        """Relay detections from detection service to clients."""
        detect_url = settings.detection_service_url.replace("http://", "ws://").replace("https://", "wss://")
        
        while len(self.active_connections) > 0:
            try:
                async with websockets.connect(
                    f"{detect_url}/ws/detections",
                    ping_interval=20,
                    ping_timeout=10
                ) as ws:
                    self.detection_ws = ws
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            await self.broadcast(data)
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"Error broadcasting message: {e}")
            except websockets.exceptions.ConnectionClosed:
                # Connection closed, wait and retry
                await asyncio.sleep(2)
            except Exception as e:
                print(f"WebSocket relay error: {e}, retrying in 2 seconds...")
                await asyncio.sleep(2)
            finally:
                self.detection_ws = None
    
    async def broadcast(self, message: dict):
        """Broadcast to all connections."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


async def websocket_live(websocket: WebSocket):
    """Live detection stream WebSocket."""
    try:
        await manager.connect(websocket)
        # Keep connection alive - wait for disconnect
        # The relay task will send messages to this connection
        # We don't need to receive anything from the client
        try:
            ping_interval = 30  # Send ping every 30 seconds
            last_ping = asyncio.get_event_loop().time()
            
            while True:
                await asyncio.sleep(1)
                
                # Send ping periodically to keep connection alive
                current_time = asyncio.get_event_loop().time()
                if current_time - last_ping >= ping_interval:
                    try:
                        await websocket.send_json({"type": "ping", "ts": current_time})
                        last_ping = current_time
                    except Exception:
                        # Connection closed
                        break
        except Exception:
            pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

