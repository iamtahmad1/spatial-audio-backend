# app/services/ws_auth.py

from fastapi import WebSocket, status
from app.db.crud import get_user_by_username
from app.services.jwt import decode_token
from sqlalchemy.orm import Session

async def get_user_from_ws(websocket: WebSocket, db: Session):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return None

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None

    user = get_user_by_username(db, payload["sub"])
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return None

    return user
