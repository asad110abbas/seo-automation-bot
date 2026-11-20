from fastapi import APIRouter
from app.api.v1.projects import router as projects_router
from app.api.v1.results import router as results_router
from app.api.v1.global_usage import router as global_usage_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
api_router.include_router(results_router)
api_router.include_router(global_usage_router)
