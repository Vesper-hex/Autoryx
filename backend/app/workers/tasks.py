import asyncio
from datetime import datetime
from typing import Optional
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import logger
from app.models.assignment import Assignment, Question
from app.models.job import Job, GeneratedSolution
from app.models.activity import ActivityLog, Setting
from app.services.generation.solution_generator import SolutionGenerator
from app.services.validation.repair_service import RepairService
from app.services.github.publishing_service import PublishingService

def log_job_activity(db, job_id: str, assignment_id: str, event_type: str, message: str, severity: str = "info", meta: dict = None):
    activity = ActivityLog(
        job_id=job_id,
        assignment_id=assignment_id,
        event_type=event_type,
        message=message,
        severity=severity,
        metadata_json=meta or {}
    )
    db.add(activity)
    db.commit()
    logger.info(f"[{event_type}] {message}")

def get_db_setting(db, key: str, default: Optional[str] = None) -> Optional[str]:
    row = db.query(Setting).filter(Setting.key == key).first()
    if row and row.value is not None:
        return row.value
    return default

def run_job_sync(job_id: str):
    """
    Synchronous worker task wrapper that runs the async job pipeline.
    Suitable for running inside worker processes or background threads.
    """
    asyncio.run(execute_job_pipeline(job_id))

async def execute_job_pipeline(job_id: str, db_session = None):
    """
    Core state-machine workflow executor for an Autoryx assignment job:
    Generating -> Compiling -> Testing -> Repairing -> Ready to Publish -> Publishing -> Published
    """
    from app.core.database import init_db
    init_db()

    should_close = False
    if db_session:
        db = db_session
    else:
        db = SessionLocal()
        should_close = True

    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found.")
            return

        if job.status == "cancelled":
            logger.info(f"Job {job_id} was cancelled before execution.")
            return

        assignment = db.query(Assignment).filter(Assignment.id == job.assignment_id).first()
        if not assignment:
            job.status = "failed"
            job.error_message = "Associated assignment not found."
            db.commit()
            return

        # Fetch provider & token settings from DB or config
        ai_provider = get_db_setting(db, "ai_provider", settings.AI_PROVIDER)
        gemini_key = get_db_setting(db, "gemini_key", settings.GEMINI_API_KEY)
        openai_key = get_db_setting(db, "openai_key", settings.OPENAI_API_KEY)
        github_token = get_db_setting(db, "github_token", settings.GITHUB_TOKEN)
        auto_pub_str = get_db_setting(db, "auto_publish_branch", "false")
        auto_publish = auto_pub_str.lower() in ("true", "1") or settings.AUTO_PUBLISH_BRANCH

        # Fetch approved questions
        questions = db.query(Question).filter(
            Question.assignment_id == assignment.id,
            Question.is_approved == True
        ).order_by(Question.question_number.asc()).all()

        if not questions:
            job.status = "failed"
            job.error_message = "No approved questions found for this assignment."
            db.commit()
            log_job_activity(db, job.id, assignment.id, "JOB_FAILED", "No approved questions to generate", severity="error")
            return

        # Phase 1: Generation
        job.status = "generating"
        job.current_step = f"Generating solution code ({len(questions)} questions)"
        job.progress_percent = 20
        db.commit()
        log_job_activity(db, job.id, assignment.id, "GENERATION_STARTED", f"Generating code for {len(questions)} question(s) in {assignment.language.upper()}")

        # Clean any old solutions for this job
        db.query(GeneratedSolution).filter(GeneratedSolution.job_id == job.id).delete()
        db.commit()

        api_key = gemini_key if ai_provider == "gemini" else openai_key
        solutions_data = []

        total_q = len(questions)
        for idx, q in enumerate(questions, 1):
            if job.status == "cancelled":
                break

            # 1. Generate code
            code = SolutionGenerator.generate(
                question_title=q.title,
                question_description=q.description,
                language=assignment.language,
                constraints=q.constraints,
                sample_inputs=q.sample_inputs,
                sample_outputs=q.sample_outputs,
                provider_name=ai_provider,
                api_key=api_key
            )
            log_job_activity(db, job.id, assignment.id, "FILE_CREATED", f"Generated source file '{q.target_filename}'")

            # 2. Compile & Validate with Automated Repair
            job.status = "testing"
            job.current_step = f"Compiling and testing {q.target_filename} (Q{q.question_number})"
            job.progress_percent = 20 + int((idx / total_q) * 50)
            db.commit()

            val_result = RepairService.validate_and_repair(
                initial_code=code,
                filename=q.target_filename,
                language=assignment.language,
                question_description=q.description,
                sample_inputs=q.sample_inputs or [],
                sample_outputs=q.sample_outputs or [],
                provider_name=ai_provider,
                api_key=api_key
            )

            if val_result["repair_attempts"] > 0:
                log_job_activity(
                    db, job.id, assignment.id, "REPAIR_ATTEMPTED",
                    f"Repaired '{q.target_filename}' ({val_result['repair_attempts']} attempts, final status: {val_result['validation_status']})",
                    severity="warning" if val_result["validation_status"] != "passed" else "success"
                )
            else:
                log_job_activity(
                    db, job.id, assignment.id, "COMPILATION_COMPLETED",
                    f"Validated '{q.target_filename}' - status: {val_result['validation_status']} ({val_result['tests_passed']}/{val_result['tests_total']} tests passed)"
                )

            sol = GeneratedSolution(
                job_id=job.id,
                question_id=q.id,
                filename=q.target_filename,
                source_code=val_result["final_code"],
                language=assignment.language,
                compilation_status=val_result["compilation_status"],
                compiler_output=val_result["compiler_output"],
                tests_total=val_result["tests_total"],
                tests_passed=val_result["tests_passed"],
                test_results=val_result["test_results"],
                repair_attempts=val_result["repair_attempts"],
                repair_history=val_result["repair_history"],
                validation_status=val_result["validation_status"]
            )
            db.add(sol)
            db.commit()

            solutions_data.append({
                "filename": q.target_filename,
                "source_code": val_result["final_code"],
                "language": assignment.language,
                "compilation_status": val_result["compilation_status"],
                "validation_status": val_result["validation_status"],
                "tests_passed": val_result["tests_passed"],
                "tests_total": val_result["tests_total"],
                "repair_attempts": val_result["repair_attempts"],
                "test_results": val_result["test_results"]
            })

        # Phase 3: Assembly & Output Organization
        job.target_branch = PublishingService.generate_branch_name(job.id)
        job.output_directory = f"{settings.TARGET_ISOLATED_DIR}/assignments/{assignment.id}"
        job.progress_percent = 80
        job.status = "ready_to_publish"
        job.current_step = "All solutions compiled and verified. Ready for GitHub publishing."
        db.commit()
        log_job_activity(db, job.id, assignment.id, "VALIDATION_COMPLETED", "All solutions generated and verified under sandbox.")

        # Phase 4: Auto-Publish if enabled and token present
        if auto_publish and github_token:
            job.status = "publishing"
            job.current_step = f"Publishing verified files to dedicated branch {job.target_branch}"
            db.commit()
            log_job_activity(db, job.id, assignment.id, "BRANCH_CREATED", f"Publishing to dedicated branch '{job.target_branch}'")

            try:
                pub_result = await PublishingService.publish_to_github(
                    assignment_id=assignment.id,
                    job_id=job.id,
                    assignment_title=assignment.title,
                    language=assignment.language,
                    solutions=solutions_data,
                    week_module=assignment.week_module,
                    token=github_token
                )
                job.commit_sha = pub_result["commit_sha"]
                job.commit_url = pub_result["commit_url"]
                job.status = "published"
                job.current_step = "Successfully published to GitHub."
                job.progress_percent = 100
                job.finished_at = datetime.utcnow()
                db.commit()
                log_job_activity(
                    db, job.id, assignment.id, "PUSH_COMPLETED",
                    f"Successfully pushed commit {pub_result['commit_sha'][:7]} to {job.target_branch}",
                    severity="success"
                )
            except Exception as pe:
                logger.error(f"Publishing failed: {pe}")
                job.status = "ready_to_publish"
                job.error_message = f"Publishing failed: {str(pe)}. Local work preserved."
                db.commit()
                log_job_activity(db, job.id, assignment.id, "PUSH_FAILED", f"Publishing failed: {str(pe)}", severity="error")

    except Exception as e:
        logger.error(f"Job execution failed with unexpected error: {e}", exc_info=True)
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.finished_at = datetime.utcnow()
            db.commit()
            log_job_activity(db, job.id, job.assignment_id, "JOB_FAILED", f"Job failed: {str(e)}", severity="error")
    finally:
        if should_close:
            db.close()
