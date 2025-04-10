from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(30), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)

    room_associations = relationship(
        "RoomParticipant",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class Room(Base):
    __tablename__ = "rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False)

    participant_associations = relationship(
        "RoomParticipant",
        back_populates="room",
        cascade="all, delete-orphan"
    )

# -------------------------------
# RoomParticipant Join Table
# -------------------------------
class RoomParticipant(Base):
    __tablename__ = "room_participants"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships back to User and Room
    user = relationship("User", back_populates="room_associations")
    room = relationship("Room", back_populates="participant_associations")

    # Ensure a user can’t join the same room twice
    __table_args__ = (
        UniqueConstraint("user_id", "room_id", name="uix_user_room"),
    )