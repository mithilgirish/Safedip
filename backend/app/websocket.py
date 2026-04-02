from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, pool_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(pool_id, []).append(websocket)

    def disconnect(self, pool_id: str, websocket: WebSocket):
        if pool_id in self.active_connections:
            if websocket in self.active_connections[pool_id]:
                self.active_connections[pool_id].remove(websocket)

    async def broadcast(self, pool_id: str, data: dict):
        if pool_id in self.active_connections:
            for connection in self.active_connections[pool_id]:
                try:
                    await connection.send_json(data)
                except Exception:
                    # Connection might be closed, disconnect logic handles it generally
                    pass

manager = ConnectionManager()

async def broadcast_to_pool(pool_id: str, data: dict):
    await manager.broadcast(pool_id, data)

@router.websocket("/ws/pool/{pool_id}")
async def websocket_endpoint(websocket: WebSocket, pool_id: str):
    await manager.connect(pool_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(pool_id, websocket)
