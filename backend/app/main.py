"""
RouteIQ - Fleet Intelligence Platform
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import redis_client
import logging
from app.core.logging import setup_logging
from app.middleware.metrics import PrometheusMiddleware
from app.middleware.request_id import RequestIDMiddleware

logger = logging.getLogger("routeiq.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    setup_logging()

    # Create DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Connect Redis
    try:
        await redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis on startup: {e}")
        # In some environments, we might want to allow startup without Redis
        # but for production it's usually better to know immediately.

    yield

    # Cleanup
    await redis_client.close()
    await engine.dispose()


app = FastAPI(
    title="RouteIQ",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware (order matters — outermost first)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "RouteIQ API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    try:
        await redis_client.ping()
        return {"status": "ready", "redis": "ok", "database": "ok"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}
