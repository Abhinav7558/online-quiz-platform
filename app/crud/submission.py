from sqlalchemy.orm import Session

from typing import List
from ..models import Submission

def get_submission_by_id(db: Session, submission_id: int, student_id: int):
    """
    Fetch a single submission by ID.
    """
    return db.query(Submission).filter(Submission.id == submission_id).first()

def get_submissions_by_student(db: Session, student_id: int) -> List[Submission]:
    """Fetch all submissions for a given student."""
    return (
        db.query(Submission)
        .filter(Submission.student_id == student_id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )