"""
IMPLEMENTATION GUIDE - RAG Document Assistant

This guide provides detailed information about the production-quality RAG system
that has been built with all components, patterns, and best practices.
"""

# ============================================================================
# PROJECT OVERVIEW
# ============================================================================

The RAG Document Assistant is a complete, production-ready implementation featuring:

1. CLEAN HEXAGONAL ARCHITECTURE
   - Clear separation of concerns across multiple layers
   - Domain → Infrastructure → Services → API
   - Each layer has well-defined responsibilities

2. DESIGN PATTERNS IMPLEMENTED
   - Strategy Pattern: Pluggable embeddings/LLM providers
   - Repository Pattern: Abstracted data access
   - Factory Pattern: Component creation
   - Dependency Injection: Centralized container

3. PRODUCTION-QUALITY FEATURES
   - Zero external API dependency (mock mode default)
   - Comprehensive error handling with custom exceptions
   - Structured logging with context
   - Type hints throughout (Pydantic validation)
   - SOLID principles adherence

# ============================================================================
# ARCHITECTURE LAYERS
# ============================================================================

LAYER 1: DOMAIN MODELS (app/domain/models.py)
──────────────────────────────────────────────
Business entities with Pydantic validation:
- Document: Uploaded files with metadata
- Chunk: Text segments with embeddings
- Citation: Source references with relevance
- QueryResult: RAG output with citations
- ChatMessage & ChatSession: Conversation management

LAYER 2: CORE INFRASTRUCTURE (app/core/)
─────────────────────────────────────────
- config.py: Settings with validation (Pydantic)
- logging.py: Structured logging (structlog)
- exceptions.py: Custom exception hierarchy
- interfaces.py: Abstract base classes for plugins

LAYER 3: INFRASTRUCTURE LAYER (app/infrastructure/)
────────────────────────────────────────────────────
Implementations of abstract interfaces:

Document Loaders (loaders.py):
- PDFLoader: Extracts text from PDF files
- DocxLoader: Reads Word documents
- TextLoader: Plain text files
- MarkdownLoader: Markdown content
- CSVLoader: Tabular data
- DocumentLoaderFactory: Dynamic loader selection

Text Splitters (splitter.py):
- RecursiveCharacterTextSplitter: Intelligent chunking with overlap
- SimpleCharacterSplitter: Fixed-size chunks
- Preserves semantic boundaries

Embedding Providers (embeddings.py):
- LocalEmbeddingProvider: Hash-based, deterministic, offline
- OpenAIEmbeddingProvider: Production-grade semantic embeddings
- Factory function for provider selection

Vector Store (vector_store.py):
- ChromaVectorStore: ChromaDB integration
- Semantic search with HNSW indexing
- Persistent storage
- Collection management

LLM Services (llm_service.py):
- MockLLMProvider: Deterministic responses (testing)
- OpenAILLMProvider: GPT models with streaming
- Factory function for provider selection

LAYER 4: SERVICES (app/services/)
──────────────────────────────────
Business logic orchestration:

IngestionService:
- Document ingestion pipeline
- Text splitting and chunking
- Embedding generation
- Vector store updates
- Document lifecycle management

RAGService:
- Query embedding generation
- Semantic document retrieval
- Context building
- Citation extraction
- LLM generation coordination

ChatService:
- Session management
- Conversation history
- Context building from chat history
- Message persistence

LAYER 5: API LAYER (app/api/)
─────────────────────────────
FastAPI REST interface:

routes.py: Endpoints
- POST /api/upload: Document ingestion
- POST /api/query: RAG queries with citations
- POST /api/chat: Streaming chat
- GET /api/documents: List documents
- DELETE /api/documents/{id}: Remove document
- POST /api/clear-knowledge-base: Reset system
- GET /api/health: Status check

schemas.py: Pydantic models
- Request/response validation
- OpenAPI documentation
- Type safety

dependencies.py: DI Container
- Centralized service instantiation
- Provider configuration
- Dependency graph management

main.py: FastAPI application
- CORS middleware
- Static file serving
- Startup/shutdown hooks

# ============================================================================
# DESIGN PATTERNS EXPLAINED
# ============================================================================

1. STRATEGY PATTERN
   Interface: EmbeddingProvider, LLMProvider, DocumentLoader, TextSplitter
   Implementations: Multiple concrete strategies
   Benefit: Easy provider switching without code changes
   
   Usage:
   ```python
   provider = create_embedding_provider("local")  # Switch to "openai"
   embeddings = await provider.embed_texts(texts)
   ```

