from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GitHubStatusResponse(BaseModel):
    is_connected: bool
    owner: str
    repo: str
    default_branch: str
    target_isolated_dir: str
    message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None

class ProposedFileChange(BaseModel):
    relative_path: str
    action: str  # "create", "modify", "skip"
    size_bytes: int
    validation_status: str

class PublishPreviewResponse(BaseModel):
    job_id: str
    target_branch: str
    target_isolated_dir: str
    proposed_files: List[ProposedFileChange]
    validation_summary: Dict[str, Any]
    safety_checks_passed: bool
    warnings: List[str] = []

class PublishActionRequest(BaseModel):
    job_id: str
    commit_message: Optional[str] = None
    create_pull_request: bool = False

class PublishResultResponse(BaseModel):
    success: bool
    job_id: str
    branch_name: str
    commit_sha: Optional[str] = None
    commit_url: Optional[str] = None
    pull_request_url: Optional[str] = None
    published_files: List[str] = []
    error: Optional[str] = None
