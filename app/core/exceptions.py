"""
Custom exception classes for the RAG Pipeline application.

Provides domain-specific exceptions for error handling throughout the application.
"""


class RAGPipelineException(Exception):
    """Base exception for all RAG Pipeline errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        """
        Initialize RAG Pipeline exception.

        Args:
            message: Error message
            code: Error code for categorization
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class DocumentLoadError(RAGPipelineException):
    """Raised when document loading fails."""

    def __init__(self, message: str):
        super().__init__(message, "DOCUMENT_LOAD_ERROR")


class DocumentParsingError(RAGPipelineException):
    """Raised when document parsing fails."""

    def __init__(self, message: str):
        super().__init__(message, "DOCUMENT_PARSING_ERROR")


class TextSplittingError(RAGPipelineException):
    """Raised when text splitting fails."""

    def __init__(self, message: str):
        super().__init__(message, "TEXT_SPLITTING_ERROR")


class EmbeddingError(RAGPipelineException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str):
        super().__init__(message, "EMBEDDING_ERROR")


class VectorStoreError(RAGPipelineException):
    """Raised when vector store operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "VECTOR_STORE_ERROR")


class LLMError(RAGPipelineException):
    """Raised when LLM operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR")


class IngestionError(RAGPipelineException):
    """Raised when document ingestion fails."""

    def __init__(self, message: str):
        super().__init__(message, "INGESTION_ERROR")


class RetrievalError(RAGPipelineException):
    """Raised when retrieval operations fail."""

    def __init__(self, message: str):
        super().__init__(message, "RETRIEVAL_ERROR")


class ValidationError(RAGPipelineException):
    """Raised when validation fails."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class ConfigurationError(RAGPipelineException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")


class FileNotFoundError(RAGPipelineException):
    """Raised when required file is not found."""

    def __init__(self, message: str):
        super().__init__(message, "FILE_NOT_FOUND")


class InvalidFormatError(RAGPipelineException):
    """Raised when file format is invalid."""

    def __init__(self, message: str):
        super().__init__(message, "INVALID_FORMAT")