2. FACTORY PATTERN
   Functions: create_embedding_provider(), create_llm_provider()
   Purpose: Centralized component creation
   Benefit: Consistent instantiation, easier testing
   
   Usage:
   ```python
   llm = create_llm_provider("mock")  # Or "openai"
   response = await llm.generate(prompt, context)
   ```

3. REPOSITORY PATTERN
   Class: IngestionService with document storage
   Purpose: Abstract data persistence
   Benefit: Can replace in-memory storage with database
   
   Usage:
   ```python
   service.get_document(doc_id)
   service.delete_document(doc_id)
   ```

4. DEPENDENCY INJECTION
   Container: get_container() singleton
   Purpose: Manage all service dependencies
   Benefit: Easy testing, flexible configuration
   
   Usage:
   ```python
   container = get_container()
   rag_service = container.rag_service
   ```

# ============================================================================
# QUICK START GUIDE
# ============================================================================

1. INSTALLATION
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create configuration
   cp .env.example .env
   ```

2. START SERVER
   ```bash
   # Development with auto-reload
   python -m uvicorn app.api.main:app --reload
   
   # Production
   python main.py
   ```

3. UPLOAD DOCUMENTS
   - Via web UI at http://localhost:8000
   - Or CLI: python -m cli.main ingest data/sample_document_1.txt

4. QUERY DOCUMENTS
   - Via web UI chat interface
   - Or CLI: python -m cli.main query "What is machine learning?"

# ============================================================================
# API USAGE EXAMPLES
# ============================================================================

1. UPLOAD DOCUMENT
   curl -X POST http://localhost:8000/api/upload \
     -F "file=@document.pdf"

2. QUERY WITH RAG
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Explain machine learning"}'

3. STREAMING CHAT
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about Python"}' \
     --header "Accept: text/event-stream"

4. GET DOCUMENTS
   curl http://localhost:8000/api/documents

5. HEALTH CHECK
   curl http://localhost:8000/api/health

# ============================================================================
# CONFIGURATION OPTIONS
# ============================================================================

Core Settings (.env):
- DEBUG: Enable debug mode
- API_HOST/PORT: Server configuration
- LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL
- LOG_FORMAT: json or console

Document Processing:
- CHUNK_SIZE: Text chunk size (default 1000)
- CHUNK_OVERLAP: Overlap between chunks (default 200)
- MAX_FILE_SIZE_MB: Upload limit (default 50)

Embeddings:
- EMBEDDING_MODEL: local, openai, or sentence-transformers
- EMBEDDING_DIMENSION: Vector size (default 384)

LLM:
- LLM_PROVIDER: mock or openai
- LLM_MODEL: Model name (e.g., gpt-4-turbo-preview)
- LLM_TEMPERATURE: Response creativity (0-2)

# ============================================================================
# EXTENDING THE SYSTEM
# ============================================================================

ADD NEW DOCUMENT LOADER
───────────────────────
1. Create class in app/infrastructure/loaders.py
2. Inherit from DocumentLoader interface
3. Implement load() and supported_extensions()
4. Register in DocumentLoaderFactory

Example:
```python
class EPubLoader(DocumentLoader):
    async def load(self, file_path: str) -> str:
        # Implementation
        pass
    
    def supported_extensions(self) -> List[str]:
        return [".epub"]

# Add to factory
DocumentLoaderFactory._loaders[".epub"] = EPubLoader
```

ADD NEW EMBEDDING PROVIDER
──────────────────────────
1. Create class in app/infrastructure/embeddings.py
2. Inherit from EmbeddingProvider interface
3. Implement embed_text() and embed_texts()
4. Update create_embedding_provider() factory

Example:
```python
class HuggingFaceEmbeddings(EmbeddingProvider):
    async def embed_text(self, text: str) -> List[float]:
        # Implementation
        pass
