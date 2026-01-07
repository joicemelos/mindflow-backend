from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, default="anonymous")
    q1 = Column(String)
    q2 = Column(Integer)
    q3 = Column(String)
    q4 = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
