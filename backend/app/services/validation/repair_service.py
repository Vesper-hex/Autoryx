from typing import Dict, Any, List, Optional
from app.services.validation.compilers.cpp_compiler import CppCompiler
from app.services.validation.compilers.java_compiler import JavaCompiler
from app.services.validation.compilers.python_runner import PythonRunner
from app.services.generation.solution_generator import SolutionGenerator
from app.core.config import settings
from app.core.logging import logger

class RepairService:
    """
    Coordinates compilation, automated sample testing, and iterative AI repairs
    bounded by the maximum repair attempts setting.
    """

    @classmethod
    def run_validation(
        cls,
        source_code: str,
        filename: str,
        language: str,
        sample_inputs: List[str],
        sample_outputs: List[str]
    ) -> Dict[str, Any]:
        """Dispatches validation to the correct compiler/runner based on language."""
        lang = language.lower()
        if "c++" in lang or "cpp" in lang:
            return CppCompiler.validate(source_code, filename, sample_inputs, sample_outputs, is_c=False)
        elif lang == "c":
            return CppCompiler.validate(source_code, filename, sample_inputs, sample_outputs, is_c=True)
        elif "java" in lang:
            return JavaCompiler.validate(source_code, filename, sample_inputs, sample_outputs)
        elif "python" in lang or "py" in lang:
            return PythonRunner.validate(source_code, filename, sample_inputs, sample_outputs)
        else:
            return CppCompiler.validate(source_code, filename, sample_inputs, sample_outputs, is_c=False)

    @classmethod
    def validate_and_repair(
        cls,
        initial_code: str,
        filename: str,
        language: str,
        question_description: str,
        sample_inputs: List[str],
        sample_outputs: List[str],
        max_repairs: Optional[int] = None,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs initial validation, and if failure occurs, performs bounded AI repair loops.
        """
        limit = max_repairs if max_repairs is not None else settings.MAX_REPAIR_ATTEMPTS
        current_code = initial_code
        repair_history: List[Dict[str, Any]] = []
        attempts = 0

        # Run initial validation
        result = cls.run_validation(
            source_code=current_code,
            filename=filename,
            language=language,
            sample_inputs=sample_inputs,
            sample_outputs=sample_outputs
        )

        while (result["validation_status"] != "passed") and (attempts < limit):
            attempts += 1
            logger.info(f"Initiating repair attempt {attempts}/{limit} for {filename}...")

            # Collate error information
            error_details = []
            if result.get("compiler_output") and result["compilation_status"] != "passed":
                error_details.append(f"Compiler Error:\n{result['compiler_output']}")
            for t in result.get("test_results", []):
                if not t.get("passed"):
                    error_details.append(
                        f"Test {t.get('test_number')} Failed:\nInput:\n{t.get('input')}\nExpected:\n{t.get('expected_output')}\nGot:\n{t.get('actual_output')}\nError: {t.get('error')}"
                    )
            combined_error = "\n\n".join(error_details)

            # Record attempt history
            repair_history.append({
                "attempt_number": attempts,
                "code_before_repair": current_code,
                "error": combined_error,
                "compilation_status": result["compilation_status"],
                "tests_passed": result["tests_passed"],
                "tests_total": result["tests_total"]
            })

            # Call AI repair
            provider = SolutionGenerator.get_provider(provider_name, api_key, model)
            try:
                repaired_raw = provider.repair_solution(
                    current_code=current_code,
                    language=language,
                    compiler_or_test_error=combined_error,
                    question_description=question_description,
                    sample_inputs=sample_inputs,
                    sample_outputs=sample_outputs
                )
                repaired_clean = SolutionGenerator.clean_code(repaired_raw, language)
                if repaired_clean:
                    current_code = repaired_clean
            except Exception as e:
                logger.error(f"Repair attempt {attempts} failed with provider error: {e}")
                break

            # Re-validate with repaired code
            result = cls.run_validation(
                source_code=current_code,
                filename=filename,
                language=language,
                sample_inputs=sample_inputs,
                sample_outputs=sample_outputs
            )

        return {
            "final_code": current_code,
            "compilation_status": result["compilation_status"],
            "compiler_output": result["compiler_output"],
            "tests_total": result["tests_total"],
            "tests_passed": result["tests_passed"],
            "test_results": result["test_results"],
            "validation_status": result["validation_status"],
            "repair_attempts": attempts,
            "repair_history": repair_history
        }
