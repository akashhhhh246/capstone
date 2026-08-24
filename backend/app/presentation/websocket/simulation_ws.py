from typing import List, Dict, Any, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket connection manager for real-time propagation event broadcasting.
    Supports targeted room subscriptions (by simulation/campaign ID) and broadcast feeds.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.simulation_subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, simulation_id: str = "global"):
        await websocket.accept()
        self.active_connections.append(websocket)
        if simulation_id not in self.simulation_subscriptions:
            self.simulation_subscriptions[simulation_id] = set()
        self.simulation_subscriptions[simulation_id].add(websocket)
        logger.info(f"WebSocket connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, simulation_id: str = "global"):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if simulation_id in self.simulation_subscriptions and websocket in self.simulation_subscriptions[simulation_id]:
            self.simulation_subscriptions[simulation_id].remove(websocket)
        logger.info(f"WebSocket disconnected. Total active: {len(self.active_connections)}")

    async def broadcast_event(self, event_data: Dict[str, Any], simulation_id: str = "global"):
        """Broadcast event payload to subscribed WebSockets and global listeners."""
        payload_str = json.dumps(event_data)
        
        # Targets: global listeners + specific simulation subscribers
        targets: Set[WebSocket] = set()
        if "global" in self.simulation_subscriptions:
            targets.update(self.simulation_subscriptions["global"])
        if simulation_id in self.simulation_subscriptions:
            targets.update(self.simulation_subscriptions[simulation_id])

        disconnected = []
        for ws in targets:
            try:
                await ws.send_text(payload_str)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws, simulation_id)

ws_manager = ConnectionManager()
