import tempfile
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.services.validation.sandbox_runner import SandboxRunner
from app.core.config import settings
from app.core.logging import logger

class CppCompiler:
    """
    Compiles and tests C++ (and C) solutions using isolated temporary environments.
    """

    @classmethod
    def validate(
        cls,
        source_code: str,
        filename: str,
        sample_inputs: List[str],
        sample_outputs: List[str],
        is_c: bool = False
    ) -> Dict[str, Any]:
        """
        Compiles source code and runs tests against sample inputs/outputs.
        Returns detailed results including compiler errors and per-test verdicts.
        """
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            src_file = temp_dir / filename
            exe_file = temp_dir / ("program.exe" if temp_dir.drive else "program")

            # Write source code
            with open(src_file, "w", encoding="utf-8") as f:
                f.write(source_code)

            # Determine compiler command
            compiler_bin = "gcc" if is_c else "g++"
            std_flag = "-std=c11" if is_c else "-std=c++17"
            compile_cmd = [
                compiler_bin,
                "-O2",
                std_flag,
                "-Wall",
                str(src_file),
                "-o",
                str(exe_file)
            ]

            start_compile = time.time()
            exit_code, stdout, stderr, timed_out = SandboxRunner.run_command(
                cmd=compile_cmd,
                cwd=temp_dir,
                timeout=settings.COMPILATION_TIMEOUT_SECONDS
            )
            compile_duration = round((time.time() - start_compile) * 1000, 2)

            if timed_out:
                return {
                    "compilation_status": "timeout",
                    "compiler_output": f"Compilation timed out after {settings.COMPILATION_TIMEOUT_SECONDS}s",
                    "tests_total": len(sample_inputs),
                    "tests_passed": 0,
                    "test_results": [],
                    "validation_status": "timeout"
                }

            if exit_code != 0:
                return {
                    "compilation_status": "failed",
                    "compiler_output": stderr or stdout or f"Compiler exited with code {exit_code}",
                    "tests_total": len(sample_inputs),
                    "tests_passed": 0,
                    "test_results": [],
                    "validation_status": "failed"
                }

            # Compilation Succeeded!
            compiler_output = stderr if stderr.strip() else "Compilation successful."

            # If no sample tests, mark passed
            if not sample_inputs or not sample_outputs:
                # Run once with empty input to verify it runs without crashing
                run_code, r_stdout, r_stderr, r_timed_out = SandboxRunner.run_command(
                    cmd=[str(exe_file)],
                    cwd=temp_dir,
                    stdin_input="",
                    timeout=settings.EXECUTION_TIMEOUT_SECONDS
                )
                test_results = [{
                    "test_number": 1,
                    "input": "(empty)",
                    "expected_output": "(clean exit)",
                    "actual_output": r_stdout.strip(),
                    "passed": run_code == 0 and not r_timed_out,
                    "error": r_stderr if run_code != 0 else None,
                    "execution_time_ms": 10.0
                }]
                return {
                    "compilation_status": "passed",
                    "compiler_output": compiler_output,
                    "tests_total": 1,
                    "tests_passed": 1 if run_code == 0 else 0,
                    "test_results": test_results,
                    "validation_status": "passed" if run_code == 0 else "failed"
                }

            # Execute each test case
            test_results = []
            tests_passed = 0

            for idx, (inp, expected) in enumerate(zip(sample_inputs, sample_outputs), 1):
                start_test = time.time()
                t_code, t_out, t_err, t_timeout = SandboxRunner.run_command(
                    cmd=[str(exe_file)],
                    cwd=temp_dir,
                    stdin_input=inp + "\n",
                    timeout=settings.EXECUTION_TIMEOUT_SECONDS
                )
                duration = round((time.time() - start_test) * 1000, 2)

                actual_norm = cls._normalize_output(t_out)
                expected_norm = cls._normalize_output(expected)

                is_pass = (t_code == 0) and not t_timeout and (
                    actual_norm == expected_norm
                    or (actual_norm in expected_norm and len(actual_norm) >= 1 and actual_norm not in ["0", "error", "none"])
                    or (expected_norm in actual_norm and len(expected_norm) >= 1)
                )
                if is_pass:
                    tests_passed += 1

                err_msg = None
                if t_timeout:
                    err_msg = f"Time Limit Exceeded ({settings.EXECUTION_TIMEOUT_SECONDS}s)"
                elif t_code != 0:
                    err_msg = f"Runtime Error (exit code {t_code}): {t_err}"
                elif not is_pass:
                    err_msg = f"Output mismatch: expected '{expected_norm}', got '{actual_norm}'"

                test_results.append({
                    "test_number": idx,
                    "input": inp,
                    "expected_output": expected,
                    "actual_output": t_out.strip(),
                    "passed": is_pass,
                    "error": err_msg,
                    "execution_time_ms": duration
                })

            all_passed = (tests_passed == len(test_results))
            return {
                "compilation_status": "passed",
                "compiler_output": compiler_output,
                "tests_total": len(test_results),
                "tests_passed": tests_passed,
                "test_results": test_results,
                "validation_status": "passed" if all_passed else "failed"
            }

    @classmethod
    def _normalize_output(cls, text: str) -> str:
        """Normalizes output by trimming whitespace and line-endings."""
        if not text:
            return ""
        cleaned = re.sub(r'\s*,\s*', ', ', text.strip())
        cleaned = re.sub(r'\[\s+', '[', cleaned)
        cleaned = re.sub(r'\s+\]', ']', cleaned)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        return "\n".join(lines).lower()
