from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import UserRole
from ..models import Quiz, Submission

def get_quiz_analytics(db: Session, user):
    """
    Return quizzes with submission counts, sorted descending.
    """
    results = (
        db.query(Quiz, func.count(Submission.id).label("submission_count"))
        .outerjoin(Submission, Quiz.id == Submission.quiz_id)
        .group_by(Quiz.id)
        .order_by(func.count(Submission.id).desc())
    )

    if user.role == UserRole.INSTRUCTOR:
        results = results.filter(Quiz.created_by == user.id)

    analytics = []
    for quiz, submission_count in results:
        analytics.append(
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "submission_count": int(submission_count or 0),
            }
        )
    return analytics

def get_quiz_detailed_analytics(db: Session, quiz_id: int, user):
    """Return detailed analytics for a specific quiz"""

    if db.query(Quiz).filter(Quiz.id == quiz_id).first() is None:
        raise ValueError("Quiz not found")

    if user.role == UserRole.INSTRUCTOR:
        if not db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == user.id).first():
            raise PermissionError("Not authorized to view analytics for this quiz")

    total_submissions = db.query(func.count(Submission.id)).filter(Submission.quiz_id == quiz_id).scalar()

    if total_submissions == 0:
        return {
            "quiz_id": quiz_id,
            "total_submissions": 0,
            "average_score": 0.0,
            "pass_rate": 0.0,
            "highest_score": 0.0,
            "lowest_score": 0.0,
        }

    average_score = db.query(func.avg(Submission.score)).filter(Submission.quiz_id == quiz_id).scalar() or 0.0
    pass_count = db.query(func.count(Submission.id)).filter(Submission.quiz_id == quiz_id, Submission.passed == True).scalar() or 0
    highest_score = db.query(func.max(Submission.score)).filter(Submission.quiz_id == quiz_id).scalar() or 0.0
    lowest_score = db.query(func.min(Submission.score)).filter(Submission.quiz_id == quiz_id).scalar() or 0.0

    pass_rate = (pass_count / total_submissions) * 100 if total_submissions > 0 else 0.0

    return {
        "quiz_id": quiz_id,
        "total_submissions": int(total_submissions),
        "average_score": float(average_score),
        "pass_rate": float(pass_rate),
        "highest_score": float(highest_score),
        "lowest_score": float(lowest_score),
    }
