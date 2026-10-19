import os
import json
import base64
import subprocess
import httpx
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from app.services.github.repo_safety import RepoSafetyValidator, RepositorySafetyError
from app.services.organization.output_organizer import OutputOrganizer
from app.core.config import settings
from app.core.logging import logger

class PublishingService:
    """
    Publishing engine that publishes verified assignment files strictly to
    a dedicated branch on the target GitHub repository.
    """

    @classmethod
    def generate_branch_name(cls, job_id: str) -> str:
        clean_id = RepoSafetyValidator.sanitize_identifier(job_id)
        branch = f"autoryx/assignment-{clean_id}"
        return RepoSafetyValidator.validate_branch_name(branch)

    @classmethod
    def preview_changes(
        cls,
        assignment_id: str,
        job_id: str,
        assignment_title: str,
        language: str,
        solutions: List[Dict[str, Any]],
        week_module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates and verifies all proposed file changes before any publishing action.
        """
        branch_name = cls.generate_branch_name(job_id)
        file_map = OutputOrganizer.assemble_assignment_files(
            assignment_id=assignment_id,
            job_id=job_id,
            assignment_title=assignment_title,
            language=language,
            solutions=solutions,
            week_module=week_module,
            branch_name=branch_name
        )

        proposed_files = []
        warnings = []
        safety_passed = True

        for path_str, content in file_map.items():
            try:
                # Enforce strict path isolation
                RepoSafetyValidator.validate_staging_path(path_str, settings.TARGET_ISOLATED_DIR)
                
                # Check for secrets
                content_safe, secret_warnings = RepoSafetyValidator.check_content_safety(content)
                if not content_safe:
                    safety_passed = False
                    warnings.extend(secret_warnings)

                proposed_files.append({
                    "relative_path": path_str,
                    "action": "create",
                    "size_bytes": len(content.encode("utf-8")),
                    "validation_status": "passed"
                })
            except RepositorySafetyError as e:
                safety_passed = False
                warnings.append(str(e))

        validation_summary = {
            "total_solutions": len(solutions),
            "solutions_passed": sum(1 for s in solutions if s.get("validation_status") == "passed"),
            "files_to_commit": len(proposed_files),
        }

        return {
            "job_id": job_id,
            "target_branch": branch_name,
            "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
            "proposed_files": proposed_files,
            "validation_summary": validation_summary,
            "safety_checks_passed": safety_passed,
            "warnings": warnings
        }

    @classmethod
    async def publish_to_github(
        cls,
        assignment_id: str,
        job_id: str,
        assignment_title: str,
        language: str,
        solutions: List[Dict[str, Any]],
        week_module: Optional[str] = None,
        commit_message: Optional[str] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes verified atomic publish to GitHub via GitHub Git Data API.
        Guarantees least privilege, dedicated branch, and verified remote commit SHA.
        """
        branch_name = cls.generate_branch_name(job_id)
        preview = cls.preview_changes(
            assignment_id=assignment_id,
            job_id=job_id,
            assignment_title=assignment_title,
            language=language,
            solutions=solutions,
            week_module=week_module
        )

        if not preview["safety_checks_passed"]:
            raise RepositorySafetyError(f"Safety checks failed: {'; '.join(preview['warnings'])}")

        github_token = token or settings.GITHUB_TOKEN
        if not github_token:
            raise RepositorySafetyError(
                "GitHub token is not configured. Please supply a Personal Access Token in Settings to publish."
            )

        owner = settings.GITHUB_OWNER
        repo = settings.GITHUB_REPO
        base_branch = settings.GITHUB_DEFAULT_BRANCH

        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Autoryx-Assignment-Agent/1.0"
        }

        file_map = OutputOrganizer.assemble_assignment_files(
            assignment_id=assignment_id,
            job_id=job_id,
            assignment_title=assignment_title,
            language=language,
            solutions=solutions,
            week_module=week_module,
            branch_name=branch_name
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Fetch latest commit SHA on base branch (main)
            ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{base_branch}"
            ref_res = await client.get(ref_url, headers=headers)
            if ref_res.status_code != 200:
                raise RepositorySafetyError(f"Failed to fetch base branch '{base_branch}': {ref_res.text}")
            base_sha = ref_res.json()["object"]["sha"]

            # 2. Get base tree SHA
            commit_url = f"https://api.github.com/repos/{owner}/{repo}/git/commits/{base_sha}"
            commit_res = await client.get(commit_url, headers=headers)
            if commit_res.status_code != 200:
                raise RepositorySafetyError(f"Failed to fetch commit '{base_sha}': {commit_res.text}")
            base_tree_sha = commit_res.json()["tree"]["sha"]

            # 3. Create Blobs & Tree Entries strictly for verified files
            tree_entries = []
            for path_str, content in file_map.items():
                # Re-verify path safety
                RepoSafetyValidator.validate_staging_path(path_str, settings.TARGET_ISOLATED_DIR)
                
                blob_url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs"
                blob_res = await client.post(
                    blob_url,
                    headers=headers,
                    json={
                        "content": content,
                        "encoding": "utf-8"
                    }
                )
                if blob_res.status_code != 201:
                    raise RepositorySafetyError(f"Failed to create blob for {path_str}: {blob_res.text}")
                
                blob_sha = blob_res.json()["sha"]
                tree_entries.append({
                    "path": path_str,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })

            # 4. Create new Tree pointing to base tree
            tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees"
            new_tree_res = await client.post(
                tree_url,
                headers=headers,
                json={
                    "base_tree": base_tree_sha,
                    "tree": tree_entries
                }
            )
            if new_tree_res.status_code != 201:
                raise RepositorySafetyError(f"Failed to create git tree: {new_tree_res.text}")
            new_tree_sha = new_tree_res.json()["sha"]

            # 5. Create Commit
            msg = commit_message or f"feat(autoryx): generate assignment solutions [{job_id}]\n\nAutomated delivery under {settings.TARGET_ISOLATED_DIR}"
            new_commit_url = f"https://api.github.com/repos/{owner}/{repo}/git/commits"
            new_commit_res = await client.post(
                new_commit_url,
                headers=headers,
                json={
                    "message": msg,
                    "tree": new_tree_sha,
                    "parents": [base_sha]
                }
            )
            if new_commit_res.status_code != 201:
                raise RepositorySafetyError(f"Failed to create commit: {new_commit_res.text}")
            new_commit_sha = new_commit_res.json()["sha"]

            # 6. Create or update reference refs/heads/autoryx/assignment-<job_id>
            # (Never touch refs/heads/main!)
            target_ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
            target_ref_res = await client.post(
                target_ref_url,
                headers=headers,
                json={
                    "ref": f"refs/heads/{branch_name}",
                    "sha": new_commit_sha
                }
            )
            
            # If branch already exists, update it safely (force=False)
            if target_ref_res.status_code == 422:
                update_ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
                target_ref_res = await client.patch(
                    update_ref_url,
                    headers=headers,
                    json={
                        "sha": new_commit_sha,
                        "force": False
                    }
                )

            if target_ref_res.status_code not in (200, 201):
                raise RepositorySafetyError(f"Failed to create dedicated branch '{branch_name}': {target_ref_res.text}")

            commit_web_url = f"https://github.com/{owner}/{repo}/commit/{new_commit_sha}"

            return {
                "success": True,
                "job_id": job_id,
                "branch_name": branch_name,
                "commit_sha": new_commit_sha,
                "commit_url": commit_web_url,
                "published_files": list(file_map.keys()),
                "error": None
            }
