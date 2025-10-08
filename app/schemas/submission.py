from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    answers: dict[int, str]


class SubmissionConfirmResponse(BaseModel):
    message: str = "Submission successful"
    id: int