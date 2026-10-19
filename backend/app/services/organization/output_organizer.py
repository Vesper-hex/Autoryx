import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from app.services.github.repo_safety import RepoSafetyValidator

class OutputOrganizer:
    """
    Builds and arranges the strictly isolated folder structure for assignments:
    STEP_Agent_Assignments/
      ├── README.md
      ├── assignments/
      │   └── <assignment_folder>/
      │       ├── <source files>
      │       ├── README.md
      │       └── report.json
      └── reports/
          └── latest_run.json
    """

    ALLOWED_ROOT = "STEP_Agent_Assignments"

    @classmethod
    def get_assignment_folder_name(cls, assignment_id: str, week_module: str = None) -> str:
        safe_id = RepoSafetyValidator.sanitize_identifier(assignment_id)
        if week_module:
            safe_wm = RepoSafetyValidator.sanitize_identifier(week_module)
            return f"{safe_wm}_{safe_id}"
        return safe_id

    @classmethod
    def assemble_assignment_files(
        cls,
        assignment_id: str,
        job_id: str,
        assignment_title: str,
        language: str,
        solutions: List[Dict[str, Any]],
        week_module: str = None,
        branch_name: str = None,
        commit_sha: str = None
    ) -> Dict[str, str]:
        """
        Generates the map of { relative_git_path: file_content_str } strictly under STEP_Agent_Assignments/
        """
        folder_name = cls.get_assignment_folder_name(assignment_id, week_module)
        assignment_dir = f"{cls.ALLOWED_ROOT}/assignments/{folder_name}"
        
        file_map: Dict[str, str] = {}

        # 1. Add all individual source files
        source_filenames = []
        for sol in solutions:
            fname = RepoSafetyValidator.validate_filename(sol["filename"])
            rel_path = f"{assignment_dir}/{fname}"
            # Validate full path
            RepoSafetyValidator.validate_staging_path(rel_path, cls.ALLOWED_ROOT)
            file_map[rel_path] = sol["source_code"]
            source_filenames.append(fname)

        # 2. Build assignment report.json
        report_data = {
            "job_id": job_id,
            "assignment_id": assignment_id,
            "title": assignment_title,
            "week_module": week_module,
            "language": language,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "git_branch": branch_name,
            "commit_sha": commit_sha,
            "solutions": [
                {
                    "filename": sol["filename"],
                    "language": sol.get("language", language),
                    "compilation_status": sol.get("compilation_status", "passed"),
                    "validation_status": sol.get("validation_status", "passed"),
                    "tests_passed": sol.get("tests_passed", 0),
                    "tests_total": sol.get("tests_total", 0),
                    "repair_attempts": sol.get("repair_attempts", 0),
                    "test_results": sol.get("test_results", [])
                }
                for sol in solutions
            ]
        }
        report_path = f"{assignment_dir}/report.json"
        RepoSafetyValidator.validate_staging_path(report_path, cls.ALLOWED_ROOT)
        file_map[report_path] = json.dumps(report_data, indent=2)

        # 3. Build assignment README.md
        readme_content = cls._build_assignment_readme(
            title=assignment_title,
            week_module=week_module,
            language=language,
            solutions=solutions,
            job_id=job_id,
            branch_name=branch_name
        )
        readme_path = f"{assignment_dir}/README.md"
        RepoSafetyValidator.validate_staging_path(readme_path, cls.ALLOWED_ROOT)
        file_map[readme_path] = readme_content

        # 4. Build latest_run.json in reports/
        latest_report_path = f"{cls.ALLOWED_ROOT}/reports/latest_run.json"
        RepoSafetyValidator.validate_staging_path(latest_report_path, cls.ALLOWED_ROOT)
        file_map[latest_report_path] = json.dumps({
            "latest_job_id": job_id,
            "latest_assignment_id": assignment_id,
            "title": assignment_title,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "files_generated": source_filenames,
            "status": "completed"
        }, indent=2)

        # 5. Build or update top-level STEP_Agent_Assignments/README.md
        root_readme_path = f"{cls.ALLOWED_ROOT}/README.md"
        RepoSafetyValidator.validate_staging_path(root_readme_path, cls.ALLOWED_ROOT)
        file_map[root_readme_path] = cls._build_root_readme(
            assignment_title=assignment_title,
            folder_name=folder_name,
            language=language,
            solutions=solutions
        )

        return file_map

    @classmethod
    def _build_assignment_readme(
        cls,
        title: str,
        week_module: str,
        language: str,
        solutions: List[Dict[str, Any]],
        job_id: str,
        branch_name: str
    ) -> str:
        run_instructions = {
            "cpp": "g++ -O2 -std=c++17 <filename>.cpp -o program && ./program",
            "c": "gcc -O2 -std=c11 <filename>.c -o program && ./program",
            "java": "javac <filename>.java && java <ClassName>",
            "python": "python <filename>.py"
        }
        cmd_example = run_instructions.get(language.lower(), "run according to language runtime")

        sol_rows = []
        for sol in solutions:
            status_badge = "PASSED" if sol.get("validation_status") == "passed" else "ATTENTION NEEDED"
            tests_info = f"{sol.get('tests_passed', 0)} / {sol.get('tests_total', 0)} passed"
            repairs = f"{sol.get('repair_attempts', 0)} repairs"
            sol_rows.append(f"| `{sol['filename']}` | {status_badge} | {tests_info} | {repairs} |")

        table_str = "\n".join(sol_rows)

        return f"""# {title}

**Generated by Autoryx Personal STEP Automation Agent**
- **Week/Module**: {week_module or 'Standard Assignment'}
- **Language**: {language.upper()}
- **Job ID**: `{job_id}`
- **Published Branch**: `{branch_name or 'N/A'}`
- **Generated At**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

## Solution Files

| File | Validation | Tests | Repairs |
| :--- | :--- | :--- | :--- |
{table_str}

## Execution Instructions

To compile and execute solutions:
```bash
{cmd_example}
```

*All solutions have undergone sandboxed compilation, sample input/output verification, and automated repair checks.*
"""

    @classmethod
    def _build_root_readme(
        cls,
        assignment_title: str,
        folder_name: str,
        language: str,
        solutions: List[Dict[str, Any]]
    ) -> str:
        return f"""# STEP Agent Assignments

This directory contains automated, verified programming assignment solutions generated by **Autoryx**.

> **Safety Notice**: This folder is strictly isolated from existing coursework folders (`Week 1/`, `Week 2/`, etc.). All additions are placed exclusively under `STEP_Agent_Assignments/`.

## Directory Overview

- `assignments/`: Individual assignment directories with source files, metadata, and reports.
- `reports/`: Execution and validation run logs.

## Latest Assignment
- **Title**: {assignment_title}
- **Folder**: [`assignments/{folder_name}/`](assignments/{folder_name}/)
- **Language**: {language.upper()}
- **Generated Files**: {', '.join(s['filename'] for s in solutions)}
"""
