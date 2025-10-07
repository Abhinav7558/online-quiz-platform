from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.option import Option
from app.models.question import Question
from ..schemas import question as schemas
from ..models.quiz import Quiz


def get_questions_by_quiz(db: Session, quiz_id: int, skip: int = 0, limit: int = 10) -> List[Question]:
    """Get all questions for a quiz with pagination."""
    return db.query(Question)\
        .filter(Question.quiz_id == quiz_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_question(db: Session, quiz_id: int, question: schemas.QuestionCreate):
    db_question = Question(
        quiz_id=quiz_id,
        text=question.text,
        question_type=question.question_type.value,
        points=question.points,
        correct_answer=question.correct_answer  # Optional for MCQ
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    # Add options if it's MCQ
    if question.question_type == schemas.QuestionTypeEnum.MCQ:
        labels = ["A", "B", "C", "D"] 
        for i, opt in enumerate(question.options):
            db_option = Option(
                question_id=db_question.id,
                text=f"{labels[i]}. {opt.text}",
                is_correct=opt.is_correct
            )
            db.add(db_option)
        db.commit()
    
    db.refresh(db_question)
    return db_question


def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    """Get a question by ID."""
    return db.query(Question).filter(Question.id == question_id).first()


def update_question(db: Session, question, question_update: schemas.QuestionUpdate):
    """Update a question.""" 
    update_data = question_update.model_dump(exclude_unset=True)

    # Adjust passing score if points are updated
    if "points" in update_data:
        new_points = update_data["points"]
        old_points = question.points
        delta = new_points - old_points
        quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
        old_passing_score = quiz.passing_score
        print(old_passing_score, delta)
        if quiz:
            if delta != 0:
                quiz.passing_score = quiz.passing_score + int(old_passing_score/delta)
                print(quiz.passing_score)
            db.add(quiz)

    for field, value in update_data.items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question) -> bool:
    """Delete a question."""
    
    db.delete(question)
    db.commit()
    return True