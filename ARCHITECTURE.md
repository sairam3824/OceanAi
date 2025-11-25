# QA Test Agent - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                    http://localhost:8501                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                            │
│                     (frontend/app.py)                            │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Document   │  │  Test Case   │  │   Selenium   │         │
│  │    Upload    │  │  Generation  │  │    Script    │         │
│  │     Tab      │  │     Tab      │  │     Tab      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                     (backend/main.py)                            │
│                   http://localhost:8000                          │
│                                                                   │
│  API Endpoints:                                                  │
│  • POST /api/upload              - Upload documents             │
│  • POST /api/upload_html         - Submit HTML content          │
│  • POST /api/build_kb            - Build knowledge base         │
│  • POST /api/generate_tests      - Generate test cases          │
│  • POST /api/generate_script     - Generate Selenium script     │
│  • GET  /api/upload_history      - Get upload sessions          │
│  • GET  /api/script_history      - Get script sessions          │
│  • POST /api/reset_script_session - Reset script session        │
│  • DELETE /api/clear             - Clear all data               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           INGESTION PIPELINE (ingest.py)                  │  │
│  │                                                            │  │
│  │  DocumentExtractor → DocumentChunker → EmbeddingGenerator │  │
│  │        ↓                  ↓                    ↓          │  │
│  │    .txt, .md          Chunks with          384-dim        │  │
│  │    .pdf, .json        metadata             vectors        │  │
│  │    .html                                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              RAG ENGINE (rag_engine.py)                   │  │
│  │                                                            │  │
│  │  Query → Embed → Retrieve → Build Prompt → LLM → Parse   │  │
│  │                      ↓                                     │  │
│  │                  Top-K Chunks                              │  │
│  │                                                            │  │
│  │  PromptBuilder:                                            │  │
│  │  • Test generation prompts                                │  │
│  │  • Script generation prompts                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        SELENIUM GENERATOR (selenium_gen.py)               │  │
│  │                                                            │  │
│  │  HTMLParser → Extract Selectors → Build Prompt → LLM     │  │
│  │      ↓              ↓                                      │  │
│  │  BeautifulSoup   IDs, Names,                              │  │
│  │                  CSS Classes                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         VECTOR DATABASE (vector_db/)                      │  │
│  │                                                            │  │
│  │  VectorDB (Abstract Base)                                 │  │
│  │       ↓                                                    │  │
│  │  ChromaVectorDB                                            │  │
│  │       ↓                                                    │  │
│  │  • add_documents()                                         │  │
│  │  • search()                                                │  │
│  │  • delete_all()                                            │  │
│  │                                                            │  │
│  │  Storage: ./chroma_db/                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FILE STORAGE                                  │  │
│  │                                                            │  │
│  │  • Uploaded documents: ./resources/uploads/               │  │
│  │  • Generated queries: ./resources/queries/                │  │
│  │  • Generated scripts: ./resources/scripts/                │  │
│  │  • HTML content: In-memory                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              OPENAI API                                    │  │
│  │                                                            │  │
│  │  Model: gpt-3.5-turbo                                      │  │
│  │  • Test case generation                                    │  │
│  │  • Selenium script generation                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         SENTENCE TRANSFORMERS                              │  │
│  │                                                            │  │
│  │  Model: all-MiniLM-L6-v2                                   │  │
│  │  • Document embedding                                      │  │
│  │  • Query embedding                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Document Ingestion Flow

```
User uploads files
       ↓
Frontend sends to /api/upload
       ↓
Backend creates timestamped session folder
       ↓
Backend saves to ./resources/uploads/{timestamp}/
       ↓
User clicks "Build Knowledge Base"
       ↓
Frontend calls /api/build_kb
       ↓
Backend clears existing vector database
       ↓
IngestionPipeline processes files:
  1. DocumentExtractor extracts text (with OCR fallback for PDFs)
  2. DocumentChunker splits into chunks
  3. EmbeddingGenerator creates vectors
  4. ChromaVectorDB stores chunks + vectors
       ↓
Success response to frontend
```

### 2. Test Case Generation Flow

```
User enters query
       ↓
Frontend sends to /api/generate_tests
       ↓
Backend appends query to ./resources/queries/queries.txt
       ↓
RAGEngine processes:
  1. Embed query with Sentence Transformers
  2. Search ChromaDB for top-k similar chunks
  3. Build prompt with query + context
  4. Call OpenAI API (gpt-3.5-turbo)
  5. Parse JSON response
  6. Format test cases
       ↓
Backend saves test cases to ./resources/queries/test_cases_{timestamp}.json
       ↓
Return test cases to frontend
       ↓
Display in JSON and Markdown table
```

### 3. Selenium Script Generation Flow

```
User selects one or more test cases
       ↓
Frontend resets script session (POST /api/reset_script_session)
       ↓
Frontend sends each test case to /api/generate_script
       ↓
Backend creates timestamped session folder (first call only)
       ↓
SeleniumScriptGenerator processes:
  1. Parse HTML with BeautifulSoup (if HTML provided)
  2. Extract all selectors (IDs, names, classes)
  3. Retrieve context from RAGEngine (top-3 chunks)
  4. Build prompt with test case + HTML + context
  5. Call OpenAI API (gpt-3.5-turbo)
  6. Clean up generated script (remove markdown formatting)
       ↓
Backend saves script to ./resources/scripts/{timestamp}/script_{test_id}.py
       ↓
Return script to frontend
       ↓
Display all scripts with syntax highlighting
       ↓
User can download combined scripts
```

## Component Interactions

### Frontend ↔ Backend

```
Streamlit (Port 8501) ←→ FastAPI (Port 8000)
         HTTP/REST
```

