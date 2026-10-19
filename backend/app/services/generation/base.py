from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseLLMProvider(ABC):
    """Abstract base class for all AI code generation providers."""

    @abstractmethod
    def generate_solution(
        self,
        question_title: str,
        question_description: str,
        language: str,
        constraints: Optional[str] = None,
        sample_inputs: Optional[list] = None,
        sample_outputs: Optional[list] = None
    ) -> str:
        """Generates source code solution for a given problem."""
        pass

    @abstractmethod
    def repair_solution(
        self,
        current_code: str,
        language: str,
        compiler_or_test_error: str,
        question_description: str,
        sample_inputs: Optional[list] = None,
        sample_outputs: Optional[list] = None
    ) -> str:
        """Proposes a corrected version of the code given the compiler or test failure."""
        pass
