from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class TestResultDetail(BaseModel):
    test_number: int
    input: str
    expected_output: str
    actual_output: Optional[str] = None
    passed: bool
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

class GeneratedSolutionResponse(BaseModel):
    id: str
    job_id: str
    question_id: str
    filename: str
    source_code: str
    language: str
    compilation_status: str
    compiler_output: Optional[str] = None
    tests_total: int
    tests_passed: int
    test_results: List[Dict[str, Any]] = []
    repair_attempts: int
    repair_history: List[Dict[str, Any]] = []
    validation_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    assignment_id: str
    auto_publish: Optional[bool] = None

class JobResponse(BaseModel):
    id: str
    assignment_id: str
    status: str
    current_step: str
    progress_percent: int
    target_branch: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_url: Optional[str] = None
    output_directory: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    finished_at: Optional[datetime] = None
    solutions: List[GeneratedSolutionResponse] = []

    class Config:
        from_attributes = True