### Backend ↔ Vector Database

```
FastAPI ←→ ChromaDB
    Python API
```

### Backend ↔ LLM

```
FastAPI ←→ OpenAI API
    HTTPS/REST
```

### Backend ↔ Embeddings

```
FastAPI ←→ Sentence Transformers
    Local Model
```

## Module Dependencies

```
frontend/app.py
    ├── streamlit
    └── requests → backend/main.py

backend/main.py
    ├── fastapi
    ├── ingest.py
    ├── rag_engine.py
    └── selenium_gen.py

backend/ingest.py
    ├── pymupdf (PDF)
    ├── beautifulsoup4 (HTML)
    ├── langchain (Chunking)
    ├── sentence-transformers (Embeddings)
    └── vector_db/chroma_db.py

backend/rag_engine.py
    ├── openai (LLM)
    ├── sentence-transformers (Embeddings)
    └── vector_db/chroma_db.py

backend/selenium_gen.py
    ├── beautifulsoup4 (HTML parsing)
    ├── openai (LLM)
    └── rag_engine.py

backend/vector_db/chroma_db.py
    ├── chromadb
    └── vector_db/base.py
```

## File Organization

```
qa-agent/
├── backend/              # Backend API and business logic
│   ├── main.py          # FastAPI application
│   ├── ingest.py        # Document processing with OCR support
│   ├── rag_engine.py    # RAG implementation
│   ├── selenium_gen.py  # Script generation
│   └── vector_db/       # Database abstraction
│       ├── base.py      # Abstract interface
│       └── chroma_db.py # ChromaDB implementation
│
├── frontend/            # Streamlit UI
│   └── app.py          # Multi-page application with navigation
│
├── assets/             # Sample documents
│   ├── product_specs.md
│   ├── checkout.html
│   ├── ui_ux_guide.txt
│   └── api_endpoints.json
│
├── tests/              # Test suite and test documents
│   ├── TEST_PROMPT.md
│   ├── product_specs.md
│   ├── checkout.html
│   ├── ui_ux_guide.txt
│   └── api_endpoints.json
│
├── resources/          # Runtime data storage (organized by session)
│   ├── uploads/        # Uploaded documents (timestamped folders)
│   ├── queries/        # Query logs and test cases (timestamped files)
│   └── scripts/        # Generated scripts (timestamped folders)
│
├── chroma_db/          # Vector database storage (created at runtime)
│
├── .streamlit/         # Streamlit configuration
│   └── config.toml
│
├── start_backend.sh    # Backend startup script
├── start_frontend.sh   # Frontend startup script
│
└── [Configuration and documentation files]
```

## Technology Stack

### Frontend
- **Streamlit 1.28+**: Multi-page web UI framework with navigation
- **Requests 2.31+**: HTTP client for API communication

### Backend
- **FastAPI 0.104+**: Web framework
- **Uvicorn 0.24+**: ASGI server
- **Python-multipart 0.0.6+**: File upload handling

### Document Processing
- **PyMuPDF 1.23+**: PDF extraction with OCR fallback support
- **BeautifulSoup4 4.12+**: HTML parsing and selector extraction
- **lxml 4.9+**: XML/HTML parser
- **Pytesseract** (optional): OCR for scanned PDFs
- **Pillow** (optional): Image processing for OCR

### Text Processing
- **LangChain 0.0.300+**: Text splitting
- **LangChain-text-splitters 0.0.1+**: Chunking utilities

### Machine Learning
- **Sentence-Transformers 2.2+**: Embeddings
- **Torch 2.0+**: ML framework
- **OpenAI 1.0+**: LLM API

### Vector Database
- **ChromaDB 0.4+**: Vector storage and search

### Testing & Automation
- **Pytest 7.4+**: Test framework
- **Pytest-asyncio 0.21+**: Async test support
- **Hypothesis 6.88+**: Property-based testing
- **Selenium 4.15+**: Browser automation

### Utilities
- **NumPy 1.24+**: Numerical operations
- **Python-dotenv 1.0+**: Environment management

## Scalability Considerations

### Current Architecture
- Single-instance deployment
- In-process vector database (ChromaDB)
- Synchronous processing with session-based file organization
- Timestamped folders for upload/script sessions
- Persistent query and test case logging

### Scaling Options

#### Horizontal Scaling
```
Load Balancer
    ├── Backend Instance 1
    ├── Backend Instance 2
    └── Backend Instance 3
         ↓
    Shared Vector DB
```

#### Vertical Scaling
- Increase server resources
- Optimize chunk sizes
- Cache embeddings
- Batch processing

#### Database Scaling
- Use persistent ChromaDB
- Consider Qdrant/Pinecone for production
- Implement sharding
- Add read replicas

## Security Architecture

### API Security
- CORS configuration (allow all origins in development)
- Input validation via Pydantic models
- File type restrictions (.txt, .md, .json, .pdf, .html, .htm)
- Multipart form data handling
- Session-based file isolation

### Data Security
- Environment variables for secrets
- No sensitive data in logs
- Temporary file cleanup
- Secure API key storage

### Network Security
- HTTPS in production
- Rate limiting
- Authentication (future)
- Authorization (future)

## Monitoring Points

### Application Metrics
- Request count
- Response times
- Error rates
- Upload sizes

### Resource Metrics
- CPU usage
- Memory usage
- Disk space
- Network I/O

### Business Metrics
- Documents processed per session
- Test cases generated (logged in queries.txt)
- Scripts generated per session
- LLM API costs (OpenAI gpt-3.5-turbo usage)
- Upload session history
- Script generation session history

---

**Architecture Version**: 1.0
**Last Updated**: November 22, 2025
