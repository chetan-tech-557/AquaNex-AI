"""FastAPI server application instance for AquaNex AI backend."""

import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure root directory is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config.settings import settings
from backend.app.database.db import init_db
from backend.app.api.routes import router as api_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("AquaNexServer")


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AquaNex AI server starting up...")
    init_db()
    logger.info("Database initialized successfully at: %s", settings.database_url)
    yield
    logger.info("AquaNex AI server shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AquaNex AI API",
        description="AI-Driven Adaptive Aquaculture Feeding Optimization REST Backend",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS configuration
    allowed_origins = list(settings.cors_origins)
    for dev_origin in ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"]:
        if dev_origin not in allowed_origins:
            allowed_origins.append(dev_origin)

    logger.info("Configuring CORS with origins: %s", allowed_origins)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router)

    @app.get("/", summary="Root Status")
    async def root():
        return JSONResponse({
            "service": "AquaNex AI Backend",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "recommendation_endpoint": "/api/v1/recommendation",
        })

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("Running AquaNex AI server on %s:%d", settings.api_host, settings.api_port)
    uvicorn.run(
        "backend.app.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
