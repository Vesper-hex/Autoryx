import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.logging import logger
from app.models.assignment import Assignment, Question
from app.models.activity import ActivityLog
from app.schemas.assignment import AssignmentResponse, TextExtractionRequest
from app.schemas.question import QuestionResponse, QuestionUpdate
from app.services.ingestion.document_parser import DocumentParser
from app.services.extraction.question_extractor import QuestionExtractor

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.post("/upload", response_model=AssignmentResponse)
async def upload_assignment_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    week_module: Optional[str] = Form(None),
    language: str = Form("cpp"),
    db: Session = Depends(get_db)
):
    """
    Accepts assignment PDF, TXT, or image upload, parses readable content,
    extracts individual questions, and stores a draft assignment for review.
    """
    contents = await file.read()
    file_size = len(contents)

    # Validate upload
    is_valid, err_msg = DocumentParser.validate_upload(file.filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=err_msg)

    # Save to safe private storage
    upload_name = f"{Path(file.filename).stem}_{os.urandom(4).hex()}{Path(file.filename).suffix}"
    saved_path = settings.UPLOAD_DIR / upload_name
    with open(saved_path, "wb") as f:
        f.write(contents)

    # Extract text
    try:
        raw_text = DocumentParser.parse_file(saved_path)
    except Exception as e:
        logger.error(f"Failed to parse uploaded document: {e}")
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {str(e)}")

    assignment_title = title.strip() if title and title.strip() else Path(file.filename).stem

    # Create Assignment
    assignment = Assignment(
        title=assignment_title,
        week_module=week_module.strip() if week_module and week_module.strip() else None,
        language=language.lower().strip(),
        source_filename=file.filename,
        raw_content=raw_text,
        status="awaiting_review"
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    # Extract questions
    extracted_questions = QuestionExtractor.extract_questions_rule_based(raw_text, language)
    for q_data in extracted_questions:
        q = Question(
            assignment_id=assignment.id,
            question_number=q_data["question_number"],
            title=q_data["title"],
            description=q_data["description"],
            constraints=q_data.get("constraints"),
            target_filename=q_data["target_filename"],
            sample_inputs=q_data.get("sample_inputs", []),
            sample_outputs=q_data.get("sample_outputs", []),
            is_approved=True
        )
        db.add(q)

    # Log activity
    log = ActivityLog(
        assignment_id=assignment.id,
        event_type="UPLOAD_RECEIVED",
        message=f"Received upload '{file.filename}', extracted {len(extracted_questions)} question(s)",
        severity="info"
    )
    db.add(log)
    db.commit()
    db.refresh(assignment)

    return assignment

@router.post("/text", response_model=AssignmentResponse)
def create_assignment_from_text(req: TextExtractionRequest, db: Session = Depends(get_db)):
    """Creates an assignment directly from pasted assignment text."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Assignment text cannot be empty.")

    assignment = Assignment(
        title=req.title.strip(),
        week_module=req.week_module.strip() if req.week_module else None,
        language=req.language.lower().strip(),
        source_filename="pasted_text.txt",
        raw_content=req.text,
        status="awaiting_review"
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    extracted_questions = QuestionExtractor.extract_questions_rule_based(req.text, req.language)
    for q_data in extracted_questions:
        q = Question(
            assignment_id=assignment.id,
            question_number=q_data["question_number"],
            title=q_data["title"],
            description=q_data["description"],
            constraints=q_data.get("constraints"),
            target_filename=q_data["target_filename"],
            sample_inputs=q_data.get("sample_inputs", []),
            sample_outputs=q_data.get("sample_outputs", []),
            is_approved=True
        )
        db.add(q)

    log = ActivityLog(
        assignment_id=assignment.id,
        event_type="UPLOAD_RECEIVED",
        message=f"Created assignment '{assignment.title}' from pasted text ({len(extracted_questions)} question(s))",
        severity="info"
    )
    db.add(log)
    db.commit()
    db.refresh(assignment)

    return assignment

@router.get("", response_model=List[AssignmentResponse])
def list_assignments(db: Session = Depends(get_db)):
    """Lists all assignments ordered by most recent."""
    return db.query(Assignment).order_by(Assignment.created_at.desc()).all()

@router.get("/{id}", response_model=AssignmentResponse)
def get_assignment(id: str, db: Session = Depends(get_db)):
    """Retrieves an assignment by ID with all questions."""
    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return assignment

@router.put("/{id}/questions/{q_id}", response_model=QuestionResponse)
def update_question(id: str, q_id: str, req: QuestionUpdate, db: Session = Depends(get_db)):
    """Updates an extracted question's title, filename, constraints, or approval status."""
    q = db.query(Question).filter(Question.id == q_id, Question.assignment_id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    if req.title is not None:
        q.title = req.title.strip()
    if req.description is not None:
        q.description = req.description
    if req.constraints is not None:
        q.constraints = req.constraints
    if req.target_filename is not None:
        from app.services.github.repo_safety import RepoSafetyValidator
        q.target_filename = RepoSafetyValidator.validate_filename(req.target_filename.strip())
    if req.sample_inputs is not None:
        q.sample_inputs = req.sample_inputs
    if req.sample_outputs is not None:
        q.sample_outputs = req.sample_outputs
    if req.is_approved is not None:
        q.is_approved = req.is_approved

    db.commit()
    db.refresh(q)
    return q

@router.delete("/{id}")
def delete_assignment(id: str, db: Session = Depends(get_db)):
    """Deletes an assignment and associated records."""
    assignment = db.query(Assignment).filter(Assignment.id == id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully"}
