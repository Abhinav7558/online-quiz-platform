from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

from ..database import Base


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
