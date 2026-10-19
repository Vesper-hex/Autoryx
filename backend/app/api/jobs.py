from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.assignment import Assignment, Question
from app.models.job import Job, GeneratedSolution
from app.schemas.job import JobCreate, JobResponse
from app.workers.job_queue import PersistentJobQueue
from app.core.logging import logger

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse)
def create_job(req: JobCreate, db: Session = Depends(get_db)):
    """
    Creates and enqueues a background assignment generation and validation job.
    Processing continues in the background even if client disconnects.
    """
    assignment = db.query(Assignment).filter(Assignment.id == req.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    # Check for approved questions
    approved_count = db.query(Question).filter(
        Question.assignment_id == assignment.id,
        Question.is_approved == True
    ).count()

    if approved_count == 0:
        raise HTTPException(status_code=400, detail="Cannot start job: no approved questions.")

    # Create new Job
    job = Job(
        assignment_id=assignment.id,
        status="queued",
        current_step="Queued for processing",
        progress_percent=0
    )
    db.add(job)
    assignment.status = "in_progress"
    db.commit()
    db.refresh(job)

    # Enqueue in persistent queue
    PersistentJobQueue.enqueue(job.id)

    return job

@router.get("/{id}", response_model=JobResponse)
def get_job(id: str, db: Session = Depends(get_db)):
    """Retrieves current job status, solutions, compiler output, and validation results."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.get("/assignment/{assignment_id}/latest", response_model=Optional[JobResponse])
def get_latest_job_for_assignment(assignment_id: str, db: Session = Depends(get_db)):
    """Retrieves the most recent job for a specific assignment."""
    job = db.query(Job).filter(Job.assignment_id == assignment_id).order_by(Job.created_at.desc()).first()
    return job

@router.post("/{id}/cancel", response_model=JobResponse)
def cancel_job(id: str, db: Session = Depends(get_db)):
    """Safely cancels an active or queued job."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status in ("published", "completed", "failed"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status '{job.status}'.")

    job.status = "cancelled"
    job.current_step = "Job cancelled by user"
    job.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job

@router.post("/{id}/retry", response_model=JobResponse)
def retry_job(id: str, db: Session = Depends(get_db)):
    """Retries a failed or completed job."""
    old_job = db.query(Job).filter(Job.id == id).first()
    if not old_job:
        raise HTTPException(status_code=404, detail="Job not found.")

    new_job = Job(
        assignment_id=old_job.assignment_id,
        status="queued",
        current_step="Re-queued for execution",
        progress_percent=0
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    PersistentJobQueue.enqueue(new_job.id)
    return new_job
