from fastapi import APIRouter, Depends
from uuid import uuid4
from app.models.room import RoomCreate, RoomResponse


router = APIRouter()

@router.post("/", response_model=RoomResponse)
def create_room(room: RoomCreate):
    return RoomResponse(id=uuid4(), name=room.name, participants=[])
