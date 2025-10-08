from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import Submission, Answer, Question, Quiz


def create_submission(db: Session, student_id: int, quiz_id: int, answers: dict):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise ValueError("Quiz not found")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()

    submission = Submission(student_id=student_id, quiz_id=quiz_id, submitted_at=datetime.now(timezone.utc))
    
    db.add(submission)
    db.commit()
    db.refresh(submission)

    for q in questions:
        ans_text = answers.get(q.id)
        is_correct = ans_text == q.correct_answer 
        db_answer = Answer(
            submission_id=submission.id,
            question_id=q.id,
            answer_text=ans_text,
            is_correct=is_correct
        )
        db.add(db_answer)

    db.commit()
    db.refresh(submission)

    return submission
