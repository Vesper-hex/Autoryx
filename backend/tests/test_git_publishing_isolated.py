import os
import subprocess
import tempfile
from pathlib import Path
from app.services.organization.output_organizer import OutputOrganizer
from app.services.github.repo_safety import RepoSafetyValidator

def test_isolated_git_staging_and_branch_in_temp_repo():
    """
    Simulates the remote repository layout in an isolated temporary git repo.
    Verifies that staging and committing strictly touches ONLY STEP_Agent_Assignments/
    and preserves Week 1/, Week 2/, and root files completely.
    """
    with tempfile.TemporaryDirectory() as temp_repo_dir:
        repo_path = Path(temp_repo_dir)

        # 1. Initialize local Git repo mimicking Highorder-Thinking/Step_semester_3
        subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "agent@autoryx.local"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.name", "Autoryx Agent"], cwd=repo_path, check=True)

        # Create Week 1 and Week 2 and root files
        (repo_path / "Week 1").mkdir()
        (repo_path / "Week 1" / "Q1.java").write_text("// Existing Week 1 solution", encoding="utf-8")
        
        (repo_path / "Week 2").mkdir()
        (repo_path / "Week 2" / "Q1.java").write_text("// Existing Week 2 solution", encoding="utf-8")
        
        (repo_path / "README.md").write_text("# STEP Semester 3\n\nOriginal README", encoding="utf-8")
        (repo_path / ".gitignore").write_text("*.class\n*.exe\n", encoding="utf-8")

        # Initial commit on main
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit with Week 1 and Week 2"], cwd=repo_path, check=True, capture_output=True)

        # Record commit hash and file hashes of Week 1 and Week 2
        week1_content_before = (repo_path / "Week 1" / "Q1.java").read_text(encoding="utf-8")
        week2_content_before = (repo_path / "Week 2" / "Q1.java").read_text(encoding="utf-8")
        readme_before = (repo_path / "README.md").read_text(encoding="utf-8")

        # 2. Assemble new assignment files via OutputOrganizer
        job_id = "job_test_456"
        branch_name = f"autoryx/assignment-{job_id}"
        RepoSafetyValidator.validate_branch_name(branch_name)

        solutions = [
            {
                "filename": "question_01.cpp",
                "source_code": "#include <iostream>\nint main(){ std::cout << 42 << std::endl; return 0; }",
                "language": "cpp",
                "validation_status": "passed",
                "tests_passed": 1,
                "tests_total": 1,
                "repair_attempts": 0
            }
        ]

        file_map = OutputOrganizer.assemble_assignment_files(
            assignment_id="asgn_sample",
            job_id=job_id,
            assignment_title="Sample Math Assignment",
            language="cpp",
            solutions=solutions,
            week_module="Week 3",
            branch_name=branch_name
        )

        # 3. Create dedicated branch
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True, capture_output=True)

        # 4. Write files strictly to their allowed relative paths
        staged_paths = []
        for rel_path, content in file_map.items():
            # Validate safety before writing or staging
            clean_rel = RepoSafetyValidator.validate_staging_path(rel_path, "STEP_Agent_Assignments")
            full_path = repo_path / clean_rel
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            staged_paths.append(str(clean_rel).replace("\\", "/"))

        # 5. Stage ONLY the explicitly allowed paths (NEVER git add .)
        for path in staged_paths:
            subprocess.run(["git", "add", path], cwd=repo_path, check=True, capture_output=True)

        # 6. Commit
        commit_res = subprocess.run(
            ["git", "commit", "-m", f"feat(autoryx): deliver assignment [{job_id}]"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        # Verify commit SHA
        sha_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_path, check=True, capture_output=True, text=True)
        commit_sha = sha_res.stdout.strip()
        assert len(commit_sha) == 40

        # Verify git status has no untracked or staged files
        status_res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, check=True, capture_output=True, text=True)
        assert status_res.stdout.strip() == ""

        # 7. CRITICAL SAFETY VERIFICATION: Week 1, Week 2, and root README must be completely unchanged!
        assert (repo_path / "Week 1" / "Q1.java").read_text(encoding="utf-8") == week1_content_before
        assert (repo_path / "Week 2" / "Q1.java").read_text(encoding="utf-8") == week2_content_before
        assert (repo_path / "README.md").read_text(encoding="utf-8") == readme_before

        # Check diff against main: diff must ONLY contain STEP_Agent_Assignments/
        diff_res = subprocess.run(
            ["git", "diff", "--name-only", "main", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        changed_files = [f.strip().replace("\\", "/") for f in diff_res.stdout.splitlines() if f.strip()]
        for changed_file in changed_files:
            assert changed_file.startswith("STEP_Agent_Assignments/"), f"Unauthorized file changed: {changed_file}"
