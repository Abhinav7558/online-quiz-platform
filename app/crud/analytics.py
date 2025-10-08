from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import UserRole
from ..models import Quiz, Submission, User

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

def get_student_analytics(db: Session, user):
    """Return student analytics."""
    attempts_sq = (
        db.query(
            Submission.student_id.label("student_id"),
            func.count(func.distinct(Submission.quiz_id)).label("quizzes_attempted"),
        )
        .group_by(Submission.student_id)
        .subquery()
    )

    passed_sq = (
        db.query(
            Submission.student_id.label("student_id"),
            func.count(func.distinct(Submission.quiz_id)).label("quizzes_passed"),
        )
        .filter(Submission.passed == True)
        .group_by(Submission.student_id)
        .subquery()
    )

    q = (
        db.query(
            User.id.label("id"),
            User.username.label("username"),
            func.coalesce(attempts_sq.c.quizzes_attempted, 0).label("quizzes_attempted"),
            func.coalesce(passed_sq.c.quizzes_passed, 0).label("quizzes_passed"),
        )
        .outerjoin(attempts_sq, User.id == attempts_sq.c.student_id)
        .outerjoin(passed_sq, User.id == passed_sq.c.student_id)
        .filter(User.role == UserRole.STUDENT)
        .order_by(func.coalesce(passed_sq.c.quizzes_passed, 0).desc())
    )

    results = q.all()

    analytics = []
    for sid, username, quizzes_attempted, quizzes_passed in results:
        analytics.append(
            {
                "student_id": int(sid),
                "username": username,
                "quizzes_attempted": int(quizzes_attempted or 0),
                "quizzes_passed": int(quizzes_passed or 0),
            }
        )

    return analytics

def get_individual_student_analytics(db: Session, student_id: int, user):
    """Return individual student analytics."""
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        raise ValueError("Student not found")

    if user.role == UserRole.INSTRUCTOR:
        instructor_quiz_ids = db.query(Quiz.id).filter(Quiz.created_by == user.id).subquery()
        submission_exists = db.query(Submission).filter(
            Submission.student_id == student_id,
            Submission.quiz_id.in_(instructor_quiz_ids)
        ).first()
        if not submission_exists:
            raise PermissionError("Not authorized to view analytics for this student")

    total_attempts = db.query(func.count(Submission.id)).filter(Submission.student_id == student_id).scalar() or 0
    total_passed = db.query(func.count(Submission.id)).filter(Submission.student_id == student_id, Submission.passed == True).scalar() or 0

    submissions_q = db.query(Submission, Quiz).join(Quiz, Submission.quiz_id == Quiz.id)
    submissions_q = submissions_q.filter(Submission.student_id == student_id)
    if user.role == UserRole.INSTRUCTOR:
        submissions_q = submissions_q.filter(Quiz.created_by == user.id)

    submissions = submissions_q.order_by(Submission.submitted_at.desc()).all()

    per_quiz = []
    for submission, quiz in submissions:
        per_quiz.append(
            {
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "score": submission.score,
                "passed": bool(submission.passed),
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at is not None else None,
            }
        )

    return {
        "student_id": student.id,
        "username": student.username,
        "total_attempts": int(total_attempts),
        "total_passed": int(total_passed),
        "submissions": per_quiz,
    }


def get_overall_analytics(db: Session, user):
    """Return overall analytics: total users, total quizzes, total submissions, average score."""
    total_users = db.query(func.count(User.id)).scalar() or 0

    quiz_q = db.query(Quiz)
    submission_q = db.query(Submission)

    total_quizzes = quiz_q.count() or 0
    total_submissions = submission_q.count() or 0

    return {
        "total_users": int(total_users),
        "total_quizzes": int(total_quizzes),
        "total_submissions": int(total_submissions),
    }
