from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.auth import UserCreate, UserCreateResponse
from ..dependencies import get_db
from ..models.user import User
from ..utils.password_utils import get_password_hash


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserCreateResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
       raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = get_password_hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
     

@router.post("/login")
async def login_user():             
    """User login"""
    return {"message": "User logged in successfully"}

@router.post("/logout")
async def logout_user():
    """User logout"""
    return {"message": "User logged out successfully"}

