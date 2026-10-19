import pytest
import asyncio
from app.models.assignment import Assignment, Question
from app.models.job import Job, GeneratedSolution
from app.workers.tasks import execute_job_pipeline
from app.services.github.publishing_service import PublishingService

@pytest.mark.asyncio
async def test_end_to_end_assignment_job_pipeline(db_session):
    # 1. Create an assignment with 2 questions
    assignment = Assignment(
        title="Week 3 Algorithms",
        week_module="Week 3",
        language="cpp",
        status="awaiting_review"
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)

    q1 = Question(
        assignment_id=assignment.id,
        question_number=1,
        title="Sum of Two Numbers",
        description="Read two integers a and b from stdin and output their sum.",
        constraints="1 <= a, b <= 10^9",
        target_filename="question_01.cpp",
        sample_inputs=["10 20", "100 250"],
        sample_outputs=["30", "350"],
        is_approved=True
    )
    q2 = Question(
        assignment_id=assignment.id,
        question_number=2,
        title="Check Even or Odd",
        description="Read an integer n from stdin. Output 'Even' if even, 'Odd' if odd.",
        constraints="1 <= n <= 10^9",
        target_filename="question_02.cpp",
        sample_inputs=["4", "7"],
        sample_outputs=["Even", "Odd"],
        is_approved=True
    )
    db_session.add(q1)
    db_session.add(q2)
    db_session.commit()

    # 2. Create and start Job
    job = Job(
        assignment_id=assignment.id,
        status="queued",
        current_step="Queued for processing"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # 3. Execute the full pipeline asynchronously
    await execute_job_pipeline(job.id, db_session=db_session)

    # 4. Refresh and assert outcomes
    db_session.refresh(job)
    assert job.status in ("ready_to_publish", "published")
    assert job.progress_percent >= 80
    assert job.target_branch.startswith("autoryx/assignment-")

    # Verify both questions generated solutions
    solutions = db_session.query(GeneratedSolution).filter(GeneratedSolution.job_id == job.id).all()
    assert len(solutions) == 2

    for sol in solutions:
        assert sol.compilation_status == "passed"
        assert sol.validation_status == "passed"
        assert sol.tests_total >= 1
        assert sol.tests_passed == sol.tests_total
        assert len(sol.source_code) > 0
        assert not sol.source_code.startswith("```") # Markdown fences stripped

    # 5. Verify publish preview passes all strict safety rules
    preview = PublishingService.preview_changes(
        assignment_id=assignment.id,
        job_id=job.id,
        assignment_title=assignment.title,
        language=assignment.language,
        solutions=[
            {
                "filename": s.filename,
                "source_code": s.source_code,
                "language": s.language,
                "validation_status": s.validation_status,
                "tests_passed": s.tests_passed,
                "tests_total": s.tests_total
            }
            for s in solutions
        ],
        week_module=assignment.week_module
    )

    assert preview["safety_checks_passed"] is True
    assert len(preview["warnings"]) == 0
    assert len(preview["proposed_files"]) >= 4 # 2 source files + README + report.json + latest_run.json
    for pf in preview["proposed_files"]:
        assert pf["relative_path"].startswith("STEP_Agent_Assignments/")
