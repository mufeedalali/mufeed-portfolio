"""FastAPI application entry point for production deployment."""

from app.api.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings

    settings = get_settings()

    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
