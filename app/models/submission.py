from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Boolean

from ..database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    score = Column(Integer, default=0)
    passed = Column(Boolean, default=False)
