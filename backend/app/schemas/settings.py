from pydantic import BaseModel
from typing import Optional, Dict, Any

class SettingsResponse(BaseModel):
    github_owner: str
    github_repo: str
    github_default_branch: str
    target_isolated_dir: str
    has_github_token: bool
    github_token_masked: Optional[str] = None
    
    ai_provider: str  # "gemini", "openai", "mock"
    gemini_model: str
    has_gemini_key: bool
    gemini_key_masked: Optional[str] = None
    
    openai_model: str
    has_openai_key: bool
    openai_key_masked: Optional[str] = None
    
    max_repair_attempts: int
    auto_publish_branch: bool
    compilation_timeout_seconds: int
    execution_timeout_seconds: int
    
    worker_health: str
    database_status: str

class SettingsUpdateRequest(BaseModel):
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    github_default_branch: Optional[str] = None
    github_token: Optional[str] = None
    
    ai_provider: Optional[str] = None
    gemini_key: Optional[str] = None
    gemini_model: Optional[str] = None
    openai_key: Optional[str] = None
    openai_model: Optional[str] = None
    
    max_repair_attempts: Optional[int] = None
    auto_publish_branch: Optional[bool] = None
