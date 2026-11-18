"""Document loaders for multiple file formats."""

import os
from pathlib import Path
from typing import List
from abc import abstractmethod
from app.core.interfaces import DocumentLoader
from app.core.exceptions import DocumentIngestionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFLoader(DocumentLoader):
    """Loader for PDF files."""

    async def load(self, file_path: str) -> str:
        """Load content from a PDF file."""
        try:
            import PyPDF2

            content = []
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        content.append(f"--- Page {page_num + 1} ---\n{text}")

            return "\n".join(content)
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise DocumentIngestionError(f"Failed to load PDF: {str(e)}")

    def supported_extensions(self) -> List[str]:
        return [".pdf"]


class DocxLoader(DocumentLoader):
    """Loader for DOCX files."""

    async def load(self, file_path: str) -> str:
        """Load content from a DOCX file."""
        try:
            from docx import Document

            doc = Document(file_path)
            content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    content.append(para.text)

            return "\n".join(content)
        except Exception as e:
            logger.error(f"Error loading DOCX {file_path}: {str(e)}")
            raise DocumentIngestionError(f"Failed to load DOCX: {str(e)}")

    def supported_extensions(self) -> List[str]:
        return [".docx"]


class TextLoader(DocumentLoader):
    """Loader for plain text files."""

    async def load(self, file_path: str) -> str:
        """Load content from a text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise DocumentIngestionError(f"Failed to load text file: {str(e)}")

    def supported_extensions(self) -> List[str]:
        return [".txt"]


class MarkdownLoader(DocumentLoader):
    """Loader for Markdown files."""

    async def load(self, file_path: str) -> str:
        """Load content from a Markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error loading Markdown file {file_path}: {str(e)}")
            raise DocumentIngestionError(f"Failed to load Markdown file: {str(e)}")

    def supported_extensions(self) -> List[str]:
        return [".md", ".markdown"]


class CSVLoader(DocumentLoader):
    """Loader for CSV files."""

    async def load(self, file_path: str) -> str:
        """Load content from a CSV file."""
        try:
            import csv

            content = []
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    content.append(" | ".join(f"{k}: {v}" for k, v in row.items()))

            return "\n".join(content)
        except Exception as e:
            logger.error(f"Error loading CSV {file_path}: {str(e)}")
            raise DocumentIngestionError(f"Failed to load CSV: {str(e)}")

    def supported_extensions(self) -> List[str]:
        return [".csv"]


class DocumentLoaderFactory:
    """Factory for creating document loaders based on file type."""

    _loaders = {
        ".pdf": PDFLoader,
        ".docx": DocxLoader,
        ".txt": TextLoader,
        ".md": MarkdownLoader,
        ".markdown": MarkdownLoader,
        ".csv": CSVLoader,
    }

    @classmethod
    def create_loader(cls, file_path: str) -> DocumentLoader:
        """Create appropriate loader for file type."""
        ext = Path(file_path).suffix.lower()

        if ext not in cls._loaders:
            raise DocumentIngestionError(
                f"Unsupported file type: {ext}. Supported: {list(cls._loaders.keys())}"
            )

        return cls._loaders[ext]()

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get all supported file extensions."""
        return list(cls._loaders.keys())
