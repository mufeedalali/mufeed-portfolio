"""
Document loader implementations for various file formats.

Supports PDF, Markdown, Text, and DOCX files with async operations.
"""

import asyncio
from pathlib import Path
from typing import Optional, List
from app.core.exceptions import (
    DocumentLoadError,
    DocumentParsingError,
    InvalidFormatError,
    FileNotFoundError as RAGFileNotFoundError,
)
from app.domain.models import Document, DocumentType
from app.domain.interfaces import DocumentLoader
from app.core.logging import get_logger
import uuid

logger = get_logger(__name__)


class TextFileLoader(DocumentLoader):
    """Loader for plain text files."""

    async def load(self, file_path: str) -> Document:
        """
        Load a text file.

        Args:
            file_path: Path to text file

        Returns:
            Document: Loaded document

        Raises:
            DocumentLoadError: If loading fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise RAGFileNotFoundError(f"File not found: {file_path}")

            content = await asyncio.to_thread(path.read_text, encoding="utf-8")
            logger.info(f"Loaded text file: {file_path}")

            return Document(
                id=str(uuid.uuid4()),
                filename=path.name,
                content=content,
                document_type=DocumentType.TEXT,
                source_path=str(path.absolute()),
                metadata={"size_bytes": path.stat().st_size},
            )
        except RAGFileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise DocumentLoadError(f"Failed to load text file: {str(e)}")

    async def supports(self, file_path: str) -> bool:
        """Check if file is a text file."""
        return file_path.lower().endswith(".txt")


class MarkdownFileLoader(DocumentLoader):
    """Loader for Markdown files."""

    async def load(self, file_path: str) -> Document:
        """
        Load a Markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Document: Loaded document

        Raises:
            DocumentLoadError: If loading fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise RAGFileNotFoundError(f"File not found: {file_path}")

            content = await asyncio.to_thread(path.read_text, encoding="utf-8")
            logger.info(f"Loaded markdown file: {file_path}")

            return Document(
                id=str(uuid.uuid4()),
                filename=path.name,
                content=content,
                document_type=DocumentType.MARKDOWN,
                source_path=str(path.absolute()),
                metadata={"size_bytes": path.stat().st_size},
            )
        except RAGFileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error loading markdown file {file_path}: {str(e)}")
            raise DocumentLoadError(f"Failed to load markdown file: {str(e)}")

    async def supports(self, file_path: str) -> bool:
        """Check if file is a markdown file."""
        return file_path.lower().endswith((".md", ".markdown"))


class PDFFileLoader(DocumentLoader):
    """Loader for PDF files (basic implementation)."""

    async def load(self, file_path: str) -> Document:
        """
        Load a PDF file (simplified for offline operation).

        Args:
            file_path: Path to PDF file

        Returns:
            Document: Loaded document

        Raises:
            DocumentLoadError: If loading fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise RAGFileNotFoundError(f"File not found: {file_path}")

            # For offline operation, read raw bytes and convert to text
            # In production, use pypdf or pdfplumber
            raw_bytes = await asyncio.to_thread(path.read_bytes)

            # Extract ASCII text from PDF (basic implementation)
            content = raw_bytes.decode("utf-8", errors="ignore")
            content = "\n".join(
                line for line in content.split("\n") if line.strip()
            )

            logger.info(f"Loaded PDF file: {file_path}")

            return Document(
                id=str(uuid.uuid4()),
                filename=path.name,
                content=content,
                document_type=DocumentType.PDF,
                source_path=str(path.absolute()),
                metadata={"size_bytes": path.stat().st_size},
            )
        except RAGFileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {str(e)}")
            raise DocumentLoadError(f"Failed to load PDF file: {str(e)}")

    async def supports(self, file_path: str) -> bool:
        """Check if file is a PDF file."""
        return file_path.lower().endswith(".pdf")


class DocumentLoaderFactory:
    """Factory for creating appropriate document loaders."""

    def __init__(self):
        """Initialize with available loaders."""
        self.loaders: List[DocumentLoader] = [
            TextFileLoader(),
            MarkdownFileLoader(),
            PDFFileLoader(),
        ]

    async def load(self, file_path: str) -> Document:
        """
        Load document using appropriate loader.

        Args:
            file_path: Path to document file

        Returns:
            Document: Loaded document

        Raises:
            DocumentLoadError: If no loader supports the file
        """
        for loader in self.loaders:
            if await loader.supports(file_path):
                return await loader.load(file_path)

        raise InvalidFormatError(
            f"No loader found for file type: {Path(file_path).suffix}"
        )

    def register_loader(self, loader: DocumentLoader) -> None:
        """
        Register a new document loader.

        Args:
            loader: Loader instance to register
        """
        self.loaders.append(loader)
        logger.info(f"Registered loader: {loader.__class__.__name__}")

    async def load_directory(self, directory_path: str) -> List[Document]:
        """
        Load all documents from a directory.

        Args:
            directory_path: Path to directory

        Returns:
            List[Document]: List of loaded documents
        """
        docs = []
        dir_path = Path(directory_path)

        if not dir_path.exists():
            raise RAGFileNotFoundError(f"Directory not found: {directory_path}")

        for file_path in dir_path.glob("*"):
            if file_path.is_file():
                try:
                    doc = await self.load(str(file_path))
                    docs.append(doc)
                    logger.info(f"Loaded document: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Skipped file {file_path.name}: {str(e)}")

        logger.info(f"Loaded {len(docs)} documents from {directory_path}")
        return docs
