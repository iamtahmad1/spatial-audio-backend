from app.db.crud import get_recent_messages as db_get_recent_messages
from sqlalchemy.orm import Session
from typing import List

def get_recent_messages_for_ws(db: Session, room_id: str, limit: int = 50) -> List[dict]:
    messages = db_get_recent_messages(db, room_id, limit)
    return [
        {
            "id": msg.id,
            "user_id": msg.user_id,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
        }
        for msg in reversed(messages)
    ]
