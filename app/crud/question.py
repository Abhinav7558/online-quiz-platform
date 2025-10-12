from typing import List

from sqlalchemy.orm import Session

from ..schemas import question as schemas
from ..models.quiz import Quiz
from ..models.user import UserRole
from ..models.question import Question, QuestionType
from app.models.option import Option


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

    update_quiz_total_points(db, quiz_id, db_question.points)
    
    db.refresh(db_question)
    return db_question


def get_question_by_id(db: Session, question_id: int, user):
    """Get a question by ID."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        return None
    quiz = (
        db.query(Quiz)
        .join(Question, Quiz.id == Question.quiz_id)
        .filter(Question.id == question.id, Quiz.is_published == True)
        .first()
    )
    if not quiz:
        if user.role == UserRole.INSTRUCTOR:
            question = db.query(Question).filter(Question.id == question_id).join(Quiz).filter(Quiz.created_by == user.id).first()
        elif user.role == UserRole.ADMIN:
            question = db.query(Question).filter(Question.id == question_id).first()
        elif user.role == UserRole.STUDENT:
            question = None  
    return question


def update_question(db: Session, question, question_update: schemas.QuestionUpdate):
    """Update a question.""" 
    update_data = question_update.model_dump(exclude_unset=True)

    q_type = update_data.get("question_type", question.question_type)

    if "correct_answer" in update_data:
        correct_answer = update_data["correct_answer"]

        if q_type == QuestionType.MCQ and correct_answer not in {"A", "B", "C", "D"}:
            raise ValueError("For MCQ, correct_answer must be one of 'A', 'B', 'C', 'D'.")

        elif q_type == QuestionType.TRUE_FALSE and correct_answer.upper() not in {"TRUE", "FALSE"}:
            raise ValueError("For TRUE_FALSE, correct_answer must be 'TRUE' or 'FALSE'.")

    # Adjust passing score if points are updated
    if "points" in update_data:
        new_points = update_data["points"]
        old_points = question.points
        delta = new_points - old_points

        quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
        old_passing_score = quiz.passing_score
        if quiz:
            if delta != 0:
                quiz.passing_score = quiz.passing_score + int(old_passing_score/delta)
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

    update_quiz_total_points(db, question.quiz_id, -question.points)
    return True

def get_options_by_question(db: Session, question_id: int):
    """Get options for a specific question."""
    return db.query(Option).filter(Option.question_id == question_id).all()

def update_quiz_total_points(db: Session, quiz_id: int, additional_points: int):
    """Update the total points of a quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz:
        quiz.total_points += additional_points
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
    return quiz