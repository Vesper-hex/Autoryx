import re
import os
from pathlib import Path
from typing import List, Tuple, Set

# Reserved Windows file names and dangerous shell characters
RESERVED_NAMES = {"con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "lpt1", "lpt2", "lpt3"}
DANGEROUS_CHARACTERS = set(';&|`$<>"\n\r\t?*[]!^')

# Forbidden patterns to never commit (secrets, binaries, envs)
FORBIDDEN_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".obj", ".class",
    ".env", ".key", ".pem", ".p12", ".crt", ".token", ".secret"
}
FORBIDDEN_FILENAMES = {
    ".env", ".env.local", ".env.production", "credentials.json", "id_rsa", "id_ed25519"
}

class RepositorySafetyError(ValueError):
    """Raised when an operation violates strict repository safety boundaries."""
    pass

class RepoSafetyValidator:
    """
    Strict repository safety gatekeeper for Autoryx.
    All GitHub publishing and staging must pass through this validator.
    """

    ALLOWED_PREFIX = "STEP_Agent_Assignments"

    @classmethod
    def sanitize_identifier(cls, raw_name: str) -> str:
        """Sanitizes an assignment or folder identifier into safe alphanumeric/underscores."""
        clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', raw_name.strip()).strip('_')
        if not clean:
            clean = "assignment"
        return clean[:50]

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """
        Validates a single source or documentation filename.
        Rejects path traversal, forbidden extensions, reserved device names, and control characters.
        """
        if not filename or not isinstance(filename, str):
            raise RepositorySafetyError("Filename cannot be empty.")
            
        filename = filename.strip()
        
        # Check forbidden characters
        if any(c in DANGEROUS_CHARACTERS for c in filename):
            raise RepositorySafetyError(f"Malicious or illegal characters in filename: {filename}")
            
        # Check path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            raise RepositorySafetyError(f"Filename must be a single file name, not a path: {filename}")
            
        stem = Path(filename).stem.lower()
        if stem in RESERVED_NAMES:
            raise RepositorySafetyError(f"Filename uses reserved system device name: {filename}")
            
        ext = Path(filename).suffix.lower()
        if ext in FORBIDDEN_EXTENSIONS:
            raise RepositorySafetyError(f"Forbidden file extension '{ext}' in filename: {filename}")
            
        if filename.lower() in FORBIDDEN_FILENAMES:
            raise RepositorySafetyError(f"Forbidden file name: {filename}")
            
        return filename

    @classmethod
    def validate_staging_path(cls, relative_path: str, allowed_root_dir: str = "STEP_Agent_Assignments") -> Path:
        """
        Validates that a relative file path is strictly within the permitted output folder.
        Rejects path traversal, absolute paths, and any file outside allowed_root_dir.
        """
        if not relative_path:
            raise RepositorySafetyError("Path cannot be empty.")
            
        # Normalise separators
        norm = relative_path.replace("\\", "/").strip("/")
        
        # Disallow absolute paths
        if relative_path.startswith("/") or relative_path.startswith("\\") or (len(relative_path) > 1 and relative_path[1] == ":"):
            raise RepositorySafetyError(f"Absolute paths are forbidden: {relative_path}")
            
        # Disallow path traversal components
        parts = norm.split("/")
        if ".." in parts or "." in parts:
            raise RepositorySafetyError(f"Path traversal detected: {relative_path}")
            
        # Must start with allowed_root_dir
        if parts[0] != allowed_root_dir:
            raise RepositorySafetyError(
                f"SAFETY VIOLATION: Path '{relative_path}' is outside permitted directory '{allowed_root_dir}'."
            )
            
        # Verify the file name part
        cls.validate_filename(parts[-1])
        
        return Path(norm)

    @classmethod
    def validate_batch_staging_paths(cls, relative_paths: List[str], allowed_root_dir: str = "STEP_Agent_Assignments") -> List[str]:
        """
        Validates a list of relative paths intended for git staging.
        Guarantees that git add . is NEVER used and every single file is explicitly permitted.
        """
        if not relative_paths:
            raise RepositorySafetyError("No files provided for staging.")
            
        validated = []
        for path in relative_paths:
            cls.validate_staging_path(path, allowed_root_dir)
            validated.append(path.replace("\\", "/"))
            
        return validated

    @classmethod
    def validate_branch_name(cls, branch_name: str) -> str:
        """
        Validates a git branch name. Must be dedicated (e.g. autoryx/assignment-*) and not main/master.
        """
        if not branch_name:
            raise RepositorySafetyError("Branch name cannot be empty.")
            
        cleaned = branch_name.strip()
        if cleaned.lower() in {"main", "master", "develop", "prod", "production", "head"}:
            raise RepositorySafetyError(f"Direct publishing to protected branch '{cleaned}' is strictly forbidden.")
            
        if not cleaned.startswith("autoryx/"):
            raise RepositorySafetyError(f"Dedicated branch must start with 'autoryx/', got: {cleaned}")
            
        if any(c in DANGEROUS_CHARACTERS or c.isspace() for c in cleaned):
            raise RepositorySafetyError(f"Illegal characters in branch name: {cleaned}")
            
        return cleaned

    @classmethod
    def check_content_safety(cls, content: str) -> Tuple[bool, List[str]]:
        """
        Checks whether source content accidentally contains exposed tokens, private keys, or passwords.
        """
        warnings = []
        patterns = {
            "GitHub Token": r'(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})',
            "Google AI Key": r'AIza[0-9A-Za-z-_]{35}',
            "OpenAI Key": r'sk-[a-zA-Z0-9]{20,}',
            "Private Key": r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----',
        }
        
        for name, pattern in patterns.items():
            if re.search(pattern, content):
                warnings.append(f"Potential {name} detected in source code! Publishing blocked.")
                
        return len(warnings) == 0, warnings
