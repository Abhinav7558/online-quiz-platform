from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    answers: dict[int, str]


class SubmissionConfirmResponse(BaseModel):
    message: str = "Submission successful"
    id: int


class SubmissionResult(BaseModel):
    id: int
    quiz_id: int
    score: float
    passed: bool
    submitted_at: datetime


class SubmissionFeedback(BaseModel):
    question_id: int
    result: str


class SubmissionDetailResponse(BaseModel):
    id: int
    quiz_id: int
    score: int
    passed: bool
    submitted_at: datetime
    feedback: Dict[int, str]

    class Config:
        from_attributes = True