# RAG Pipeline — AI Document Assistant

A production-ready Retrieval-Augmented Generation (RAG) system for querying documents with AI-powered answers backed by citations.

## Features

- **Multi-format Document Support**: PDF, DOCX, TXT, CSV, Markdown
- **Advanced Text Splitting**: Recursive character splitting with semantic overlap
- **Flexible Embeddings**: Mock (offline), OpenAI, or Sentence Transformers
- **Vector Storage**: ChromaDB for efficient retrieval
- **LLM Agnostic**: Mock provider for offline development, OpenAI integration
- **Streaming Responses**: Server-Sent Events (SSE) for real-time answers
- **Modern Web UI**: Dark mode chat interface with document management
- **Interactive CLI**: Command-line tools for ingestion, querying, and chat
- **Comprehensive Logging**: Structured logging throughout
- **Type-Safe**: Full type hints and Pydantic validation
- **SOLID Architecture**: Clean separation of concerns

## Project Structure

```
app/
├── core/                    # Configuration, logging, exceptions
│   ├── config.py           # Settings with environment loading
│   ├── logging.py          # Structured logging setup
│   └── exceptions.py       # Custom exception hierarchy
├── domain/                 # Domain models and interfaces
│   ├── models.py           # Pydantic models (Document, Chunk, etc.)
│   └── interfaces.py       # Abstract base classes (IDocumentLoader, IVectorStore, etc.)
├── infrastructure/         # Implementation layer
│   ├── document_loaders.py # PDF, DOCX, TXT, CSV, MD parsers
│   ├── text_splitter.py    # Recursive character splitting
│   ├── embeddings.py       # Mock, OpenAI, Sentence Transformers
│   ├── vector_store.py     # ChromaDB implementation
│   └── llm_service.py      # Mock and OpenAI LLM providers
├── services/               # Business logic orchestration
│   ├── ingestion_service.py    # Document pipeline
│   ├── rag_service.py          # Query orchestration
│   ├── chat_service.py         # Session management
│   └── document_repository.py  # Document storage
├── api/                    # FastAPI application
│   ├── main.py            # App initialization, middleware
│   ├── schemas.py         # Request/response Pydantic models
│   ├── dependencies.py    # DI container
│   └── routes/
│       ├── health.py      # Health checks
│       ├── documents.py   # Upload, list, delete
│       └── rag.py         # Query and streaming
└── static/                # Web UI
    ├── index.html         # Chat interface
    ├── style.css          # Dark mode styling
    └── app.js             # Frontend client
cli/
├── main.py               # Interactive CLI with ingest, query, chat
sample_documents/        # Example files
tests/
├── test_splitter.py      # Text splitting tests
└── test_embeddings.py    # Embedding tests
requirements.txt          # Python dependencies
.env.example             # Environment template
README.md                # This file
```

## Installation

### Prerequisites

- Python 3.9+
- pip or conda

### Setup

1. **Clone repository**
```bash
git clone <repository>
cd mufeed-portfolio
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings (optional - defaults work offline)
```

## Quick Start

### Web UI

```bash
# Start the FastAPI server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Visit http://localhost:8000
```

1. Upload documents using the web interface
2. Ask questions about your documents
3. View answers with citations

### CLI

```bash
# Ingest a document
python -m cli.main ingest path/to/document.pdf

# List ingested documents
python -m cli.main list

# Query documents
python -m cli.main query "What is this document about?"

# Interactive chat
python -m cli.main chat
```

## Configuration

Create `.env` file with these variables (or use defaults):

```env
# Application
DEBUG=False
LOG_LEVEL=INFO

# Embeddings (mock, openai, sentence-transformers)
EMBEDDING_MODEL=mock
EMBEDDING_DIMENSION=384

# LLM (mock, openai)
LLM_PROVIDER=mock
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7

# Vector Store
RETRIEVAL_TOP_K=5

# OpenAI (if using OpenAI models)
OPENAI_API_KEY=sk-...
```

## API Endpoints

### Health
- `GET /health` - Service status
- `GET /health/config` - Configuration info

### Documents
- `POST /documents/upload` - Upload document (async processing)
- `GET /documents/` - List documents
- `DELETE /documents/{id}` - Delete document

### RAG
- `POST /rag/query` - Query with answer and citations
- `POST /rag/query/stream` - Query with streaming response
- `POST /rag/chat/stream` - Chat interface with streaming

