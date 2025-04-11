# app/db/crud.py
from sqlalchemy.orm import Session
from app.db.models import User, Room, RoomParticipant, ChatMessage
from sqlalchemy import and_
from app.db.models import ChatMessage
from typing import List
from datetime import datetime


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_all_rooms(db: Session):
    return db.query(Room).all()

def is_user_in_room(db: Session, user_id, room_id) -> bool:
    return db.query(RoomParticipant).filter(
        and_(
            RoomParticipant.user_id == user_id,
            RoomParticipant.room_id == room_id
        )
    ).first() is not None

def save_message(db: Session, room_id: str, user_id: int, content: str):
    msg = ChatMessage(room_id=room_id, user_id=user_id, content=content)
    db.add(msg)
    db.commit()

def get_recent_messages(db: Session, room_id: str, limit: int = 50) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(limit)
        .all()
    )