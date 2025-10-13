from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_db, instructor_required, get_current_user, admin_or_instructor_required
from ..crud import question as question_crud
from ..crud import quiz as quiz_crud
from ..schemas import question as question_schemas
from ..models.quiz import Quiz
from ..models.user import UserRole

router = APIRouter(
    prefix="/questions",      
    tags=["Questions"]
)

@router.get("{question_id}", response_model=question_schemas.QuestionDetailResponse, status_code=status.HTTP_200_OK)
def get_question_by_id(question_id: int, user = Depends(get_current_user), db = Depends(get_db)):
    """Get question by ID."""
    question = question_crud.get_question_by_id(db=db, question_id=question_id, user=user)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.question_type.name == "MCQ":
        options  = question_crud.get_options_by_question(db=db, question_id=question.id)
        question.options = options
    return question

@router.patch("/{question_id}", response_model=question_schemas.QuestionResponse, status_code=status.HTTP_200_OK)
def update_question(question_id: int, question_update: question_schemas.QuestionUpdate, user = Depends(instructor_required), db = Depends(get_db)):
    """Update an existing quiz."""
    question = question_crud.get_question_by_id(db=db, question_id=question_id, user=user)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    quiz = quiz_crud.get_quiz_by_id(db=db, quiz_id=question.quiz_id, user=user)

    if quiz.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this question")
    
    if question_update.text is None and question_update.question_type is None and question_update.correct_answer is None and question_update.points is None:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    try:
        updated_question = question_crud.update_question(
            db=db, question=question, question_update=question_update
        )
        return updated_question

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, user = Depends(admin_or_instructor_required), db = Depends(get_db)):
    """Delete a question."""
    question = question_crud.get_question_by_id(db=db, question_id=question_id, user=user)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if user.role == UserRole.INSTRUCTOR:
        quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
        if quiz.created_by != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this question")
    
    quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
    if quiz:
        quiz.passing_score = max(0, quiz.passing_score - question.points)
        db.add(quiz)
    
    question_crud.delete_question(db=db, question=question)
    return None