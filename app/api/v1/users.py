from fastapi import APIRouter
from app.models.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/", response_mode=UserResponse)
def create_user(user: UserCreate):
    return UserResponse(id="u123", username=user.username)