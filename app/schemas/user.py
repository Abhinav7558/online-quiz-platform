from datetime import datetime

from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    instructor = "instructor"
    student = "student"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRoleRequest(BaseModel):
    role: UserRole
