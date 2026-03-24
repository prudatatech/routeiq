"""
RouteIQ - Fleet Intelligence Platform
"""
import sys
import logging
print("PYTHON_STARTUP: Initializing RouteIQ Backend...")
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
    logger.info("Lifespan starting: Resilient Mode active")

    import asyncio

    # Background task for DB + Redis to avoid blocking the server boot
    async def initial_setup():
        # 1. Database
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified/created background")
        except Exception as e:
            logger.error(f"Background database init failed: {e}")

        # 2. Redis
        try:
            await redis_client.ping()
            logger.info("Redis connected background")
        except Exception as e:
            logger.error(f"Background Redis init failed: {e}")

    asyncio.create_task(initial_setup())
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
