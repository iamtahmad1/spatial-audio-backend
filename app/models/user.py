from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"