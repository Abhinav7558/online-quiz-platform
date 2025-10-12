from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

class QuizBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    total_points: int = Field(0, ge=0)


class QuizCreate(QuizBase):
    passing_score: int = Field(..., ge=0, le=100)


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    passing_score: Optional[int] = Field(None, ge=0, le=100)

    class Config:
        extra = "forbid"  # prevent sending unknown fields


class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    total_points: int

    class Config:
        from_attributes = True


class QuizResponseWithPublishedStatus(QuizResponse):
    is_published: bool

    class Config:
        from_attributes = True


class QuizDetailResponse(QuizResponse):
    passing_score: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
