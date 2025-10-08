from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..crud import analytics as analytics_crud
from ..schemas import analytics as analytics_schema
from ..dependencies import get_db, admin_or_instructor_required


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get("/quizzes/", response_model=List[analytics_schema.QuizAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_quiz_analytics(
    db: Session = Depends(get_db),
    user=Depends(admin_or_instructor_required)
):
    """Return quizzes with submission counts sorted by count descending."""
    return analytics_crud.get_quiz_analytics(db, user)


@router.get("/quizzes/{quiz_id}", response_model=analytics_schema.QuizDetailedAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_quiz_detailed_analytics(quiz_id: int, db=Depends(get_db), user=Depends(admin_or_instructor_required)):
    """Return detailed analytics for a specific quiz."""
    try:
        quiz_analytics = analytics_crud.get_quiz_detailed_analytics(db, quiz_id, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return quiz_analytics
