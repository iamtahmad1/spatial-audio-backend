from fastapi import WebSocket
from collections import defaultdict
from typing import Dict, List, Set
import asyncio
import json
from datetime import datetime


class RoomConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.user_ids: Dict[str, Set[str]] = defaultdict(set)
        self.socket_to_user: Dict[WebSocket, str] = {}
        self.socket_to_room: Dict[WebSocket, str] = {}
        self.last_ping: Dict[WebSocket, datetime] = {}
        self.lock = asyncio.Lock()

    async def connect(self, room_id: str, websocket: WebSocket, user_id: str):
        async with self.lock:
            print(f"[DEBUG] Connecting user {user_id} to room {room_id}", flush=True)

            self.active_connections[room_id].append(websocket)
            self.user_ids[room_id].add(user_id)
            self.socket_to_user[websocket] = user_id
            self.socket_to_room[websocket] = room_id

            await self.broadcast(room_id, json.dumps({
                "type": "join",
                "user": user_id,
                "message": f"{user_id} joined the room"
            }))
            await self.broadcast_presence(room_id)

    async def disconnect(self, room_id: str, websocket: WebSocket):
        async with self.lock:
            user_id = self.socket_to_user.get(websocket)
            print(f"[DEBUG] Disconnecting user {user_id} from room {room_id}", flush=True)

            if websocket in self.active_connections.get(room_id, []):
                self.active_connections[room_id].remove(websocket)

            if user_id:
                self.user_ids[room_id].discard(user_id)
                self.socket_to_user.pop(websocket, None)
                self.socket_to_room.pop(websocket, None)
                self.last_ping.pop(websocket, None)

                await self.broadcast(room_id, json.dumps({
                    "type": "leave",
                    "user": user_id,
                    "message": f"{user_id} left the room"
                }))

            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                del self.user_ids[room_id]

            await self.broadcast_presence(room_id)

    async def broadcast(self, room_id: str, message: str):
        connections = self.active_connections.get(room_id)
        if not connections:
            return

        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[ERROR] Failed to send message: {e}", flush=True)

    async def broadcast_presence(self, room_id: str):
        users = list(self.user_ids[room_id])
        message = json.dumps({
            "type": "presence",
            "users": users
        })
        await self.broadcast(room_id, message)

    async def handle_heartbeat(self, websocket: WebSocket):
        async with self.lock:
            self.last_ping[websocket] = datetime.utcnow()

    async def cleanup_dead_connections(self):
        while True:
            await asyncio.sleep(5)
            async with self.lock:
                now = datetime.utcnow()
                for websocket in list(self.last_ping):
                    if (now - self.last_ping[websocket]).total_seconds() > 10:
                        room_id = self.socket_to_room.get(websocket)
                        if room_id:
                            await self.disconnect(room_id, websocket)
                            await websocket.close()
