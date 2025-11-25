# 🤖 Autonomous QA Agent

> **AI-Powered Test Case and Selenium Script Generation System**  

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎥 Video Demonstration

Watch the complete walkthrough and demonstration of the Autonomous QA Agent:

**[📹 Video Demo Link](https://drive.google.com/file/d/1ZUY_t2FBcFEUMIP2X_F27TS_pAQACmuN/view?usp=sharing)**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Autonomous QA Agent** is an intelligent test automation system that leverages **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)** to automatically generate comprehensive test cases and executable Selenium scripts from natural language queries and documentation.

### What It Does

1. **📁 Knowledge Base Ingestion**: Upload product specifications, API documentation, UI/UX guides, and HTML files
2. **📋 Test Case Generation**: Generate detailed test cases using natural language queries
3. **🤖 Selenium Script Generation**: Automatically create executable Selenium WebDriver scripts

### Why It Matters

- **Reduces manual testing effort** by 70%+
- **Accelerates test coverage** with AI-powered generation
- **Maintains context** through RAG-based knowledge retrieval
- **Generates production-ready** Selenium scripts with proper selectors

---

## ✨ Key Features

### 🧠 Intelligent RAG Engine
- Vector-based semantic search using ChromaDB
- Context-aware test case generation
- Grounded responses with source attribution

### 📄 Multi-Format Document Support
- Markdown (`.md`)
- Text files (`.txt`)
- JSON (`.json`)
- PDF with OCR support (`.pdf`)
- HTML/HTM (`.html`, `.htm`)

### 🎯 Smart Test Generation
- Feature-based test case organization
- Expected results and validation points
- Traceability to source documents
- JSON and Markdown table output formats

### 🤖 Selenium Script Generation
- Automatic HTML element selector extraction
- Context-aware script generation
- Multiple test case batch processing
- Downloadable Python scripts

### 📊 Session Management
- Timestamped upload sessions
- Script generation history
- Query logging and tracking
- Organized file storage

### 🎨 Modern UI/UX
- Clean, intuitive Streamlit interface
- Multi-page navigation
- Real-time loading indicators with shimmer effects
- Syntax-highlighted code display

---

## 🏗️ Architecture

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
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                     (backend/main.py)                            │
│                   http://localhost:8000                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           INGESTION PIPELINE (ingest.py)                  │  │
│  │  DocumentExtractor → DocumentChunker → EmbeddingGenerator │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              RAG ENGINE (rag_engine.py)                   │  │
│  │  Query → Embed → Retrieve → Build Prompt → LLM → Parse   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        SELENIUM GENERATOR (selenium_gen.py)               │  │
│  │  HTMLParser → Extract Selectors → Build Prompt → LLM     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         VECTOR DATABASE (ChromaDB)                        │  │
│  │  • Semantic search                                         │  │
│  │  • 384-dim embeddings (all-MiniLM-L6-v2)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FILE STORAGE                                  │  │
│  │  • ./resources/uploads/    (Documents)                    │  │
│  │  • ./resources/queries/    (Test cases)                   │  │
│  │  • ./resources/scripts/    (Selenium scripts)             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🛠️ Technology Stack

### Frontend
- **Streamlit 1.28+**: Interactive web UI with multi-page navigation
- **Requests 2.31+**: HTTP client for backend communication

### Backend
- **FastAPI 0.104+**: High-performance async web framework
- **Uvicorn 0.24+**: ASGI server
- **Python-multipart 0.0.6+**: File upload handling

### AI/ML
- **OpenAI GPT-3.5-turbo**: Test case and script generation
- **Sentence Transformers**: Document and query embeddings (all-MiniLM-L6-v2)
- **ChromaDB 0.4+**: Vector database for semantic search

### Document Processing
- **PyMuPDF 1.23+**: PDF extraction with OCR support
- **BeautifulSoup4 4.12+**: HTML parsing and selector extraction
- **LangChain 0.0.300+**: Text chunking and processing

### Testing & Automation
- **Selenium 4.15+**: Browser automation framework
- **Pytest 7.4+**: Testing framework

---

## 📦 Installation

### Prerequisites

- **Python 3.8+** installed
- **OpenAI API Key** (get one at [platform.openai.com](https://platform.openai.com))
- **Git** (optional, for cloning)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd qa-agent
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo

# Chunking Configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Vector DB Configuration
TOP_K_RESULTS=5
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

---

## 🚀 Quick Start

### Option 1: Using Shell Scripts (Recommended)

#### Terminal 1 - Start Backend
```bash
chmod +x start_backend.sh
./start_backend.sh
```

#### Terminal 2 - Start Frontend
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

### Option 2: Manual Start

#### Terminal 1 - Start Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Start Frontend
```bash
streamlit run frontend/app.py --server.port 8501
```

### Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📖 Usage Guide

### 1. Build Knowledge Base

1. Navigate to **📁 Knowledge Base** tab
2. Upload your documentation files:
   - Product specifications (`.md`, `.txt`)
   - API documentation (`.json`)
   - UI/UX guides (`.txt`, `.md`)
   - Checkout pages (`.html`)
   - PDF documents (`.pdf`)
3. Click **🔨 Build Knowledge Base**
4. Wait for processing to complete

### 2. Generate Test Cases

1. Navigate to **📋 Test Cases** tab
2. Enter your testing query in natural language:
   ```
   Example: "Generate test cases for discount code functionality"
   ```
3. Click **🎯 Generate Test Cases**
4. View results in Markdown Table or JSON format
5. Test cases include:
   - Test ID
   - Feature name
   - Test scenario
   - Expected result
   - Source documents (grounded in)

### 3. Generate Selenium Scripts

1. Navigate to **🤖 Selenium Scripts** tab
2. Select one or more test cases using checkboxes
3. Use **✅ Select All** or **❌ Deselect All** for bulk selection
4. Click **🤖 Generate Selenium Scripts**
5. View generated Python scripts with syntax highlighting
6. Click **📥 Download All Scripts** to save locally

### 4. Run Generated Scripts

```bash
# Navigate to scripts directory
cd resources/scripts/<timestamp>/

# Run a specific script
python script_TC-001.py

# Or run with pytest
pytest script_TC-001.py -v
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Upload Documents
```http
POST /api/upload
Content-Type: multipart/form-data

files: List[UploadFile]
```

**Response**:
```json
{
  "status": "success",
  "message": "Uploaded 4 files to session 20251122_170828",
  "files": ["product_specs.md", "checkout.html"],
  "session": "20251122_170828"
}
```

#### 2. Build Knowledge Base
```http
POST /api/build_kb
```

**Response**:
```json
{
  "status": "success",
  "message": "Ingested 4 documents with 127 chunks"
}
```

#### 3. Generate Test Cases
```http
POST /api/generate_tests
Content-Type: application/json

{
  "query": "Generate test cases for discount code functionality"
}
```

**Response**:
```json
{
  "status": "success",
  "test_cases": [
    {
      "test_id": "TC-001",
      "feature": "Discount Code Validation",
      "test_scenario": "Apply valid discount code",
      "expected_result": "Discount applied successfully",
      "grounded_in": ["product_specs.md", "api_endpoints.json"]
    }
  ]
}
```

#### 4. Generate Selenium Script
```http
POST /api/generate_script
Content-Type: application/json

{
  "test_case": {
    "test_id": "TC-001",
    "feature": "Discount Code Validation",
    "test_scenario": "Apply valid discount code",
    "expected_result": "Discount applied successfully"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "script": "from selenium import webdriver...",
  "session": "20251122_172016"
}
```

#### 5. Clear Data
```http
DELETE /api/clear
```

For interactive API documentation, visit: http://localhost:8000/docs

---

## 📁 Project Structure

```
qa-agent/
├── backend/                    # Backend API and business logic
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   ├── ingest.py              # Document processing pipeline
│   ├── rag_engine.py          # RAG implementation
│   ├── selenium_gen.py        # Script generation
│   └── vector_db/             # Database abstraction layer
│       ├── __init__.py
│       ├── base.py            # Abstract interface
│       └── chroma_db.py       # ChromaDB implementation
│
├── frontend/                   # Streamlit UI
│   ├── __init__.py
│   └── app.py                 # Multi-page application
│
├── tests/                      # Test suite and sample documents
│   ├── TEST_PROMPT.md
│   ├── product_specs.md
│   ├── checkout.html
│   ├── ui_ux_guide.txt
│   └── api_endpoints.json
│
├── resources/                  # Runtime data storage
│   ├── uploads/               # Uploaded documents (timestamped)
│   ├── queries/               # Query logs and test cases
│   └── scripts/               # Generated Selenium scripts
│
├── .streamlit/                 # Streamlit configuration
│   └── config.toml
│
├── .env                        # Environment variables (create this)
├── .gitignore
├── requirements.txt            # Python dependencies
├── start_backend.sh           # Backend startup script
├── start_frontend.sh          # Frontend startup script
├── ARCHITECTURE.md            # Detailed architecture documentation
└── README.md                  # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | OpenAI model for generation | `gpt-3.5-turbo` |
| `CHUNK_SIZE` | Text chunk size for RAG | `500` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `TOP_K_RESULTS` | Number of chunks to retrieve | `5` |

### Streamlit Configuration

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

---

## 💡 Examples

### Example 1: E-commerce Checkout Testing

**Documents to Upload**:
- `product_specs.md` - Product requirements
- `checkout.html` - Checkout page HTML
- `api_endpoints.json` - API documentation
- `ui_ux_guide.txt` - UI/UX guidelines

**Query**:
```
Generate comprehensive test cases for the checkout flow including 
discount codes, shipping calculations, and payment validation
```

**Generated Test Cases**:
- TC-001: Discount Code Validation
- TC-002: Shipping Cost Calculation
- TC-003: Payment Form Validation
- TC-004: Order Summary Verification

### Example 2: API Testing

**Documents to Upload**:
- `api_endpoints.json` - API specifications
- `authentication.md` - Auth documentation

**Query**:
```
Generate test cases for user authentication API endpoints
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. OpenAI API Key Error
```
Error: OpenAI API key not found
```
**Solution**: Ensure `.env` file exists with valid `OPENAI_API_KEY`

#### 2. Port Already in Use
```
Error: Address already in use
```
**Solution**: Kill existing processes or change ports:
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in start scripts
uvicorn main:app --port 8001
```

#### 3. Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Activate virtual environment and reinstall:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 4. ChromaDB Persistence Issues
```
Error: ChromaDB collection not found
```
**Solution**: Clear and rebuild knowledge base:
```bash
rm -rf chroma_db/
# Then rebuild through UI
```

### Debug Mode

Enable debug logging:

```python
# In backend/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-3.5-turbo API
- **Sentence Transformers** for embedding models
- **ChromaDB** for vector database
- **Streamlit** for the amazing UI framework
- **FastAPI** for the high-performance backend

