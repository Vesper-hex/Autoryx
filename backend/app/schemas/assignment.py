from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.question import QuestionResponse, QuestionCreate

class AssignmentBase(BaseModel):
    title: str
    week_module: Optional[str] = None
    language: str = "cpp"

class AssignmentCreate(AssignmentBase):
    raw_content: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = None

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    week_module: Optional[str] = None
    language: Optional[str] = None

class AssignmentResponse(AssignmentBase):
    id: str
    source_filename: Optional[str] = None
    raw_content: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True

class TextExtractionRequest(BaseModel):
    title: str
    week_module: Optional[str] = None
    language: str = "cpp"
    text: str
