from pydantic import BaseModel


class OptionCreate(BaseModel):
    text: str
    is_correct: bool = False


class OptionResponse(OptionCreate):
    id: int

    class Config:
        from_attributes = True
