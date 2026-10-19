from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.assignments import router as assignments_router
from app.api.jobs import router as jobs_router
from app.api.repository import router as repository_router
from app.api.activities import router as activities_router
from app.api.settings import router as settings_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(assignments_router)
api_router.include_router(jobs_router)
api_router.include_router(repository_router)
api_router.include_router(activities_router)
api_router.include_router(settings_router)
