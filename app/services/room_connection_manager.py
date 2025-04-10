from fastapi import WebSocket
from collections import defaultdict
from typing import Dict, List
import asyncio

class RoomConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def connect(self, room_id: str, websocket: WebSocket):
        async with self.lock:
            self.active_connections[room_id].append(websocket)
    
    async def disconnect(self, room_id: str, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
    
    async def broadcast(self, room_id: str, message: str):
        async with self.lock:
            for connection in self.active_connections.get(room_id, []):
                await connection.send_text(message)