from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(30), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    creator_id = Column(String(30), nullable=False)