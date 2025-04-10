from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from sqlalchemy.orm import Session, joinedload

from app.models.room import RoomCreate, RoomResponse
from app.dependencies.auth import get_current_user
from app.db.models import Room, User, RoomParticipant
from app.db.deps import get_db
from app.db.crud import get_all_rooms

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


@router.get("/rooms", response_model=list[dict])
def get_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rooms = get_all_rooms(db)
    return [{"id": str(room.id), "name": room.name} for room in rooms]

@router.post("/{room_id}/join")
def join_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(Room).filter_by(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    already_in_room = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user.id
    ).first()
    if already_in_room:
        raise HTTPException(status_code=400, detail="User already in the room")

    participant = RoomParticipant(user_id=current_user.id, room_id=room_id)
    db.add(participant)
    db.commit()
    return {"message": f"{current_user.username} joined room {room.name}"}

@router.post("/{room_id}/leave")
def leave_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(Room).filter_by(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    participant = db.query(RoomParticipant).filter_by(
        room_id=room_id, user_id=current_user.id
    ).first()
    if not participant:
        raise HTTPException(status_code=400, detail="User not in the room")

    db.delete(participant)
    db.commit()
    return {"message": f"{current_user.username} left room {room.name}"}

@router.get("/{room_id}", summary="Get room details with participants")
def get_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).options(
        joinedload(Room.participant_associations).joinedload(RoomParticipant.user)
    ).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return {
        "id": str(room.id),
        "name": room.name,
        "creator_id": str(room.creator_id),
        "participants": [
            {
                "id": str(p.user.id),
                "username": p.user.username,
                "joined_at": p.joined_at.isoformat()
            }
            for p in room.participant_associations
        ]
    }

@router.delete("/{room_id}", summary="Delete a room")
def delete_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this room")

    db.delete(room)
    db.commit()
    return {"message": "Room deleted"}