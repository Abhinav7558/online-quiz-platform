from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user

from ..schemas import submission as submission_schema
from ..models import Answer
from ..crud import submission as submission_crud

router = APIRouter(
    prefix="/submissions",
    tags=["submissions"],
)

@router.get("/me", response_model=List[submission_schema.SubmissionResult],status_code=status.HTTP_200_OK)
def get_my_submissions(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get all submissions by the current user."""
    submissions = submission_crud.get_submissions_by_student(db, current_user.id)
    if not submissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No submissions found")
    return submissions

@router.get("/{id}", response_model=submission_schema.SubmissionDetailResponse, status_code=status.HTTP_200_OK)
def get_submission_result(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    submission = submission_crud.get_submission_by_id(db, id, current_user.id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if not submission.score:
        raise HTTPException(status_code=404, detail="Submission not graded yet")
    
    if submission.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this submission")

    answers = db.query(Answer).filter(Answer.submission_id == id).all()
    feedback = {str(a.question_id): "Correct" if a.is_correct else "Incorrect"  for a in answers}

    return submission_schema.SubmissionDetailResponse(
        id=submission.id,
        quiz_id=submission.quiz_id,
        score=submission.score,
        passed=submission.passed,
        submitted_at=submission.submitted_at,
        feedback=feedback,
    )
