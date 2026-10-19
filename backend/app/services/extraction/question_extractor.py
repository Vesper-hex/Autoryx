import re
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.services.github.repo_safety import RepoSafetyValidator

class QuestionExtractor:
    """
    Parses unstructured assignment text into structured questions with:
    - Title & question number
    - Description & problem statement
    - Constraints
    - Sample input/output pairs
    - Suggested target filename
    """

    DEFAULT_EXTENSIONS = {
        "cpp": ".cpp",
        "c": ".c",
        "java": ".java",
        "python": ".py",
    }

    @classmethod
    def get_extension_for_language(cls, language: str) -> str:
        lang = language.lower().strip()
        if "c++" in lang or "cpp" in lang:
            return ".cpp"
        elif lang == "c":
            return ".c"
        elif "java" in lang:
            return ".java"
        elif "python" in lang or "py" in lang:
            return ".py"
        return ".cpp"

    @classmethod
    def get_default_filename(cls, q_num: int, language: str) -> str:
        ext = cls.get_extension_for_language(language)
        if ext == ".java":
            return f"Q{q_num}.java"
        elif ext == ".py":
            return f"question_{q_num:02d}.py"
        elif ext == ".c":
            return f"question_{q_num:02d}.c"
        else:
            return f"question_{q_num:02d}.cpp"

    @classmethod
    def extract_questions_rule_based(cls, text: str, language: str = "cpp") -> List[Dict[str, Any]]:
        """
        Deterministic regex-based extraction splitting on Question/Problem/Exercise patterns.
        """
        questions: List[Dict[str, Any]] = []
        if not text or not text.strip():
            return questions

        # Normalize line breaks
        normalized = text.replace("\r\n", "\n")

        # Pattern to split questions: e.g. "Question 1", "Problem 1", "Q1.", "Exercise 1", "L1.", "Task 1"
        pattern = re.compile(
            r'(?m)^(?:(?:\*{1,3})?\s*(?:Question|Problem|Exercise|Task|Lab|Level|Part|Q|L)\s*#?\s*(\d+)[:\.\-\s]|(\d+)\.\s+[A-Z])',
            re.IGNORECASE
        )

        matches = list(pattern.finditer(normalized))

        if not matches:
            # Single question assignment
            q_dict = cls._parse_single_question_block(
                raw_block=normalized,
                q_num=1,
                language=language
            )
            questions.append(q_dict)
            return questions

        for i, match in enumerate(matches):
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(normalized)
            block = normalized[start_pos:end_pos].strip()

            q_num_str = match.group(1) or match.group(2)
            try:
                q_num = int(q_num_str)
            except (ValueError, TypeError):
                q_num = i + 1

            q_dict = cls._parse_single_question_block(
                raw_block=block,
                q_num=q_num,
                language=language
            )
            questions.append(q_dict)

        return questions

    @classmethod
    def _parse_single_question_block(cls, raw_block: str, q_num: int, language: str) -> Dict[str, Any]:
        def is_banner(line: str) -> bool:
            low = line.lower()
            return low.startswith('--- page') or 'codinclub' in low or 'bridgelabz' in low or 'category' in low or low.startswith('powered by')

        valid_lines = [l.strip() for l in raw_block.split("\n") if l.strip() and not is_banner(l)]
        header = valid_lines[0] if valid_lines else f"Question {q_num}"
        
        # Strip numbering prefix from title if present
        title = re.sub(r'^(?:Question|Problem|Exercise|Task|Lab|Level|Part|Q|L)?\s*#?\s*\d+[:\.\-\s]*', '', header, flags=re.IGNORECASE).strip()
        title = " ".join(title.split())
        if not title:
            title = f"Problem {q_num}"

        # Extract sample inputs / outputs
        sample_inputs = []
        sample_outputs = []

        # 1. First check tabular or assignment-style pairs (LeetCode, array sheets, etc.)
        io_sec = re.search(r'(?:Sample\s+Input\s*/\s*Output|Sample\s+I/O|Example|Input\s+Output)[\s\S]*?(?=Concepts|Constraints|\Z)', raw_block, re.IGNORECASE)
        if io_sec:
            raw_sec = re.sub(r'\(.*?\)', '', io_sec.group(0), flags=re.DOTALL)
            cleaned_sec = " ".join([l.strip() for l in raw_sec.split('\n') if l.strip()])
            pairs = re.findall(r'((?:[a-zA-Z0-9_]+\s*=\s*(?:\[[^\]]*\]|[^,\[]+),?\s*)+)\s*(\[[^\]]*\]|true|false|\d+)', cleaned_sec)
            for inp_p, out_p in pairs:
                c_inp = inp_p.strip()
                c_out = out_p.strip()
                if c_inp and c_inp not in sample_inputs:
                    sample_inputs.append(c_inp)
                if c_out and c_out not in sample_outputs:
                    sample_outputs.append(c_out)

        # 2. If not found, use traditional section-based extraction
        if not sample_inputs or not sample_outputs:
            input_matches = re.findall(r'Sample\s+Input[:\s]+([\s\S]*?)(?=Sample\s+Output|\Z)', raw_block, re.IGNORECASE)
            for inp in input_matches:
                clean_inp = " ".join(inp.strip("` \n\r\t/").split())
                if clean_inp and clean_inp not in ["/", "\\", "-"] and clean_inp not in sample_inputs:
                    sample_inputs.append(clean_inp)

            output_matches = re.findall(r'Sample\s+Output[:\s]+([\s\S]*?)(?=Sample\s+Input|Explanation|\Z)', raw_block, re.IGNORECASE)
            for out in output_matches:
                clean_out = " ".join(out.strip("` \n\r\t/").split())
                # If clean_out has brackets or numbers, extract that cleanly
                bracket_m = re.search(r'\[[^\]]*\]', clean_out)
                if bracket_m:
                    clean_out = bracket_m.group(0)
                elif re.search(r'\b(true|false)\b', clean_out, re.I):
                    clean_out = re.search(r'\b(true|false)\b', clean_out, re.I).group(0).lower()
                elif len(clean_out) > 100:
                    clean_out = clean_out[:100]
                if clean_out and clean_out not in sample_outputs:
                    sample_outputs.append(clean_out)

        # Extract constraints if any
        constraints = ""
        constraint_match = re.search(r'(?:Constraints?|Limits?)[:\s]*\n?([\s\S]*?)(?=(?:Sample|Example|Input|Output|\Z))', raw_block, re.IGNORECASE)
        if constraint_match:
            constraints = constraint_match.group(1).strip()

        # Check if text specifically asks for a specific filename (e.g. "Save as Q1.java" or "File: solution.cpp")
        filename_match = re.search(r'(?:Save as|filename|file name|create a file named)[:\s]*`?([a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+)`?', raw_block, re.IGNORECASE)
        if filename_match:
            raw_filename = filename_match.group(1)
            try:
                target_filename = RepoSafetyValidator.validate_filename(raw_filename)
            except Exception:
                target_filename = cls.get_default_filename(q_num, language)
        else:
            target_filename = cls.get_default_filename(q_num, language)

        return {
            "question_number": q_num,
            "title": title[:200],
            "description": raw_block,
            "constraints": constraints or None,
            "target_filename": target_filename,
            "sample_inputs": sample_inputs,
            "sample_outputs": sample_outputs,
            "is_approved": True,
        }
