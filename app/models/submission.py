from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Boolean

from ..database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    score = Column(Integer, nullable=True)
    passed = Column(Boolean, nullable=True)
