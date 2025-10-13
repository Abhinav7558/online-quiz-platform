from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from ..schemas import options as option_schemas

class QuestionTypeEnum(str, Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "TRUE_FALSE"
    SHORT_ANSWER = "SHORT_ANSWER"  
    

class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1)
    question_type: QuestionTypeEnum
    correct_answer: str 
    points: int = Field(default=1, ge=1)

    @field_validator("correct_answer")
    @classmethod
    def validate_correct_answer(cls, value, info):
        """
        Validate correct_answer based on question_type.
        """
        q_type = info.data.get("question_type")
        if q_type == QuestionTypeEnum.MCQ:
            if value not in {"A", "B", "C", "D"}:
                raise ValueError("For MCQ, correct_answer must be one of A, B, C, D")
        elif q_type == QuestionTypeEnum.TRUE_FALSE:
            if value.upper() not in {"TRUE", "FALSE"}:
                raise ValueError("For TRUE_FALSE, correct_answer must be TRUE or FALSE")
        # SHORT_ANSWER: no restriction
        return value


class QuestionCreate(QuestionBase):
    options: Optional[List[option_schemas.OptionCreate]] = None

    @model_validator(mode='after')
    @classmethod
    def validate_question(cls, values):
        q_type = values.question_type
        options = values.options

        if q_type == QuestionTypeEnum.MCQ:
            if not options or len(options) != 4:
                raise ValueError("MCQ must have 4 options")
        elif q_type == QuestionTypeEnum.TRUE_FALSE:
            q_correct_answer = values.correct_answer
            if q_correct_answer and q_correct_answer.upper() not in {"TRUE", "FALSE"}:
                raise ValueError("For TRUE_FALSE, correct_answer must be TRUE or FALSE")
        return values


class QuestionUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionTypeEnum] = None
    correct_answer: Optional[str] = Field(None, min_length=1)
    points: Optional[int] = Field(None, ge=1)

    options: Optional[List[option_schemas.OptionCreate]] = None

    @model_validator(mode='after')
    @classmethod
    def validate_question(cls, values):
        q_type = values.question_type
        options = values.options
        if q_type == QuestionTypeEnum.MCQ:
            if not options or len(options) != 4:
                raise ValueError("MCQ must have 4 options")
        return values


class QuestionResponse(BaseModel):
    id: int
    quiz_id: int
    text: str = Field(..., min_length=1)
    question_type: QuestionTypeEnum
    points: int = Field(default=1, ge=1)

    @field_validator('question_type', mode='before')
    @classmethod
    def convert_question_type(cls, v):
        # Convert SQLAlchemy enum to Pydantic enum
        if hasattr(v, 'name'):
            # It's a SQLAlchemy enum, use the name (MCQ, TRUE_FALSE, SHORT_ANSWER)
            return v.name
        return v

    class Config:
        from_attributes = True

class QuestionDetailResponse(QuestionResponse): 
    options: Optional[List[option_schemas.OptionResponse]] = None

    class Config:
        from_attributes = True


