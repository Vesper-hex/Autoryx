import re
from typing import Optional, List, Dict, Any
from app.services.generation.base import BaseLLMProvider
from app.services.generation.gemini_provider import GeminiProvider
from app.services.generation.openai_provider import OpenAIProvider
from app.services.generation.mock_provider import MockLLMProvider
from app.core.config import settings
from app.core.logging import logger

class SolutionGenerator:
    """
    Orchestrates AI code generation, provider selection, output cleanup,
    markdown stripping, and syntax validation.
    """

    @classmethod
    def clean_code(cls, raw_output: str, language: str) -> str:
        """Strips markdown fences and introductory conversational text."""
        if not raw_output:
            return ""

        text = raw_output.strip()

        # Extract code from ```lang ... ``` blocks if present
        fence_match = re.search(r'```(?:[a-zA-Z0-9_\-\+]+)?\s*\n([\s\S]*?)```', text)
        if fence_match:
            text = fence_match.group(1).strip()
        else:
            # If line starts with ```, strip it
            lines = text.split("\n")
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # Remove common introductory greetings like "Here is the C++ solution:"
        unwanted_prefixes = [
            r'^(?:Here\s+is\s+the\s+.*?(?:solution|code):?\s*\n*)',
            r'^(?:Sure!|Certainly!|Below\s+is\s+the\s+code:?\s*\n*)',
        ]
        for pat in unwanted_prefixes:
            text = re.sub(pat, '', text, flags=re.IGNORECASE)

        return text.strip()

    @classmethod
    def get_provider(cls, provider_name: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None) -> BaseLLMProvider:
        prov = (provider_name or settings.AI_PROVIDER).lower()

        if prov == "gemini":
            key = api_key or settings.GEMINI_API_KEY
            if key:
                return GeminiProvider(api_key=key, model_name=model or settings.GEMINI_MODEL)
            logger.info("Gemini API key not found; using high-fidelity offline mock provider.")
            return MockLLMProvider()

        elif prov == "openai":
            key = api_key or settings.OPENAI_API_KEY
            if key:
                return OpenAIProvider(api_key=key, model_name=model or settings.OPENAI_MODEL)
            logger.info("OpenAI API key not found; using high-fidelity offline mock provider.")
            return MockLLMProvider()

        elif prov == "mock":
            return MockLLMProvider()

        return MockLLMProvider()

    @classmethod
    def generate(
        cls,
        question_title: str,
        question_description: str,
        language: str,
        constraints: Optional[str] = None,
        sample_inputs: Optional[List[str]] = None,
        sample_outputs: Optional[List[str]] = None,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        provider = cls.get_provider(provider_name, api_key, model)
        try:
            raw = provider.generate_solution(
                question_title=question_title,
                question_description=question_description,
                language=language,
                constraints=constraints,
                sample_inputs=sample_inputs,
                sample_outputs=sample_outputs
            )
            cleaned = cls.clean_code(raw, language)
            if not cleaned:
                raise ValueError("Model produced empty code output.")
            return cleaned
        except Exception as e:
            logger.warning(f"Primary provider generation error: {e}. Falling back to deterministic offline provider.")
            mock = MockLLMProvider()
            raw = mock.generate_solution(
                question_title=question_title,
                question_description=question_description,
                language=language,
                constraints=constraints,
                sample_inputs=sample_inputs,
                sample_outputs=sample_outputs
            )
            return cls.clean_code(raw, language)
