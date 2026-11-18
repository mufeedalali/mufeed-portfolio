"""
Main FastAPI application entry point.

Initializes and configures the RAG Pipeline API server.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import RAGPipelineException
from app.api.routes import health, documents, rag
from app.api.dependencies import (
    get_settings_instance,
    get_ingestion_service,
    get_rag_service,
    get_chat_service,
    reset_dependencies,
)

# Setup logging
settings = get_settings()
logger = setup_logging(
    log_level=settings.log_level,
    log_file="rag_pipeline.log",
    log_dir="./logs",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")

    # Initialize services
    _ = get_settings_instance()
    _ = get_ingestion_service()
    _ = get_rag_service()
    _ = get_chat_service()

    logger.info("All services initialized")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    reset_dependencies()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Complete RAG Pipeline for AI-powered document analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler
@app.exception_handler(RAGPipelineException)
async def rag_exception_handler(request: Request, exc: RAGPipelineException):
    """Handle RAG Pipeline exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "code": exc.code,
            "path": str(request.url),
        },
    )


# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(rag.router, prefix="/api")


# Static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Pipeline API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
