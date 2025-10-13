import logging

from sqlalchemy.orm import Session

from ..celery_app import celery_app
from app.database import SessionLocal
from app.models import Answer, Question, Submission, Quiz

logger = logging.getLogger(__name__)

@celery_app.task
def calculate_submission_score(submission_id: int):
    """Calculate score and pass/fail status for a submission."""
    db: Session = SessionLocal()

    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        db.close()
        return

    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    questions = db.query(Question).filter(Question.quiz_id == quiz.id).all()
    answers = db.query(Answer).filter(Answer.submission_id == submission.id).all()

    total_score = 0
    correct_count = 0

    for answer in answers:
        question = next((q for q in questions if q.id == answer.question_id), None)
        if not question:
            continue

        # Check correctness (for text-based questions)
        if question.correct_answer and answer.answer_text == question.correct_answer:
            answer.is_correct = True
            total_score += question.points
            correct_count += 1
        else:
            answer.is_correct = False

    passing_score = quiz.passing_score if quiz.passing_score is not None else 0
    passed = total_score >= passing_score

    # Update submission
    submission.score = total_score
    submission.passed = passed

    db.commit()
    db.close()

    logger.info(f"Graded submission {submission_id}: {total_score} correct, passed={passed}")

