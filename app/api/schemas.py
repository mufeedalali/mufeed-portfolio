"""API request and response schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Document Schemas

class DocumentUploadRequest(BaseModel):
    """Request schema for document upload."""

    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="Document type (pdf, docx, txt, csv, md)")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class DocumentResponse(BaseModel):
    """Response schema for document."""

    id: UUID = Field(..., description="Document ID")
    filename: str = Field(..., description="Filename")
    file_type: str = Field(..., description="Document type")
    status: str = Field(..., description="Processing status")
    chunk_count: int = Field(..., description="Number of chunks")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class DocumentListResponse(BaseModel):
    """Response schema for document list."""

    documents: List[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total count")
    skip: int = Field(..., description="Skip value")
    limit: int = Field(..., description="Limit value")


# Query Schemas

class QueryRequest(BaseModel):
    """Request schema for query."""

    query: str = Field(..., description="Query text")
    document_id: Optional[UUID] = Field(None, description="Optional document to filter by")


class CitationResponse(BaseModel):
    """Response schema for citation."""

    document_name: str = Field(..., description="Source document")
    text: str = Field(..., description="Cited text excerpt")
    relevance_score: float = Field(..., description="Relevance score")
    chunk_index: int = Field(..., description="Chunk position")


class QueryResponse(BaseModel):
    """Response schema for query result."""

    query_id: UUID = Field(..., description="Query ID")
    answer: str = Field(..., description="Generated answer")
    citations: List[CitationResponse] = Field(..., description="Source citations")
    retrieval_time_ms: float = Field(..., description="Retrieval time in ms")
    generation_time_ms: float = Field(..., description="Generation time in ms")
    total_time_ms: float = Field(..., description="Total time in ms")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class QueryStreamChunk(BaseModel):
    """Response schema for streaming query chunk."""

    type: str = Field(..., description="Chunk type: citations, chunk, metadata")
    data: dict = Field(..., description="Chunk data")


# Chat Schemas

class ChatMessageRequest(BaseModel):
    """Request schema for chat message."""

    message: str = Field(..., description="Message content")
    session_id: Optional[UUID] = Field(None, description="Optional session ID")


class ChatMessageResponse(BaseModel):
    """Response schema for chat message."""

    id: UUID = Field(..., description="Message ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class ChatSessionResponse(BaseModel):
    """Response schema for chat session."""

    id: UUID = Field(..., description="Session ID")
    title: Optional[str] = Field(None, description="Session title")
    message_count: int = Field(..., description="Number of messages")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class ChatSessionListResponse(BaseModel):
    """Response schema for chat session list."""

    sessions: List[ChatSessionResponse] = Field(..., description="List of sessions")


class ChatStreamChunk(BaseModel):
    """Response schema for streaming chat chunk."""

    type: str = Field(..., description="Chunk type: chunk, metadata, citations")
    data: dict = Field(..., description="Chunk data")


# Health Schemas

class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")


# Error Schemas

class ErrorResponse(BaseModel):
    """Response schema for errors."""

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[dict] = Field(None, description="Additional error details")
