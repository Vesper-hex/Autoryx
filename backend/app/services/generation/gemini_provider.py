import os
from typing import Optional
from app.services.generation.base import BaseLLMProvider
from app.core.logging import logger

class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI generation provider."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name or "gemini-1.5-flash"

    def _get_model(self, genai):
        for candidate in [self.model_name, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            try:
                return genai.GenerativeModel(candidate)
            except Exception:
                continue
        return genai.GenerativeModel("gemini-1.5-flash")

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
            raise ValueError("GEMINI_API_KEY is not configured. Please add your key in Settings.")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = self._get_model(genai)

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
{constraints or 'None specified'}

{samples_text}

CRITICAL RULES:
1. Provide ONLY valid executable source code.
2. Read from standard input (stdin) and write to standard output (stdout) exactly as requested.
3. Handle edge cases and time/memory limits.
4. Do NOT include markdown explanations, tutorials, conversational greetings, or backticks in the response if possible, or format with clean ```{language} fences.
5. If Java is requested, use 'public class Solution' or 'public class Q1' with standard main method.
"""
        response = model.generate_content(prompt)
        return response.text

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
            raise ValueError("GEMINI_API_KEY is not configured.")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)

        prompt = f"""You are repairing a {language} solution that failed compilation or tests.

Problem Context:
{question_description}

Current Code:
```{language}
{current_code}
```

Failure / Compiler / Test Error Output:
{compiler_or_test_error}

TASK:
Fix the bugs and provide the complete corrected source code in {language}.
Return ONLY the corrected code without markdown or conversational explanations.
"""
        response = model.generate_content(prompt)
        return response.text
