from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    question_number: int = 1
    title: str
    description: str
    constraints: Optional[str] = None
    target_filename: str
    sample_inputs: List[str] = Field(default_factory=list)
    sample_outputs: List[str] = Field(default_factory=list)
    is_approved: bool = True

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    constraints: Optional[str] = None
    target_filename: Optional[str] = None
    sample_inputs: Optional[List[str]] = None
    sample_outputs: Optional[List[str]] = None
    is_approved: Optional[bool] = None

class QuestionResponse(QuestionBase):
    id: str
    assignment_id: str
    created_at: datetime

    class Config:
        from_attributes = True
