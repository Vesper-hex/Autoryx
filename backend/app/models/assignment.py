from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def generate_id(prefix: str = "asgn") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(32), primary_key=True, default=lambda: generate_id("asgn"))
    title = Column(String(255), nullable=False)
    week_module = Column(String(100), nullable=True)
    language = Column(String(50), nullable=False, default="cpp")
    source_filename = Column(String(255), nullable=True)
    raw_content = Column(Text, nullable=True)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = relationship("Question", back_populates="assignment", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="assignment", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(32), primary_key=True, default=lambda: generate_id("q"))
    assignment_id = Column(String(32), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False, default=1)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    constraints = Column(Text, nullable=True)
    target_filename = Column(String(100), nullable=False)
    sample_inputs = Column(JSON, default=list)
    sample_outputs = Column(JSON, default=list)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignment = relationship("Assignment", back_populates="questions")
    solutions = relationship("GeneratedSolution", back_populates="question", cascade="all, delete-orphan")
