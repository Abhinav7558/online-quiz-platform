from pydantic import BaseModel
from typing import Optional


class QuizAnalyticsResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    submission_count: int

    class Config:
        form_attributes = True


class QuizDetailedAnalyticsResponse(BaseModel):
    quiz_id: int
    total_submissions: int
    average_score: float
    pass_rate: float
    highest_score: float
    lowest_score: float

    class Config:
        form_attributes = True


class StudentAnalyticsItem(BaseModel):
    student_id: int
    username: str
    quizzes_attempted: int
    quizzes_passed: int

    class Config:
        form_attributes = True


class IndividualSubmissionItem(BaseModel):
    quiz_id: int
    quiz_title: str
    score: Optional[float] = None
    passed: bool
    submitted_at: Optional[str] = None

    class Config:
        form_attributes = True


class IndividualStudentAnalyticsResponse(BaseModel):
    student_id: int
    username: str
    total_attempts: int
    total_passed: int
    submissions: list[IndividualSubmissionItem]

    class Config:
        form_attributes = True


class OverallAnalyticsResponse(BaseModel):
    total_users: int
    total_quizzes: int
    total_submissions: int

    class Config:
        form_attributes = True