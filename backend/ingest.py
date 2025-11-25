"""Document ingestion module for extracting, chunking, and embedding documents."""
import json
from typing import List, Dict, Tuple
from pathlib import Path
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np


class DocumentExtractor:
    """Extract text from different file formats."""
    
    def extract_text(self, file_path: str) -> str:
        """Extract plain text from .txt or .md files."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_pdf(self, file_path: str) -> str:
        """Extract text using PyMuPDF with OCR fallback."""
        doc = fitz.open(file_path)
        text = ""
        
        # Try standard text extraction first
        for page in doc:
            text += page.get_text()
        
        # If no text extracted, try OCR as fallback
        if not text.strip():
            try:
                import pytesseract
                from PIL import Image
                import io
                
                print(f"No text found in {file_path}, attempting OCR...")
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Perform OCR
                    page_text = pytesseract.image_to_string(img)
                    text += page_text + "\n"
                
                print(f"OCR extracted {len(text)} characters from {file_path}")
            
            except ImportError:
                print(f"Warning: pytesseract not installed. Cannot OCR {file_path}")
                print("Install with: pip install pytesseract pillow")
                print("Also install tesseract: brew install tesseract (macOS)")
            except Exception as e:
                print(f"OCR failed for {file_path}: {e}")
        
        doc.close()
        return text
    
    def extract_html(self, file_path: str) -> Tuple[str, Dict]:
        """Extract text and DOM structure using BeautifulSoup."""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Extract selectors
        selectors = {
            'ids': [],
            'names': [],
            'classes': []
        }
        
        for element in soup.find_all(True):
            if element.get('id'):
                selectors['ids'].append({
                    'tag': element.name,
                    'id': element.get('id')
                })
            if element.get('name'):
                selectors['names'].append({
                    'tag': element.name,
                    'name': element.get('name')
                })
            if element.get('class'):
                selectors['classes'].append({
                    'tag': element.name,
                    'class': ' '.join(element.get('class'))
                })
        
        return text, selectors
    
    def extract_json(self, file_path: str) -> str:
        """Parse JSON and extract text content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to readable text
        return json.dumps(data, indent=2)


class DocumentChunker:
    """Chunk documents for embedding."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def chunk_document(self, text: str, metadata: dict) -> List[dict]:
        """Split document into chunks with metadata."""
        chunks = self.splitter.split_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                'id': f"{metadata.get('filename', 'doc')}_{i}",
                'content': chunk,
                'metadata': {
                    **metadata,
                    'chunk_index': i
                }
            })
        
        return result


class EmbeddingGenerator:
    """Generate embeddings using Sentence Transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for text chunks."""
        return self.model.encode(texts, convert_to_numpy=True)


class IngestionPipeline:
    """Orchestrate the ingestion process."""
    
    def __init__(self, vector_db, extractor: DocumentExtractor, 
                 chunker: DocumentChunker, embedder: EmbeddingGenerator):
        self.vector_db = vector_db
        self.extractor = extractor
        self.chunker = chunker
        self.embedder = embedder
        self.html_selectors = {}
    
    def ingest_documents(self, file_paths: List[str]) -> dict:
        """Process and store documents in vector database."""
        try:
            all_chunks = []
            
            for file_path in file_paths:
                path = Path(file_path)
                file_ext = path.suffix.lower()
                filename = path.name
                
                # Extract text based on file type
                if file_ext in ['.txt', '.md']:
                    text = self.extractor.extract_text(file_path)
                    doc_type = 'text'
                    selectors = None
                elif file_ext == '.pdf':
                    text = self.extractor.extract_pdf(file_path)
                    doc_type = 'pdf'
                    selectors = None
                elif file_ext == '.json':
                    text = self.extractor.extract_json(file_path)
                    doc_type = 'json'
                    selectors = None
                elif file_ext in ['.html', '.htm']:
                    text, selectors = self.extractor.extract_html(file_path)
                    doc_type = 'html'
                    # Store HTML selectors for later use
                    self.html_selectors[filename] = selectors
                else:
                    continue
                
                # Chunk document
                metadata = {
                    'filename': filename,
                    'type': doc_type,
                    'section': 'main'
                }
                
                chunks = self.chunker.chunk_document(text, metadata)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                return {'status': 'error', 'message': 'No valid documents to process'}
            
            # Generate embeddings
            texts = [chunk['content'] for chunk in all_chunks]
            embeddings = self.embedder.generate_embeddings(texts)
            
            # Store in vector database
            self.vector_db.add_documents(all_chunks, embeddings)
            
            return {
                'status': 'success',
                'message': f'Successfully ingested {len(file_paths)} documents with {len(all_chunks)} chunks'
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