## Architecture

### Clean Architecture Layers

1. **Domain Layer** (`domain/`)
   - Domain models (Document, Chunk, Citation, QueryResult)
   - Interfaces defining contracts for implementations
   - No external dependencies

2. **Infrastructure Layer** (`infrastructure/`)
   - Concrete implementations of domain interfaces
   - Document loading (PDF, DOCX, TXT, CSV, MD)
   - Text splitting algorithms
   - Embedding providers
   - Vector store operations
   - LLM providers

3. **Services Layer** (`services/`)
   - Orchestrates domain objects and infrastructure
   - Business logic without framework coupling
   - Transaction management
   - Cross-cutting concerns

4. **API Layer** (`api/`)
   - FastAPI routes
   - Request/response schemas
   - Dependency injection
   - Middleware

### Key Design Patterns

- **Factory Pattern**: DocumentLoaderFactory, LLMProviderFactory
- **Strategy Pattern**: Multiple embeddings/LLM providers implementing same interface
- **Repository Pattern**: InMemoryDocumentRepository
- **Dependency Injection**: DIContainer for singletons
- **Service Locator**: get_rag_service(), get_ingestion_service()

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_embeddings.py -v
```

### Adding New Document Formats

1. Create loader in `infrastructure/document_loaders.py`
2. Implement `IDocumentLoader` interface
3. Register in `DocumentLoaderFactory`

### Adding New Embeddings

1. Create provider in `infrastructure/embeddings.py`
2. Implement `IEmbeddingProvider` interface
3. Update `DIContainer.get_embedding_provider()`

## Production Considerations

### Recommended Changes

1. **Database**: Replace InMemoryDocumentRepository with PostgreSQL/MongoDB
2. **Authentication**: Add API key or OAuth2 authentication
3. **Rate Limiting**: Implement rate limiting middleware
4. **Caching**: Add Redis caching for embeddings
5. **Monitoring**: Integrate with APM (Datadog, New Relic)
6. **Error Handling**: Implement exponential backoff for API calls
7. **Testing**: Add integration tests with real APIs

### Performance Tuning

- Batch embedding generation for multiple chunks
- Implement caching for frequently accessed embeddings
- Use async/await throughout for I/O operations
- Consider vector quantization for large databases

### Security

- Sanitize file uploads
- Validate all API inputs
- Use environment variables for secrets (never hardcode)
- Implement proper CORS settings
- Add request rate limiting

## Example Usage

### Python API

```python
from app.infrastructure.embeddings import MockEmbeddingProvider
from app.infrastructure.vector_store import ChromaVectorStore
from app.infrastructure.llm_service import MockLLMProvider
from app.services.rag_service import RAGService

# Initialize components
embedding_provider = MockEmbeddingProvider()
vector_store = ChromaVectorStore(persist_directory="./data/vector_db")
llm_provider = MockLLMProvider()

# Create RAG service
rag_service = RAGService(
    embedding_provider=embedding_provider,
    vector_store=vector_store,
    llm_provider=llm_provider,
    top_k=5
)

# Query documents
result = await rag_service.query("What is the main topic?")
print(result.answer)
for citation in result.citations:
    print(f"- {citation.document_name}")
```

### Web UI

1. Open browser to `http://localhost:8000`
2. Upload PDF/DOCX/TXT/CSV/Markdown files
3. Ask questions using the chat interface
4. View answers with source citations

### CLI

```bash
# Upload documents
python -m cli.main ingest data/sample.pdf
python -m cli.main ingest data/document.docx

# List documents
python -m cli.main list

# Query
python -m cli.main query "What are the key findings?"

# Interactive chat
python -m cli.main chat
```

## Troubleshooting

### Import Errors

Ensure you're running from project root and have installed dependencies:
```bash
pip install -r requirements.txt
```

### CORS Issues

Check `app/api/main.py` CORS middleware configuration. In production, restrict origins:
```python
allow_origins=["https://yourdomain.com"]
```

### Out of Memory with Large Files

Adjust chunk size and batch sizes:
```env
CHUNK_SIZE=500
```

### Slow Embeddings

For development, use MockEmbeddingProvider (default). For production, use:
- OpenAI (fastest, requires API key)
- Sentence Transformers (good balance)

## License

MIT

## Support

For issues, questions, or contributions, please open an issue on the repository.
