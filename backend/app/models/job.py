from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def generate_job_id() -> str:
    return f"job_{uuid.uuid4().hex[:10]}"

def generate_sol_id() -> str:
    return f"sol_{uuid.uuid4().hex[:10]}"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(32), primary_key=True, default=generate_job_id)
    assignment_id = Column(String(32), ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="queued", index=True)
    # queued, extracting, awaiting_review, generating, compiling, testing, repairing, ready_to_publish, publishing, published, failed, cancelled
    current_step = Column(String(100), default="Initialized")
    progress_percent = Column(Integer, default=0)
    
    target_branch = Column(String(150), nullable=True)
    commit_sha = Column(String(100), nullable=True)
    commit_url = Column(String(255), nullable=True)
    output_directory = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    assignment = relationship("Assignment", back_populates="jobs")
    solutions = relationship("GeneratedSolution", back_populates="job", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="job", cascade="all, delete-orphan")

class GeneratedSolution(Base):
    __tablename__ = "generated_solutions"

    id = Column(String(32), primary_key=True, default=generate_sol_id)
    job_id = Column(String(32), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(32), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    
    filename = Column(String(100), nullable=False)
    source_code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    
    compilation_status = Column(String(50), default="not_run") # passed, failed, timeout, not_run
    compiler_output = Column(Text, nullable=True)
    
    tests_total = Column(Integer, default=0)
    tests_passed = Column(Integer, default=0)
    test_results = Column(JSON, default=list)
    
    repair_attempts = Column(Integer, default=0)
    repair_history = Column(JSON, default=list)
    validation_status = Column(String(50), default="pending") # passed, failed, timeout, pending
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="solutions")
    question = relationship("Question", back_populates="solutions")
