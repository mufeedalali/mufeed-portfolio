"""API routes for RAG document assistant."""

import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
import aiofiles

from app.api.schemas import (
    DocumentUploadResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    ChatRequest,
    ChatResponse,
    KnowledgeBaseStatsResponse,
    HealthCheckResponse,
    DocumentInfo,
)
from app.api.dependencies import get_container
from app.core.exceptions import RAGException, DocumentIngestionError
from app.core.logging import get_logger
from app.infrastructure.loaders import DocumentLoaderFactory

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    container = get_container()
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        embedding_provider=container.embedding_provider.__class__.__name__,
        llm_provider=container.llm_provider.__class__.__name__,
    )


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a document."""
    try:
        container = get_container()
        ingestion_service = container.ingestion_service

        # Validate file type
        supported_exts = DocumentLoaderFactory.get_supported_extensions()
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in supported_exts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_ext}",
            )

        # Save uploaded file temporarily
        temp_dir = Path("data/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / file.filename

        async with aiofiles.open(temp_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        try:
            # Ingest document
            document = await ingestion_service.ingest_document(str(temp_path))

            return DocumentUploadResponse(
                id=document.id,
                filename=document.filename,
                file_type=document.file_type,
                chunk_count=document.chunk_count,
                size_bytes=document.size_bytes,
                upload_date=document.upload_date,
            )
        finally:
            # Clean up temporary file
            if temp_path.exists():
                os.remove(temp_path)

    except DocumentIngestionError as e:
        logger.error(f"Document ingestion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading document",
        )


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """Process a RAG query."""
    try:
        container = get_container()
        rag_service = container.rag_service

        response = await rag_service.query(request.query)

        # Convert domain model to schema
        citations = [
            {
                "document_id": c.document_id,
                "filename": c.filename,
                "chunk_index": c.chunk_index,
                "snippet": c.snippet,
                "relevance_score": c.relevance_score,
            }
            for c in response.citations
        ]

        return RAGQueryResponse(
            query=response.query,
            answer=response.answer,
            citations=citations,
            model=response.model,
            processing_time_ms=response.processing_time_ms,
            tokens_used=response.tokens_used,
        )

    except RAGException as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing query",
        )


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint with streaming response."""
    try:
        container = get_container()
        chat_service = container.chat_service

        async def generate():
            try:
                async for chunk in chat_service.stream_chat(request.message):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Error in chat streaming: {str(e)}")
                yield f"data: Error: {str(e)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing chat",
        )


@router.get("/documents", response_model=KnowledgeBaseStatsResponse)
async def get_documents():
    """Get list of ingested documents and statistics."""
    try:
        container = get_container()
        ingestion_service = container.ingestion_service

        stats = ingestion_service.get_stats()

        documents = [
            DocumentInfo(
                id=doc["id"],
                filename=doc["filename"],
                chunk_count=doc["chunk_count"],
                size_bytes=doc["size_bytes"],
                upload_date=doc["upload_date"],
            )
            for doc in stats["documents"]
        ]

        return KnowledgeBaseStatsResponse(
            total_documents=stats["total_documents"],
            total_chunks=stats["total_chunks"],
            total_size_bytes=stats["total_size_bytes"],
            documents=documents,
        )

    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting documents",
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base."""
    try:
        container = get_container()
        ingestion_service = container.ingestion_service

        document = ingestion_service.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        await ingestion_service.delete_document(document_id)

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document",
        )


@router.post("/clear-knowledge-base")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base."""
    try:
        container = get_container()
        ingestion_service = container.ingestion_service

        # Delete all documents
        for doc_id in list(ingestion_service.documents.keys()):
            await ingestion_service.delete_document(doc_id)

        return {"message": "Knowledge base cleared successfully"}

    except Exception as e:
        logger.error(f"Error clearing knowledge base: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing knowledge base",
        )
