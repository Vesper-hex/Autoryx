import pytest
from app.services.ingestion.document_parser import DocumentParser
from app.services.extraction.question_extractor import QuestionExtractor

def test_validate_upload_limits():
    valid, err = DocumentParser.validate_upload("assignment.pdf", 1024 * 1024)
    assert valid is True
    assert err is None

    # Unsupported format
    invalid, err = DocumentParser.validate_upload("payload.exe", 1024)
    assert invalid is False
    assert "Unsupported file format" in err

    # Oversized file (> 25MB)
    oversized, err = DocumentParser.validate_upload("huge.pdf", 30 * 1024 * 1024)
    assert oversized is False
    assert "exceeds maximum limit" in err

def test_extract_questions_rule_based():
    sample_text = """
    Question 1: Sum of Array Elements
    Given an array of integers, return the sum of all elements.
    Constraints: 1 <= n <= 1000
    Sample Input:
    5
    1 2 3 4 5
    Sample Output:
    15

    Question 2: Palindrome Checker
    Determine if a given string is a palindrome.
    Sample Input:
    racecar
    Sample Output:
    Yes
    """
    questions = QuestionExtractor.extract_questions_rule_based(sample_text, language="cpp")
    assert len(questions) == 2
    assert questions[0]["question_number"] == 1
    assert "Sum of Array" in questions[0]["title"]
    assert questions[0]["target_filename"] == "question_01.cpp"
    assert len(questions[0]["sample_inputs"]) > 0

    assert questions[1]["question_number"] == 2
    assert "Palindrome" in questions[1]["title"]
    assert questions[1]["target_filename"] == "question_02.cpp"
