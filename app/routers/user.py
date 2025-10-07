from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies import get_db, admin_required
from ..schemas import user as user_schemas
from ..crud import user as user_crud
from ..models.user import UserRole


router = APIRouter(
    prefix="/users", 
    tags=["Users"]
)

@router.get("", response_model=List[user_schemas.UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(user = Depends(admin_required),  db: Session = Depends(get_db), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    """Get all users for admin."""
    users = user_crud.get_users(db=db, limit=limit, offset=offset)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")   
    return users

@router.get("/{user_id}", response_model=user_schemas.UserDetailResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, user = Depends(admin_required), db: Session = Depends(get_db)):
    """Get user by ID for admin."""
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/role", response_model=user_schemas.UserDetailResponse, status_code=status.HTTP_200_OK)
def update_user_role(user_id: int, role: UserRole = Query(...), user = Depends(admin_required), db: Session = Depends(get_db)):
    """Update user role for admin."""
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        updated_user = user_crud.update_user_role(db=db, user=user, new_role=role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return updated_user
    
