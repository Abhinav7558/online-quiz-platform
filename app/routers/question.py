from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_db, instructor_required
from ..crud import question as question_crud
from ..schemas import question as question_schemas
from ..models.quiz import Quiz

router = APIRouter(
    prefix="/questions",      
    tags=["Questions"]
)

@router.get("{question_id}", response_model=question_schemas.QuestionDetailResponse, status_code=status.HTTP_200_OK)
def get_question_by_id(question_id: int, user = Depends(instructor_required), db = Depends(get_db)):
    """Get question by ID."""
    question = question_crud.get_question_by_id(db=db, question_id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.question_type.name == "MCQ":
        options  = question_crud.get_options_by_question(db=db, question_id=question.id)
        question.options = options
    return question

@router.patch("/{question_id}", response_model=question_schemas.QuestionResponse, status_code=status.HTTP_200_OK)
def update_question(question_id: int, question_update: question_schemas.QuestionUpdate, user = Depends(instructor_required), db = Depends(get_db)):
    """Update an existing quiz."""
    question = question_crud.get_question_by_id(db=db, question_id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question_update.text is None and question_update.question_type is None and question_update.correct_answer is None and question_update.points is None:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    updated_question = question_crud.update_question(db=db, question=question, question_update=question_update)
    return updated_question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(question_id: int, user = Depends(instructor_required), db = Depends(get_db)):
    question = question_crud.get_question_by_id(db=db, question_id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == question.quiz_id).first()
    if quiz:
        quiz.passing_score = max(0, quiz.passing_score - question.points)
        db.add(quiz)
    
    question_crud.delete_question(db=db, question=question)
    return None