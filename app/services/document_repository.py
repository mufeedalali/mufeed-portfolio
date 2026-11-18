"""In-memory document repository implementation."""

from typing import Optional
from uuid import UUID

from app.domain.interfaces import IDocumentRepository
from app.domain.models import Document


class InMemoryDocumentRepository(IDocumentRepository):
    """In-memory implementation of document repository for demo purposes."""

    def __init__(self):
        """Initialize repository."""
        self.documents: dict[UUID, Document] = {}

    async def save(self, document: Document) -> Document:
        """
        Save document metadata.

        Args:
            document: Document to save

        Returns:
            Saved document
        """
        self.documents[document.id] = document
        return document

    async def get(self, document_id: UUID) -> Optional[Document]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        return self.documents.get(document_id)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """
        List all documents.

        Args:
            skip: Number of documents to skip
            limit: Maximum number to return

        Returns:
            List of documents
        """
        all_docs = list(self.documents.values())
        return all_docs[skip:skip + limit]

    async def delete(self, document_id: UUID) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False

    async def update(self, document: Document) -> Document:
        """
        Update document metadata.

        Args:
            document: Document with updated fields

        Returns:
            Updated document
        """
        self.documents[document.id] = document
        return document
