from fastapi import APIRouter, HTTPException, Depends
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.user import UserCreate, UserResponse
from app.db.models import User as UserModel
from app.db.deps import get_db
from app.services.auth import hash_password
from app.dependencies.auth import get_current_user
from app.services.auth import verify_password


router = APIRouter()

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    

    hashed = hash_password(user.password)
    new_user = UserModel(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    
    return UserResponse(id=new_user.id, username=new_user.username)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return UserResponse(id=current_user.id, username=current_user.username)