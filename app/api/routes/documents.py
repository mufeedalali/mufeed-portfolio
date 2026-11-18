"""
Document management routes for the API.

Provides endpoints for document upload and ingestion.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from pathlib import Path
import aiofiles
from app.api.schemas import IngestionTaskResponse, DocumentUploadRequest
from app.api.dependencies import get_ingestion_service, get_settings_instance
from app.core.logging import get_logger
from app.core.exceptions import IngestionError, ValidationError

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=IngestionTaskResponse)
async def upload_document(
    file: UploadFile = File(...),
    ingestion_service=Depends(get_ingestion_service),
    settings=Depends(get_settings_instance),
):
    """
    Upload and ingest a document.

    Args:
        file: Document file to upload
        ingestion_service: Ingestion service instance
        settings: Application settings

    Returns:
        IngestionTaskResponse: Ingestion task status
    """
    try:
        logger.info(f"Uploading document: {file.filename}")

        # Validate file type
        allowed_extensions = [".txt", ".md", ".markdown", ".pdf"]
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}",
            )

        # Save file
        upload_dir = settings.upload_dir_path
        file_path = upload_dir / file.filename

        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Saved file to {file_path}")

        # Ingest document
        task = await ingestion_service.ingest_file(str(file_path))

        return IngestionTaskResponse(
            id=task.id,
            document_id=task.document_id,
            status=task.status.value,
            progress_percent=task.progress_percent,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            error_message=task.error_message,
        )

    except IngestionError as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/ingest-directory", response_model=List[IngestionTaskResponse])
async def ingest_directory(
    directory_path: str,
    ingestion_service=Depends(get_ingestion_service),
):
    """
    Ingest all documents from a directory.

    Args:
        directory_path: Path to directory
        ingestion_service: Ingestion service instance

    Returns:
        List[IngestionTaskResponse]: List of ingestion tasks
    """
    try:
        logger.info(f"Ingesting directory: {directory_path}")

        tasks = await ingestion_service.ingest_directory(directory_path)

        return [
            IngestionTaskResponse(
                id=task.id,
                document_id=task.document_id,
                status=task.status.value,
                progress_percent=task.progress_percent,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat(),
                error_message=task.error_message,
            )
            for task in tasks
        ]

    except IngestionError as e:
        logger.error(f"Directory ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=IngestionTaskResponse)
async def get_task_status(
    task_id: str,
    ingestion_service=Depends(get_ingestion_service),
):
    """
    Get status of an ingestion task.

    Args:
        task_id: Task ID
        ingestion_service: Ingestion service instance

    Returns:
        IngestionTaskResponse: Task status
    """
    try:
        task = await ingestion_service.get_task_status(task_id)

        return IngestionTaskResponse(
            id=task.id,
            document_id=task.document_id,
            status=task.status.value,
            progress_percent=task.progress_percent,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            error_message=task.error_message,
        )

    except IngestionError as e:
        logger.error(f"Task lookup error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tasks", response_model=List[IngestionTaskResponse])
async def get_all_tasks(ingestion_service=Depends(get_ingestion_service)):
    """
    Get all ingestion tasks.

    Args:
        ingestion_service: Ingestion service instance

    Returns:
        List[IngestionTaskResponse]: All tasks
    """
    tasks = await ingestion_service.get_all_tasks()

    return [
        IngestionTaskResponse(
            id=task.id,
            document_id=task.document_id,
            status=task.status.value,
            progress_percent=task.progress_percent,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            error_message=task.error_message,
        )
        for task in tasks
    ]
