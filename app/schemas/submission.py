from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    answers: dict[int, str]


class SubmissionConfirmResponse(BaseModel):
    id: int
    message: str = "Submission successful"


class SubmissionResult(BaseModel):
    id: int
    quiz_id: int
    score: Optional[float]
    passed: Optional[bool]
    submitted_at: datetime


class SubmissionFeedback(BaseModel):
    question_id: int
    result: str


class SubmissionDetailResponse(BaseModel):
    id: int
    quiz_id: int
    score: Optional[float]
    passed: Optional[bool]
    submitted_at: datetime
    feedback: Dict[int, str]

    class Config:
        from_attributes = True