from sqlalchemy import Column, ForeignKey, Integer, Boolean, Text

from ..database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
