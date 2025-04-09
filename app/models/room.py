from pydantic import BaseModel, Field
from uuid import UUID
from typing import List

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)

class RoomResponse(BaseModel):
    id: UUID
    name: str
    participants: List[str] = []