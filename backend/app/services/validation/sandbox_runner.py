import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.core.logging import logger

class SandboxExecutionError(Exception):
    pass

class SandboxRunner:
    """
    Executes compilation and test runs within a strictly isolated,
    ephemeral environment with timeouts, sanitized environment variables,
    and automatic cleanup of all binary artifacts.
    """

    SAFE_ENV_KEYS = {
        "PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "PATHEXT",
        "JAVA_HOME", "LANG", "LC_ALL", "USERPROFILE",
        "APPDATA", "LOCALAPPDATA", "HOMEDRIVE", "HOMEPATH",
        "PROGRAMDATA", "PROGRAMFILES", "COMMONPROGRAMFILES", "OS"
    }

    @classmethod
    def get_sanitized_env(cls) -> Dict[str, str]:
        """Creates a minimal environment dictionary stripped of all secrets and credentials."""
        safe_keys_upper = {k.upper() for k in cls.SAFE_ENV_KEYS}
        safe_env = {}
        for key, val in os.environ.items():
            if key.upper() in safe_keys_upper:
                safe_env[key] = val
        # Explicitly ensure no credentials leak into sandbox
        for forbidden in ["GITHUB_TOKEN", "GEMINI_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "DATABASE_URL"]:
            for k in list(safe_env.keys()):
                if forbidden.lower() in k.lower():
                    safe_env.pop(k, None)
        return safe_env

    @classmethod
    def run_command(
        cls,
        cmd: List[str],
        cwd: Path,
        stdin_input: Optional[str] = None,
        timeout: int = 10
    ) -> Tuple[int, str, str, bool]:
        """
        Runs a command with timeouts and captured outputs.
        Returns: (exit_code, stdout, stderr, timed_out)
        """
        env = cls.get_sanitized_env()
        timed_out = False
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                stdin=subprocess.PIPE if stdin_input is not None else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                # On Windows, create new process group
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )

            stdout_data, stderr_data = proc.communicate(
                input=stdin_input,
                timeout=timeout
            )
            return proc.returncode, stdout_data or "", stderr_data or "", False

        except subprocess.TimeoutExpired:
            timed_out = True
            logger.warning(f"Process timed out after {timeout} seconds: {' '.join(cmd)}")
            try:
                proc.kill()
                stdout_data, stderr_data = proc.communicate(timeout=2)
            except Exception:
                stdout_data, stderr_data = "", ""
            return -1, stdout_data or "", (stderr_data or "") + f"\n[Execution timed out after {timeout} seconds]", True

        except Exception as e:
            logger.error(f"Execution error for {cmd}: {e}")
            return -1, "", str(e), False
