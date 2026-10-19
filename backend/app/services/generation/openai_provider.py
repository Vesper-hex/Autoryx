import os
from typing import Optional
from app.services.generation.base import BaseLLMProvider
from app.core.logging import logger

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API code generation and repair provider."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model_name = model_name

    def generate_solution(
        self,
        question_title: str,
        question_description: str,
        language: str,
        constraints: Optional[str] = None,
        sample_inputs: Optional[list] = None,
        sample_outputs: Optional[list] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        samples_text = ""
        if sample_inputs and sample_outputs:
            samples_text = "Sample Test Cases:\n"
            for idx, (inp, out) in enumerate(zip(sample_inputs, sample_outputs), 1):
                samples_text += f"Test {idx}:\nInput:\n{inp}\nExpected Output:\n{out}\n"

        prompt = f"""You are an expert programming assignment automation assistant.
Generate a complete, optimal, self-contained, and bug-free source code solution in {language}.

Problem Title: {question_title}
Language: {language}
Description:
{question_description}

Constraints:
{constraints or 'None'}

{samples_text}

Provide ONLY executable source code without markdown or explanation.
"""
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a professional software engineer that outputs only clean, executable code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content or ""

    def repair_solution(
        self,
        current_code: str,
        language: str,
        compiler_or_test_error: str,
        question_description: str,
        sample_inputs: Optional[list] = None,
        sample_outputs: Optional[list] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)

        prompt = f"""Repair this {language} solution:

Problem Context:
{question_description}

Code:
```{language}
{current_code}
```

Error Details:
{compiler_or_test_error}

Return ONLY the corrected code.
"""
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a code debugging expert that returns only fixed source code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content or ""
