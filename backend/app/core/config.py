from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Autoryx"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database & Cache
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR}/autoryx.db",
        description="Database connection string (SQLite for zero-config local, PostgreSQL for cloud/prod)"
    )
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Target GitHub Repository Defaults
    GITHUB_OWNER: str = "Highorder-Thinking"
    GITHUB_REPO: str = "Step_semester_3"
    GITHUB_DEFAULT_BRANCH: str = "main"
    GITHUB_TOKEN: Optional[str] = None
    TARGET_ISOLATED_DIR: str = "STEP_Agent_Assignments"
    AUTO_PUBLISH_BRANCH: bool = False
    
    # AI Providers & Model Defaults
    AI_PROVIDER: str = "gemini"  # "gemini", "openai", "mock"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    # Sandbox & Validation
    MAX_REPAIR_ATTEMPTS: int = 2
    COMPILATION_TIMEOUT_SECONDS: int = 15
    EXECUTION_TIMEOUT_SECONDS: int = 5
    SANDBOX_MEMORY_MB: int = 256
    
    # Paths
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    WORKSPACE_DIR: Path = BASE_DIR / "storage" / "workspace"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    class Config:
        env_file = f"{BASE_DIR}/.env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure storage directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
