"""Health check and service status routes."""

import datetime

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Service health status and version
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.datetime.utcnow().isoformat()
    )


@router.get("/config")
async def config_info():
    """
    Get configuration information.

    Returns:
        Current configuration (sensitive values masked)
    """
    config = {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "retrieval_top_k": settings.retrieval_top_k,
        "upload_dir": str(settings.upload_dir),
        "vector_db_dir": str(settings.vector_db_dir),
        "log_level": settings.log_level,
        "log_format": settings.log_format,
    }

    # Mask OpenAI key if present
    if settings.openai_api_key:
        config["openai_api_key"] = f"******{settings.openai_api_key[-4:]}"
    else:
        config["openai_api_key"] = None

    return config
