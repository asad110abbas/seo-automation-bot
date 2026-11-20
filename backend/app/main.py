from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router
from app.api.v1.websocket import router as ws_router
from app.api.v1.auth import router as auth_router
from app.core.database import engine
from app.core.redis_client import close_redis
from app.core.logging import setup_logging, logger
from app.models import *  # noqa — ensures all models are registered for Alembic
from app.models.user import User  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("startup", environment=settings.environment)
    yield
    await close_redis()
    logger.info("shutdown")


app = FastAPI(
    title="SEO Automation Bot API",
    description="Multi-agent AI SEO automation system for local businesses in Pakistan",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SEO Automation Bot"}
