"""
Domain models for the RAG Pipeline application.

Defines core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    DOCX = "docx"


class ProcessingStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """
    Represents a document in the system.

    Attributes:
        id: Unique document identifier
        filename: Original filename
        content: Full document content
        document_type: Type of document (PDF, Markdown, Text, etc.)
        source_path: Path where document was loaded from
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional metadata about the document
    """

    id: str
    filename: str
    content: str
    document_type: DocumentType
    source_path: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate document after initialization."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Document ID must be a non-empty string")
        if not self.filename:
            raise ValueError("Filename is required")
        if not self.content:
            raise ValueError("Document content cannot be empty")


@dataclass
class TextChunk:
    """
    Represents a chunk of text from a document.

    Attributes:
        id: Unique chunk identifier
        document_id: ID of source document
        content: Chunk content
        chunk_index: Sequential index within document
        start_char: Starting character position in original document
        end_char: Ending character position in original document
        metadata: Additional metadata about the chunk
    """

    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate chunk after initialization."""
        if not self.id:
            raise ValueError("Chunk ID is required")
        if not self.content:
            raise ValueError("Chunk content cannot be empty")
        if self.start_char < 0 or self.end_char <= self.start_char:
            raise ValueError("Invalid character positions")


@dataclass
class Embedding:
    """
    Represents an embedding vector.

    Attributes:
        chunk_id: ID of chunk that was embedded
        vector: Embedding vector (list of floats)
        model: Model used to generate embedding
        dimension: Dimension of the embedding
        created_at: Creation timestamp
    """

    chunk_id: str
    vector: List[float]
    model: str
    dimension: int
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate embedding after initialization."""
        if not self.chunk_id:
            raise ValueError("Chunk ID is required")
        if not self.vector or len(self.vector) != self.dimension:
            raise ValueError(f"Vector dimension must be {self.dimension}")


@dataclass
class RetrievalResult:
    """
    Represents a retrieval result from the vector store.

    Attributes:
        chunk_id: ID of retrieved chunk
        document_id: ID of source document
        filename: Name of source document
        content: Content of the chunk
        similarity_score: Similarity score (0-1)
        metadata: Metadata from the chunk
    """

    chunk_id: str
    document_id: str
    filename: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate retrieval result."""
        if not 0 <= self.similarity_score <= 1:
            raise ValueError("Similarity score must be between 0 and 1")


@dataclass
class RAGResponse:
    """
    Represents a RAG system response.

    Attributes:
        query: Original user query
        answer: Generated answer
        retrieved_chunks: List of retrieved chunks used
        sources: List of source documents
        confidence_score: Overall confidence score
        generation_time_ms: Time taken to generate response
    """

    query: str
    answer: str
    retrieved_chunks: List[RetrievalResult] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    generation_time_ms: float = 0.0

    def __post_init__(self):
        """Validate RAG response."""
        if not self.query:
            raise ValueError("Query is required")
        if not self.answer:
            raise ValueError("Answer is required")
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("Confidence score must be between 0 and 1")


@dataclass
class ChatMessage:
    """
    Represents a message in a chat conversation.

    Attributes:
        id: Unique message identifier
        conversation_id: ID of the conversation
        role: Role of message author (user, assistant, system)
        content: Message content
        timestamp: When message was created
        metadata: Additional metadata
    """

    id: str
    conversation_id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate chat message."""
        if self.role not in ("user", "assistant", "system"):
            raise ValueError("Role must be 'user', 'assistant', or 'system'")
        if not self.content:
            raise ValueError("Content is required")


@dataclass
class IngestionTask:
    """
    Represents a document ingestion task.

    Attributes:
        id: Unique task identifier
        document_id: Associated document ID
        status: Processing status
        progress_percent: Progress percentage (0-100)
        created_at: Task creation time
        updated_at: Last update time
        error_message: Error message if failed
        metadata: Task metadata
    """

    id: str
    document_id: str
    status: ProcessingStatus
    progress_percent: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate ingestion task."""
        if not 0 <= self.progress_percent <= 100:
            raise ValueError("Progress percent must be between 0 and 100")
