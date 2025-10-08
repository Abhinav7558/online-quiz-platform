from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas import auth as auth_schemas
from ..dependencies import get_db
from ..utils import password_utils, token_utils
from ..crud import auth as auth_crud


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=auth_schemas.UserRegisterResponse)
async def register_user(user: auth_schemas.UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = auth_crud.get_user_by_username_or_email(db, user.username, user.email)
    if existing_user:
       raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = auth_crud.create_user(db, user)

    return new_user
     

@router.post("/login", response_model=auth_schemas.UserLoginResponse)
async def login_user(user: auth_schemas.UserLoginCreate, db: Session = Depends(get_db)):             
    """User login"""
    db_user = auth_crud.get_user_by_username(db, user.username)
    if not db_user or not password_utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Here you would normally generate JWT tokens
    access_token = token_utils.create_access_token(data={"sub": db_user.username, "role": db_user.role.value})
    refresh_token = token_utils.create_refresh_token(data={"sub": db_user.username, "role": db_user.role.value})

    return {
        "access_token" : access_token,
        "refresh_token" : refresh_token
    }


@router.post("/refresh", response_model=auth_schemas.TokenRefreshResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        new_access_token = token_utils.create_access_token_from_refresh_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid token type, expected refresh token")

    return {
        "access_token": new_access_token,
    }
    

