from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.quiz import Quiz
from ..models.question import Question
from ..schemas import quiz as quiz_schemas
from ..models.user import UserRole

def get_quizzes_student(db: Session, limit: int = 10, offset: int = 0):
    """Retrieve quizzes with pagination."""
    return db.query(Quiz).filter(Quiz.is_published == True).offset(offset).limit(limit).all()

def get_quizzes_instructor(db: Session, instructor_id: int, limit: int = 10, offset: int = 0):
    """Retrieve quizzes created by a specific instructor with pagination."""
    return db.query(Quiz).filter(Quiz.created_by == instructor_id).offset(offset).limit(limit).all()

def get_quizzess_admin(db: Session, limit: int = 10, offset: int = 0):
    """Retrieve all quizzes for admin with pagination."""
    return db.query(Quiz).offset(offset).limit(limit).all()

def get_quiz_by_id(db: Session, quiz_id: int, user):
    """Retrieve a quiz by its ID."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id,Quiz.is_published == True).first()
    if not quiz:
        if user.role == UserRole.INSTRUCTOR:
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id,Quiz.created_by == user.id).first()
        elif user.role == UserRole.ADMIN:
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()    

    return quiz

def create_quiz(db: Session, quiz, creator_id: int):
    """Create a new quiz."""
    new_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        passing_score=quiz.passing_score,
        created_by=creator_id
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    return new_quiz

def get_total_points(db: Session, quiz_id: int) -> int:
    """
    Calculate total points of all questions in a quiz.
    Returns 0 if the quiz has no questions.
    """
    total = db.query(func.sum(Question.points)) \
              .filter(Question.quiz_id == quiz_id) \
              .scalar()
    return total or 0

def get_quiz_by_title(db: Session, title: str):
    """Retrieve a quiz by its title."""
    return db.query(Quiz).filter(Quiz.title == title).first() 

def update_quiz(db: Session, quiz: Quiz, quiz_update: quiz_schemas.QuizUpdate):
    """Update an existing quiz."""
    if quiz_update.title is not None:
        quiz.title = quiz_update.title
    if quiz_update.description is not None:
        quiz.description = quiz_update.description
    if quiz_update.passing_score is not None:
        quiz.passing_score = quiz_update.passing_score
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

def delete_quiz(db: Session, quiz: Quiz):
    """Delete a quiz."""
    db.delete(quiz)
    db.commit()