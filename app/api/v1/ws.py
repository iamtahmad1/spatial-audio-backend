# app/api/v1/ws.py

from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.ws_auth import get_user_from_ws 
from app.services.room_connection_manager import RoomConnectionManager
from app.db.crud import is_user_in_room
from app.db.crud import save_message
from app.db.crud import get_recent_messages
from app.services.chat_service import get_recent_messages_for_ws
import json

router = APIRouter()
manager = RoomConnectionManager()

@router.websocket("/rooms/{room_id}")
async def room_ws_endpoint(websocket: WebSocket, room_id: str, db: Session = Depends(get_db)):
    user = await get_user_from_ws(websocket, db)
    if not user:
        return  # Already closed inside auth

    if not is_user_in_room(db, user.id, room_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Access denied: Not in room")
        return

    await websocket.accept()
    await manager.connect(room_id, websocket, user.username)

    recent_messages = get_recent_messages_for_ws(db, room_id)
    await websocket.send_text(json.dumps({
    "type": "history",
    "messages": [
        {
            "id": str(m["id"]),
            "user_id": str(m["user_id"]),
            "message": m["content"],
            "timestamp": m["timestamp"]
        }
        for m in recent_messages
    ]
}))


    try:
        while True:
            data = await websocket.receive_text()
            if not data.strip():
                continue  # Ignore empty messages

            try:
                parsed = json.loads(data)
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON decode failed: {e} | data: {data}", flush=True)
                continue  # Skip this message

            if parsed.get("type") == "chat":
                message = parsed.get("message", "")

                await manager.broadcast(room_id, json.dumps({
                    "type": "chat",
                    "sender": user.username,
                    "message": message
                }))
                save_message(db, room_id, user.id, message)

    except WebSocketDisconnect:
        await manager.disconnect(room_id, websocket)
