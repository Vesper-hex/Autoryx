from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.config import settings
from app.models.job import Job, GeneratedSolution
from app.models.assignment import Assignment
from app.models.activity import Setting
from app.schemas.github import GitHubStatusResponse, PublishPreviewResponse, PublishActionRequest, PublishResultResponse
from app.services.github.github_client import GitHubClient
from app.services.github.publishing_service import PublishingService
from app.services.github.repo_safety import RepositorySafetyError
from app.core.logging import logger

router = APIRouter(prefix="/repository", tags=["Repository"])

def get_token(db: Session) -> Optional[str]:
    setting = db.query(Setting).filter(Setting.key == "github_token").first()
    if setting and setting.value:
        return setting.value
    return settings.GITHUB_TOKEN

@router.get("/status", response_model=GitHubStatusResponse)
async def get_github_status(db: Session = Depends(get_db)):
    """Checks remote repository reachability, branch status, and rate limit."""
    token = get_token(db)
    client = GitHubClient(token=token)
    status_data = await client.get_repo_status()
    return status_data

@router.get("/contents")
async def get_repo_contents(path: str = Query("", description="Folder path inside repo"), db: Session = Depends(get_db)):
    """Lists repository files/directories at the given path."""
    token = get_token(db)
    client = GitHubClient(token=token)
    items = await client.get_contents(path=path)
    return items

@router.get("/file")
async def get_file_content(path: str = Query(..., description="File path to fetch"), ref: str = Query("main"), db: Session = Depends(get_db)):
    """Retrieves raw content of a text file from the repository."""
    token = get_token(db)
    client = GitHubClient(token=token)
    content = await client.get_raw_file(path=path, ref=ref)
    if content is None:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return {"path": path, "ref": ref, "content": content}

@router.get("/preview/{job_id}", response_model=PublishPreviewResponse)
def get_publish_preview(job_id: str, db: Session = Depends(get_db)):
    """
    Returns proposed file change summary before publishing to GitHub.
    Enforces strict isolation under STEP_Agent_Assignments/.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    assignment = db.query(Assignment).filter(Assignment.id == job.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    solutions = db.query(GeneratedSolution).filter(GeneratedSolution.job_id == job.id).all()
    if not solutions:
        raise HTTPException(status_code=400, detail="No generated solutions found for this job.")

    sol_dicts = [
        {
            "filename": s.filename,
            "source_code": s.source_code,
            "language": s.language,
            "compilation_status": s.compilation_status,
            "validation_status": s.validation_status,
            "tests_passed": s.tests_passed,
            "tests_total": s.tests_total,
            "repair_attempts": s.repair_attempts,
            "test_results": s.test_results
        }
        for s in solutions
    ]

    preview = PublishingService.preview_changes(
        assignment_id=assignment.id,
        job_id=job.id,
        assignment_title=assignment.title,
        language=assignment.language,
        solutions=sol_dicts,
        week_module=assignment.week_module
    )
    return preview

@router.post("/publish", response_model=PublishResultResponse)
async def publish_job(req: PublishActionRequest, db: Session = Depends(get_db)):
    """
    Publishes verified assignment files strictly to a dedicated branch on the target GitHub repository.
    Verifies remote commit SHA and avoids duplicate publishing.
    """
    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    assignment = db.query(Assignment).filter(Assignment.id == job.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    solutions = db.query(GeneratedSolution).filter(GeneratedSolution.job_id == job.id).all()
    if not solutions:
        raise HTTPException(status_code=400, detail="No generated solutions found for this job.")

    token = get_token(db)
    if not token:
        raise HTTPException(
            status_code=400,
            detail="GitHub token is required to publish. Please configure a Personal Access Token in Settings."
        )

    sol_dicts = [
        {
            "filename": s.filename,
            "source_code": s.source_code,
            "language": s.language,
            "compilation_status": s.compilation_status,
            "validation_status": s.validation_status,
            "tests_passed": s.tests_passed,
            "tests_total": s.tests_total,
            "repair_attempts": s.repair_attempts,
            "test_results": s.test_results
        }
        for s in solutions
    ]

    job.status = "publishing"
    db.commit()

    try:
        result = await PublishingService.publish_to_github(
            assignment_id=assignment.id,
            job_id=job.id,
            assignment_title=assignment.title,
            language=assignment.language,
            solutions=sol_dicts,
            week_module=assignment.week_module,
            commit_message=req.commit_message,
            token=token
        )

        job.commit_sha = result["commit_sha"]
        job.commit_url = result["commit_url"]
        job.target_branch = result["branch_name"]
        job.status = "published"
        job.current_step = f"Published commit {result['commit_sha'][:7]} to {result['branch_name']}"
        db.commit()

        return result
    except RepositorySafetyError as rse:
        job.status = "ready_to_publish"
        job.error_message = f"Safety error: {str(rse)}"
        db.commit()
        raise HTTPException(status_code=422, detail=str(rse))
    except Exception as e:
        logger.error(f"Publishing error: {e}", exc_info=True)
        job.status = "ready_to_publish"
        job.error_message = f"Publishing failed: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")
