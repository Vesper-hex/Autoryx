from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.models.activity import Setting
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest
from app.services.github.github_client import GitHubClient
from app.services.generation.solution_generator import SolutionGenerator
from app.core.logging import logger

router = APIRouter(prefix="/settings", tags=["Settings"])

def mask_secret(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    val = val.strip()
    if len(val) <= 8:
        return "********"
    return f"{val[:4]}...{val[-4:]}"

def get_db_setting(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
    s = db.query(Setting).filter(Setting.key == key).first()
    if s and s.value is not None:
        return s.value
    return default

def set_db_setting(db: Session, key: str, value: Optional[str], is_secret: bool = False):
    s = db.query(Setting).filter(Setting.key == key).first()
    if not s:
        s = Setting(key=key, value=value, is_secret=is_secret)
        db.add(s)
    else:
        s.value = value
        s.is_secret = is_secret
    db.commit()

@router.get("", response_model=SettingsResponse)
def get_current_settings(db: Session = Depends(get_db)):
    """Retrieves current application settings with masked secrets."""
    github_owner = get_db_setting(db, "github_owner", settings.GITHUB_OWNER)
    github_repo = get_db_setting(db, "github_repo", settings.GITHUB_REPO)
    github_default_branch = get_db_setting(db, "github_default_branch", settings.GITHUB_DEFAULT_BRANCH)
    github_token = get_db_setting(db, "github_token", settings.GITHUB_TOKEN)
    
    ai_provider = get_db_setting(db, "ai_provider", settings.AI_PROVIDER)
    gemini_key = get_db_setting(db, "gemini_key", settings.GEMINI_API_KEY)
    gemini_model = get_db_setting(db, "gemini_model", settings.GEMINI_MODEL)
    openai_key = get_db_setting(db, "openai_key", settings.OPENAI_API_KEY)
    openai_model = get_db_setting(db, "openai_model", settings.OPENAI_MODEL)
    
    max_repair = int(get_db_setting(db, "max_repair_attempts", str(settings.MAX_REPAIR_ATTEMPTS)))
    auto_pub = get_db_setting(db, "auto_publish_branch", str(settings.AUTO_PUBLISH_BRANCH)).lower() in ("true", "1")

    return {
        "github_owner": github_owner,
        "github_repo": github_repo,
        "github_default_branch": github_default_branch,
        "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
        "has_github_token": bool(github_token),
        "github_token_masked": mask_secret(github_token),
        
        "ai_provider": ai_provider,
        "gemini_model": gemini_model,
        "has_gemini_key": bool(gemini_key),
        "gemini_key_masked": mask_secret(gemini_key),
        
        "openai_model": openai_model,
        "has_openai_key": bool(openai_key),
        "openai_key_masked": mask_secret(openai_key),
        
        "max_repair_attempts": max_repair,
        "auto_publish_branch": auto_pub,
        "compilation_timeout_seconds": settings.COMPILATION_TIMEOUT_SECONDS,
        "execution_timeout_seconds": settings.EXECUTION_TIMEOUT_SECONDS,
        
        "worker_health": "running",
        "database_status": "connected"
    }

@router.post("", response_model=SettingsResponse)
def update_settings(req: SettingsUpdateRequest, db: Session = Depends(get_db)):
    """Updates settings and persists them to the database."""
    if req.github_owner is not None:
        set_db_setting(db, "github_owner", req.github_owner.strip())
    if req.github_repo is not None:
        set_db_setting(db, "github_repo", req.github_repo.strip())
    if req.github_default_branch is not None:
        set_db_setting(db, "github_default_branch", req.github_default_branch.strip())
    if req.github_token is not None:
        set_db_setting(db, "github_token", req.github_token.strip() if req.github_token.strip() else None, is_secret=True)

    if req.ai_provider is not None:
        set_db_setting(db, "ai_provider", req.ai_provider.strip().lower())
    if req.gemini_key is not None:
        set_db_setting(db, "gemini_key", req.gemini_key.strip() if req.gemini_key.strip() else None, is_secret=True)
    if req.gemini_model is not None:
        set_db_setting(db, "gemini_model", req.gemini_model.strip())
    if req.openai_key is not None:
        set_db_setting(db, "openai_key", req.openai_key.strip() if req.openai_key.strip() else None, is_secret=True)
    if req.openai_model is not None:
        set_db_setting(db, "openai_model", req.openai_model.strip())

    if req.max_repair_attempts is not None:
        set_db_setting(db, "max_repair_attempts", str(req.max_repair_attempts))
    if req.auto_publish_branch is not None:
        set_db_setting(db, "auto_publish_branch", str(req.auto_publish_branch))

    return get_current_settings(db)

@router.post("/test-github")
async def test_github_connection(db: Session = Depends(get_db)):
    """Verifies that the configured GitHub repository and token are operational."""
    owner = get_db_setting(db, "github_owner", settings.GITHUB_OWNER)
    repo = get_db_setting(db, "github_repo", settings.GITHUB_REPO)
    token = get_db_setting(db, "github_token", settings.GITHUB_TOKEN)

    client = GitHubClient(owner=owner, repo=repo, token=token)
    res = await client.get_repo_status()
    return res

@router.post("/test-ai")
def test_ai_provider(db: Session = Depends(get_db)):
    """Tests code generation with the currently active AI provider."""
    provider = get_db_setting(db, "ai_provider", settings.AI_PROVIDER)
    gemini_key = get_db_setting(db, "gemini_key", settings.GEMINI_API_KEY)
    openai_key = get_db_setting(db, "openai_key", settings.OPENAI_API_KEY)
    key = gemini_key if provider == "gemini" else openai_key

    try:
        sample_code = SolutionGenerator.generate(
            question_title="Sum of Two Numbers",
            question_description="Write a program that takes two integers a and b from stdin and prints their sum.",
            language="cpp",
            sample_inputs=["3 5"],
            sample_outputs=["8"],
            provider_name=provider,
            api_key=key
        )
        return {
            "success": True,
            "provider": provider,
            "sample_output_preview": sample_code[:200]
        }
    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "error": str(e)
        }