```

ADD NEW LLM PROVIDER
────────────────────
1. Create class in app/infrastructure/llm_service.py
2. Inherit from LLMProvider interface
3. Implement generate() and stream_generate()
4. Update create_llm_provider() factory

# ============================================================================
# TESTING STRATEGY
# ============================================================================

Test Pyramid:
- Unit Tests: Core components (splitter, embeddings)
- Integration Tests: Service layer interactions
- E2E Tests: API endpoints

Running Tests:
```bash
pytest tests/ -v                    # All tests
pytest tests/test_splitter.py -v   # Specific file
pytest --cov=app                   # Coverage report
```

Test Areas Covered:
- Text splitting logic
- Embedding generation
- Vector search
- Query processing
- Error handling

# ============================================================================
# PERFORMANCE CONSIDERATIONS
# ============================================================================

Chunking Strategy:
- Recursive splitting preserves semantic boundaries
- Overlap ensures context continuity
- Configurable for memory vs quality tradeoff

Vector Search:
- HNSW indexing for O(log N) search
- Top-K retrieval (default 5)
- Cosine similarity scoring

Streaming:
- SSE for real-time response chunks
- Reduces perceived latency
- Better user experience

Caching:
- ChatService maintains session history
- Can be extended with Redis
- Reduces duplicate processing

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

Docker Deployment:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0"]
```

Environment Setup:
- Use different .env files per environment
- Set OPENAI_API_KEY from secrets manager
- Configure log level appropriately
- Enable CORS for frontend domain

Monitoring:
- Structured logging for aggregation
- Slow query tracking
- Error rate monitoring
- Token usage tracking (if using OpenAI)

# ============================================================================
# COMMON OPERATIONS
# ============================================================================

CLI OPERATIONS
──────────────
# Ingest document
python -m cli.main ingest data/document.pdf

# Query
python -m cli.main query "Your question"

# Chat (interactive)
python -m cli.main chat

# List documents
python -m cli.main documents

# Statistics
python -m cli.main stats

# Clear all (with confirmation)
python -m cli.main clear

TROUBLESHOOTING
───────────────
Issue: Import errors
Solution: Ensure virtual env activated, deps installed

Issue: "No documents" error
Solution: Upload documents first

Issue: Slow queries
Solution: Reduce retrieval_top_k, optimize chunk size

Issue: Out of memory
Solution: Reduce chunk_size, split large files

# ============================================================================
# FILES STRUCTURE
# ============================================================================

Core Application:
✓ app/core/config.py - Configuration management
✓ app/core/logging.py - Structured logging setup
✓ app/core/exceptions.py - Custom exceptions
✓ app/core/interfaces.py - Abstract interfaces

Domain Models:
✓ app/domain/models.py - Business entities

Infrastructure:
✓ app/infrastructure/loaders.py - Document loaders
✓ app/infrastructure/splitter.py - Text splitting
✓ app/infrastructure/embeddings.py - Embedding providers
✓ app/infrastructure/vector_store.py - ChromaDB integration
✓ app/infrastructure/llm_service.py - LLM providers

Services:
✓ app/services/ingestion_service.py - Document ingestion
✓ app/services/rag_service.py - RAG queries
✓ app/services/chat_service.py - Chat management

API:
✓ app/api/main.py - FastAPI app
✓ app/api/routes.py - API endpoints
✓ app/api/schemas.py - Request/response models
✓ app/api/dependencies.py - DI container

Frontend:
✓ app/static/index.html - Web UI
✓ app/static/style.css - Styling
✓ app/static/app.js - Frontend logic

CLI:
✓ cli/main.py - Command-line interface

Tests:
✓ tests/test_splitter.py - Splitter tests
✓ tests/test_embeddings.py - Embedding tests

Configuration:
✓ requirements.txt - Python dependencies
✓ .env.example - Environment template
✓ .gitignore - Git ignore rules
✓ README.md - Documentation

Data:
✓ data/sample_document_1.txt - Sample document
✓ data/sample_document_2.txt - Sample document
✓ data/uploads/ - Upload directory
✓ data/chroma_db/ - Vector database

# ============================================================================
# SUCCESS CHECKLIST
# ============================================================================

Before deployment, verify:
□ All dependencies installed
□ .env configured properly
□ Sample documents uploaded
□ Test queries return results with citations
□ Chat interface works
□ CLI tool functions
□ Tests pass (pytest tests/)
□ No console errors
□ API endpoints respond
□ Static files served
□ Logging configured

# ============================================================================
# NEXT STEPS
# ============================================================================

1. Run tests to verify everything works
2. Upload sample documents via web UI or CLI
3. Test queries and verify citations
4. Customize configuration in .env
5. Deploy to production with Docker
6. Monitor logs and performance
7. Extend with additional providers as needed

# ============================================================================
"""
