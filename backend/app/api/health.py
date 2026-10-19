import shutil
import sys
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Health check verifying database connection and compiler availability."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    compilers = {
        "gcc": shutil.which("gcc") is not None,
        "g++": shutil.which("g++") is not None,
        "javac": shutil.which("javac") is not None,
        "java": shutil.which("java") is not None,
        "python": shutil.which("python") is not None,
    }

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "error",
        "compilers": compilers,
        "target_repo": f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}",
        "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
        "ai_provider": settings.AI_PROVIDER
    }
