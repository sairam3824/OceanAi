"""FastAPI backend application."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv

from .ingest import DocumentExtractor, DocumentChunker, EmbeddingGenerator, IngestionPipeline
from .rag_engine import RAGEngine
from .selenium_gen import HTMLParser, SeleniumScriptGenerator
from .vector_db.chroma_db import ChromaVectorDB

# Load environment variables
load_dotenv()

app = FastAPI(title="Autonomous QA Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components - Create organized folder structure
RESOURCE_DIR = Path("./resources")
UPLOAD_DIR = RESOURCE_DIR / "uploads"
QUERY_DIR = RESOURCE_DIR / "queries"
SCRIPT_DIR = RESOURCE_DIR / "scripts"

# Create all directories
RESOURCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
QUERY_DIR.mkdir(exist_ok=True)
SCRIPT_DIR.mkdir(exist_ok=True)

vector_db = ChromaVectorDB()
extractor = DocumentExtractor()
chunker = DocumentChunker(
    chunk_size=int(os.getenv('CHUNK_SIZE', 500)),
    chunk_overlap=int(os.getenv('CHUNK_OVERLAP', 50))
)
embedder = EmbeddingGenerator(model_name=os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'))
ingestion_pipeline = IngestionPipeline(vector_db, extractor, chunker, embedder)
rag_engine = RAGEngine(vector_db, embedder)
html_parser = HTMLParser()
selenium_generator = SeleniumScriptGenerator(html_parser, rag_engine)

# Store uploaded files, HTML content, and current script session
uploaded_files = []
html_content_store = ""
current_script_session = None


class TestGenerationRequest(BaseModel):
    query: str


class ScriptGenerationRequest(BaseModel):
    test_case: dict


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Autonomous QA Agent API", "status": "running"}


@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Accept document uploads and store in timestamped folder."""
    try:
        global uploaded_files, html_content_store
        from datetime import datetime
        
        # Create timestamped folder for this upload session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = UPLOAD_DIR / timestamp
        session_dir.mkdir(exist_ok=True)
        
        uploaded_files = []
        html_content_store = ""
        
        print(f"DEBUG: Received {len(files)} files for upload")
        print(f"DEBUG: Creating upload session folder: {session_dir}")
        
        for file in files:
            file_path = session_dir / file.filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(str(file_path))
            print(f"DEBUG: Uploaded {file.filename} to {file_path}")
            
            # Store HTML content if it's an HTML file
            if file.filename.endswith(('.html', '.htm')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content_store = f.read()
        
        print(f"DEBUG: Total uploaded_files after upload: {uploaded_files}")
        
        return {
            "status": "success",
            "message": f"Uploaded {len(files)} files to session {timestamp}",
            "files": [f.filename for f in files],
            "session": timestamp
        }
    
    except Exception as e:
        print(f"DEBUG: Error in upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload_html")
async def upload_html_content(html_content: dict):
    """Accept pasted HTML content."""
    try:
        global html_content_store
        html_content_store = html_content.get('content', '')
        
        return {
            "status": "success",
            "message": "HTML content received"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/build_kb")
async def build_knowledge_base():
    """Trigger knowledge base construction using latest upload session."""
    try:
        print(f"DEBUG: uploaded_files global = {uploaded_files}")
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No valid documents to process")
        
        # Clear existing vector database before ingesting new documents
        print("DEBUG: Clearing existing vector database...")
        vector_db.delete_all()
        
        result = ingestion_pipeline.ingest_documents(uploaded_files)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        
        print(f"DEBUG: Ingestion result = {result}")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Error in build_kb: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate_tests")
async def generate_test_cases(request: TestGenerationRequest):
    """Generate test cases from user query."""
    try:
        # Append the query to a single queries.txt file in queries folder
        from datetime import datetime
        import json
        query_file = QUERY_DIR / "queries.txt"
        
        with open(query_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Query Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            f.write(f"{request.query}\n")
        
        print(f"DEBUG: Appended query to {query_file}")
        
        test_cases = rag_engine.generate_test_cases(request.query)
        
        if not test_cases:
            return {
                "status": "warning",
                "message": "No relevant context found. Please upload more documents.",
                "test_cases": []
            }
        
        # Save test cases to JSON file with timestamp in queries folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_cases_file = QUERY_DIR / f"test_cases_{timestamp}.json"
        with open(test_cases_file, 'w', encoding='utf-8') as f:
            json.dump({
                "query": request.query,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "test_cases": test_cases
            }, f, indent=2)
        
        print(f"DEBUG: Saved test cases to {test_cases_file}")
        
        return {
            "status": "success",
            "test_cases": test_cases
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate_script")
async def generate_selenium_script(request: ScriptGenerationRequest):
    """Generate Selenium script for selected test case and store in timestamped session."""
    try:
        global current_script_session
        from datetime import datetime
        
        # Create new session folder if this is the first script in a batch
        if current_script_session is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_script_session = SCRIPT_DIR / timestamp
            current_script_session.mkdir(exist_ok=True)
            print(f"DEBUG: Created script session folder: {current_script_session}")
        
        # Use HTML content if available, otherwise generate generic script
        html_to_use = html_content_store if html_content_store else "<html><body></body></html>"
        
        script = selenium_generator.generate_script(
            request.test_case,
            html_to_use
        )
        
        # Save the script to session folder
        test_id = request.test_case.get('test_id', 'TC-000')
        script_file = current_script_session / f"script_{test_id}.py"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(f"# Test Case: {test_id}\n")
            f.write(f"# Feature: {request.test_case.get('feature', 'N/A')}\n")
            f.write(f"# Scenario: {request.test_case.get('test_scenario', 'N/A')}\n")
            f.write(f"# Expected: {request.test_case.get('expected_result', 'N/A')}\n\n")
            f.write(script)
        
        print(f"DEBUG: Saved script to {script_file}")
        
        return {
            "status": "success",
            "script": script,
            "session": current_script_session.name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/upload_history")
async def get_upload_history():
    """Get list of all upload sessions."""
    try:
        sessions = []
        for session_dir in sorted(UPLOAD_DIR.iterdir(), reverse=True):
            if session_dir.is_dir() and not session_dir.name.startswith("."):
                files = [f.name for f in session_dir.iterdir() if f.is_file()]
                sessions.append({
                    "session": session_dir.name,
                    "files": files,
                    "file_count": len(files)
                })
        
        return {
            "status": "success",
            "sessions": sessions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/script_history")
async def get_script_history():
    """Get list of all script generation sessions."""
    try:
        sessions = []
        for session_dir in sorted(SCRIPT_DIR.iterdir(), reverse=True):
            if session_dir.is_dir() and not session_dir.name.startswith("."):
                files = [f.name for f in session_dir.iterdir() if f.is_file() and f.suffix == '.py']
                sessions.append({
                    "session": session_dir.name,
                    "scripts": files,
                    "script_count": len(files)
                })
        
        return {
            "status": "success",
            "sessions": sessions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset_script_session")
async def reset_script_session():
    """Reset the current script generation session to start a new batch."""
    try:
        global current_script_session
        current_script_session = None
        
        return {
            "status": "success",
            "message": "Script session reset. Next generation will create a new session."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/clear")
async def clear_data():
    """Clear current session and knowledge base."""
    try:
        global uploaded_files, html_content_store, current_script_session
        
        uploaded_files = []
        html_content_store = ""
        current_script_session = None
        
        # Clear vector database
        vector_db.delete_all()
        
        return {
            "status": "success",
            "message": "Current session and knowledge base cleared"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
