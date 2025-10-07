from sqlalchemy.orm import Session

from ..models.quiz import Quiz
from ..schemas import quiz as quiz_schemas

def get_quizzes(db: Session, limit: int = 10, offset: int = 0):
    """Retrieve quizzes with pagination."""
    return db.query(Quiz).offset(offset).limit(limit).all()

def get_quiz_by_id(db: Session, quiz_id: int):
    """Retrieve a quiz by its ID."""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()

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