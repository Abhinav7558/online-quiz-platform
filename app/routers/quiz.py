from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.tasks.calculate_score import calculate_submission_score
from ..dependencies import get_db, get_current_user, instructor_required, student_required, admin_or_instructor_required,admin_required
from ..crud import quiz as quiz_crud, question as question_crud, answer as answer_crud
from ..schemas import quiz as quiz_schemas, question as question_schemas, submission as submission_schemas
from ..models.user import UserRole


router = APIRouter(
    prefix="/quizzes",      
    tags=["Quizzes"]
)

@router.get("", response_model=List[quiz_schemas.QuizResponse], status_code=status.HTTP_200_OK)
def get_all_active_quizzes(user = Depends(get_current_user), db = Depends(get_db), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    """Get all active quizzes."""
    quizzes =  quiz_crud.get_quizzes_student(db=db, limit=limit, offset=offset)
    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found")
    
    return quizzes

@router.get("/me", response_model=List[quiz_schemas.QuizResponseWithPublishedStatus], status_code=status.HTTP_200_OK)
def get_my_quizzes(user = Depends(instructor_required), db = Depends(get_db), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    """Get quizzes created by the current instructor."""
    quizzes = quiz_crud.get_quizzes_instructor(db=db, instructor_id=user.id, limit=limit, offset=offset)
    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found")
    
    return quizzes

@router.get("/admin", response_model=List[quiz_schemas.QuizResponseWithPublishedStatus], status_code=status.HTTP_200_OK)
def get_all_quizzes(user = Depends(admin_required), db = Depends(get_db), limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    """Get quizzes created by the current instructor."""
    quizzes = quiz_crud.get_quizzess_admin(db=db, limit=limit, offset=offset)
    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found")
    
    return quizzes

@router.get("/{quiz_id}", response_model=quiz_schemas.QuizDetailResponse, status_code=status.HTTP_200_OK)
def get_quiz_by_id(quiz_id: int, user = Depends(get_current_user), db = Depends(get_db)):
    """Get quiz by ID."""
    quiz = quiz_crud.get_quiz_by_id(db=db, quiz_id=quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("", response_model=quiz_schemas.QuizDetailResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(quiz: quiz_schemas.QuizCreate, user = Depends(instructor_required), db = Depends(get_db)):
    """Create a new quiz."""
    existing_quiz = quiz_crud.get_quiz_by_title(db=db, title=quiz.title)
    if existing_quiz:
        raise HTTPException(status_code=400, detail="Quiz with this title already exists")
    new_quiz = quiz_crud.create_quiz(db=db, quiz=quiz, creator_id=user.id)

    return new_quiz

@router.patch("/{quiz_id}", response_model=quiz_schemas.QuizDetailResponse, status_code=status.HTTP_200_OK)
def update_quiz(quiz_id: int, quiz_update: quiz_schemas.QuizUpdate, user = Depends(instructor_required), db = Depends(get_db)):
    """Update an existing quiz."""
    quiz = quiz_crud.get_quiz_by_id(db=db, quiz_id=quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this quiz")
    
    if quiz_update.title is None and quiz_update.description is None and quiz_update.passing_score is None:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    updated_quiz = quiz_crud.update_quiz(db=db, quiz=quiz, quiz_update=quiz_update)
    return updated_quiz

@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(quiz_id: int, user = Depends(admin_or_instructor_required), db = Depends(get_db)):
    quiz = quiz_crud.get_quiz_by_id(db=db, quiz_id=quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.created_by != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this quiz")
    
    quiz_crud.delete_quiz(db=db, quiz=quiz)
    return None

@router.get("/{quiz_id}/questions", response_model=List[question_schemas.QuestionResponse], status_code=status.HTTP_200_OK)
def get_all_questions_by_quiz(
    quiz_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100, description="Number of questions to return"),
    offset: int = Query(0, ge=0, description="Number of questions to skip")
):
    """Get all questions for a specific quiz with pagination."""
    quiz = quiz_crud.get_quiz_by_id(db, quiz_id, user=user)
    if not quiz:
        raise HTTPException(
            status_code=404,
            detail="Quiz not found"
        )
    
    questions = question_crud.get_questions_by_quiz(db, quiz_id, skip=offset, limit=limit)
    if not questions or len(questions) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No questions found for this quiz"
        )
    
    return questions


@router.post("/{quiz_id}/questions", response_model=question_schemas.QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    quiz_id: int,
    question: question_schemas.QuestionCreate,
    user=Depends(instructor_required),
    db: Session = Depends(get_db)
):
    """Create a new question for a specific quiz."""
    quiz = quiz_crud.get_quiz_by_id(db, quiz_id, user=user)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if quiz.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add questions to this quiz"
        )
    
    try:
        new_question = question_crud.create_question(db, quiz_id, question)
        return new_question
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create question: {str(e)}"
        )
    
@router.patch("/{quiz_id}/publish", response_model=quiz_schemas.QuizDetailResponse, status_code=status.HTTP_200_OK)
def publish_quiz(quiz_id: int, user = Depends(admin_or_instructor_required), db = Depends(get_db)):
    """Publish a quiz."""
    quiz = quiz_crud.get_quiz_by_id(db=db, quiz_id=quiz_id, user=user)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.created_by != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to publish this quiz")
    
    if quiz.is_published:
        raise HTTPException(status_code=400, detail="Quiz is already published")
    
    questions = question_crud.get_questions_by_quiz(db=db, quiz_id=quiz_id)
    if not questions or len(questions) == 0:
        raise HTTPException(status_code=400, detail="Cannot publish a quiz with no questions")

    total_points = quiz_crud.get_total_points(db=db, quiz_id=quiz_id)
    if total_points < quiz.passing_score:
        raise HTTPException(status_code=400, detail="Total question points must be greater than or equal to passing score")
    
    quiz.is_published = True
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    return quiz
    
@router.post("/{quiz_id}/submit", response_model=submission_schemas.SubmissionConfirmResponse, status_code=status.HTTP_201_CREATED)
def submit_answers(quiz_id: int, data: submission_schemas.SubmissionCreate, user = Depends(student_required), db = Depends(get_db)):
    """Submit answers for a quiz."""
    try:
        is_submitted = answer_crud.has_submitted(db=db, student_id=user.id, quiz_id=quiz_id)
        if is_submitted:
            raise HTTPException(status_code=400, detail="You have already submitted this quiz")
        quiz = quiz_crud.get_quiz_by_id(db=db, quiz_id=quiz_id, user=user)
        if not quiz or not quiz.is_published:
            raise HTTPException(status_code=404, detail="Quiz not found or not published")
        submission = answer_crud.create_submission(
            db=db,
            student_id=user.id,
            quiz_id=quiz_id,
            answers=data.answers
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    calculate_submission_score.delay(submission.id)

    return submission