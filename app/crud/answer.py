from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import Submission, Answer, Question, Quiz, QuestionType


def create_submission(db: Session, student_id: int, quiz_id: int, answers: dict):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise ValueError("Quiz not found")

    questions_db = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    questions = answers.keys()
    for q_id in questions:
        if q_id not in [q.id for q in questions_db]:
            raise ValueError(f"Question ID {q_id} does not belong to Quiz")
    submission = Submission(student_id=student_id, quiz_id=quiz_id, submitted_at=datetime.now(timezone.utc))
    
    db.add(submission)
    db.commit()
    db.refresh(submission)

    for q_id in questions:
        ans_text = answers.get(q_id)
        question_type = questions_db[[q.id for q in questions_db].index(q_id)].question_type

        if question_type == QuestionType.MCQ and ans_text not in ["A", "B", "C", "D"]:
            raise ValueError(f"Invalid answer for multiple choice question ID {q_id}") 
        
        if question_type == QuestionType.TRUE_FALSE and ans_text.upper() not in ["TRUE", "FALSE"]:
            raise ValueError(f"Invalid answer for true/false question ID {q_id}")
        
        if question_type == QuestionType.TRUE_FALSE:
            ans_text = ans_text.upper()

        is_correct = ans_text == questions_db[[q.id for q in questions_db].index(q_id)].correct_answer
        db_answer = Answer(
            submission_id=submission.id,
            question_id=q_id,
            answer_text=ans_text,
            is_correct=is_correct
        )
        db.add(db_answer)

    db.commit()
    db.refresh(submission)

    return submission

def has_submitted(db: Session, student_id: int, quiz_id: int) -> bool:
    existing_submission = db.query(Submission).filter(
        Submission.student_id == student_id,
        Submission.quiz_id == quiz_id
    ).first()
    return existing_submission is not None
