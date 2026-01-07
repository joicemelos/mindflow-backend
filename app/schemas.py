from pydantic import BaseModel
from datetime import datetime

class AnswerBase(BaseModel):
    user: str | None = None
    q1: str | None = None
    q2: int | None = None
    q3: str | None = None

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

