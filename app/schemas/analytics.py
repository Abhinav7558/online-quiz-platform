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