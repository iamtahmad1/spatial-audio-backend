# app/db/crud.py
from sqlalchemy.orm import Session
from app.db.models import User, Room, RoomParticipant
from sqlalchemy import and_

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