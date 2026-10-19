from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.api.router import api_router
from app.workers.job_queue import PersistentJobQueue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Autoryx backend...")
    init_db()
    logger.info("Database initialized successfully.")
    
    # Start background persistent worker loop
    PersistentJobQueue.ensure_worker_running()
    yield
    # Shutdown
    logger.info("Shutting down Autoryx backend...")
    PersistentJobQueue.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autoryx — Personal STEP Assignment Automation Agent",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount frontend production build if available
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    logger.info(f"Mounted frontend build from {frontend_dist}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
