from fastapi import APIRouter, Depends
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.room import RoomCreate, RoomResponse
from app.dependencies.auth import get_current_user
from app.db.models import Room, User
from app.db.deps import get_db


router = APIRouter()

@router.post("/", response_model=RoomResponse)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_room = Room(
        id=uuid4(),
        name=room.name,
        creator_id=current_user.id  # assuming you track the user who created it
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    # Now only logged-in users can create a room
    return RoomResponse(
        id=uuid4(),
        name=room.name,
        participants=[],
    )


# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MTIzIiwiZXhwIjoxNzQ0MjI5NjY3fQ.wAhxo4X8egvsy-L_G2AIDqzS7NESeNBaP0x0XqubFS8

# curl -X POST http://localhost:8000/rooms/ \
#   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MTIzIiwiZXhwIjoxNzQ0MjI5NjY3fQ.wAhxo4X8egvsy-L_G2AIDqzS7NESeNBaP0x0XqubFS8" \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Test Room"}'
