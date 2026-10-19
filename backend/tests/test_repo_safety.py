import pytest
from app.services.github.repo_safety import RepoSafetyValidator, RepositorySafetyError

def test_validate_allowed_staging_path():
    # Valid paths under STEP_Agent_Assignments
    p1 = RepoSafetyValidator.validate_staging_path("STEP_Agent_Assignments/README.md")
    assert str(p1).replace("\\", "/") == "STEP_Agent_Assignments/README.md"
    
    p2 = RepoSafetyValidator.validate_staging_path("STEP_Agent_Assignments/assignments/asgn_1/question_01.cpp")
    assert str(p2).replace("\\", "/") == "STEP_Agent_Assignments/assignments/asgn_1/question_01.cpp"

def test_reject_paths_outside_isolated_directory():
    # Attempt to write into Week 1
    with pytest.raises(RepositorySafetyError, match="SAFETY VIOLATION"):
        RepoSafetyValidator.validate_staging_path("Week 1/Q1.java")
        
    # Attempt to write into Week 2
    with pytest.raises(RepositorySafetyError, match="SAFETY VIOLATION"):
        RepoSafetyValidator.validate_staging_path("Week 2/Q1.java")
        
    # Attempt to overwrite root README or .gitignore
    with pytest.raises(RepositorySafetyError, match="SAFETY VIOLATION"):
        RepoSafetyValidator.validate_staging_path("README.md")
        
    with pytest.raises(RepositorySafetyError, match="SAFETY VIOLATION"):
        RepoSafetyValidator.validate_staging_path(".gitignore")

def test_reject_path_traversal():
    # Path traversal attempts
    with pytest.raises(RepositorySafetyError, match="Path traversal detected"):
        RepoSafetyValidator.validate_staging_path("STEP_Agent_Assignments/../Week 1/hacked.cpp")
        
    with pytest.raises(RepositorySafetyError, match="Path traversal detected"):
        RepoSafetyValidator.validate_staging_path("STEP_Agent_Assignments/assignments/../../etc/passwd")

def test_reject_absolute_paths():
    with pytest.raises(RepositorySafetyError, match="Absolute paths are forbidden"):
        RepoSafetyValidator.validate_staging_path("/etc/passwd")
        
    with pytest.raises(RepositorySafetyError, match="Absolute paths are forbidden"):
        RepoSafetyValidator.validate_staging_path("C:/Windows/System32/cmd.exe")

def test_reject_malicious_and_reserved_filenames():
    # Shell injection characters
    with pytest.raises(RepositorySafetyError, match="Malicious or illegal characters"):
        RepoSafetyValidator.validate_filename("evil;rm -rf.cpp")
        
    with pytest.raises(RepositorySafetyError, match="Malicious or illegal characters"):
        RepoSafetyValidator.validate_filename("pipe|bash.py")
        
    # Reserved Windows device names
    with pytest.raises(RepositorySafetyError, match="reserved system device name"):
        RepoSafetyValidator.validate_filename("con.cpp")
        
    with pytest.raises(RepositorySafetyError, match="reserved system device name"):
        RepoSafetyValidator.validate_filename("aux.java")

    # Forbidden extensions and secrets
    with pytest.raises(RepositorySafetyError, match="Forbidden file extension"):
        RepoSafetyValidator.validate_filename("payload.exe")
        
    with pytest.raises(RepositorySafetyError, match="Forbidden file extension"):
        RepoSafetyValidator.validate_filename("secret.key")
        
    with pytest.raises(RepositorySafetyError, match="Forbidden file name"):
        RepoSafetyValidator.validate_filename(".env")

def test_branch_name_safety():
    # Dedicated branch should pass
    branch = RepoSafetyValidator.validate_branch_name("autoryx/assignment-job_123")
    assert branch == "autoryx/assignment-job_123"

    # Protected branches must be strictly blocked
    with pytest.raises(RepositorySafetyError, match="protected branch"):
        RepoSafetyValidator.validate_branch_name("main")
        
    with pytest.raises(RepositorySafetyError, match="protected branch"):
        RepoSafetyValidator.validate_branch_name("master")
        
    with pytest.raises(RepositorySafetyError, match="must start with 'autoryx/'"):
        RepoSafetyValidator.validate_branch_name("feature-test")

def test_content_safety_check_detects_tokens():
    safe_code = "#include <iostream>\nint main() { return 0; }"
    is_safe, warnings = RepoSafetyValidator.check_content_safety(safe_code)
    assert is_safe is True
    assert len(warnings) == 0

    leaked_token_code = 'const char* token = "ghp_123456789012345678901234567890123456";'
    is_safe, warnings = RepoSafetyValidator.check_content_safety(leaked_token_code)
    assert is_safe is False
    assert any("GitHub Token" in w for w in warnings)
