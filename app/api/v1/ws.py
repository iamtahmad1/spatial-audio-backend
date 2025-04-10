# app/api/v1/ws.py

from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.ws_auth import get_user_from_ws 
from app.services.room_connection_manager import RoomConnectionManager
from app.db.crud import is_user_in_room
import json

router = APIRouter()
manager = RoomConnectionManager()

@router.websocket("/ws/rooms/{room_id}")
async def room_ws_endpoint(websocket: WebSocket, room_id: str, db: Session = Depends(get_db)):
    user = await get_user_from_ws(websocket, db)
    if not user:
        return  # Already closed inside auth

    if not is_user_in_room(db, user.id, room_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Access denied: Not in room")
        return

    await websocket.accept()
    await manager.connect(room_id, websocket)

    # Notify others in room
    await manager.broadcast(room_id, json.dumps({
        "type": "join",
        "user": user.username,
        "message": f"{user.username} joined the room"
    }))

    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)

            if parsed.get("type") == "chat":
                await manager.broadcast(room_id, json.dumps({
                    "type": "chat",
                    "sender": user.username,
                    "message": parsed.get("message", "")
                }))

    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket)
        await manager.broadcast(room_id, json.dumps({
            "type": "leave",
            "user": user.username,
            "message": f"{user.username} left the room"
        }))
