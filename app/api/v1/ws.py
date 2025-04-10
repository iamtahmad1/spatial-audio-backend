from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from typing import Dict, Set
from app.services.jwt import verify_token
from app.db.crud import get_user_by_username
from app.db.deps import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Active room connections: { room_id: set of WebSocket connections }
active_connections: Dict[str, Set[WebSocket]] = {}

async def get_user_from_token(token: str, db: Session) -> str:
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise Exception("Invalid token")
    except Exception:
        return None

    user = get_user_by_username(db, username)
    return user
