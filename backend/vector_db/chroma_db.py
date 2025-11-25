"""ChromaDB implementation of vector database."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
import numpy as np
from .base import VectorDB


class ChromaVectorDB(VectorDB):
    """ChromaDB-based vector database implementation."""
    
    def __init__(self, collection_name: str = "qa_agent_docs", persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collection."""
        self.persist_directory = persist_directory
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_documents(self, chunks: List[Dict], embeddings: np.ndarray):
        """Add document chunks with embeddings to ChromaDB."""
        ids = [chunk.get('id', f"doc_{i}") for i, chunk in enumerate(chunks)]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        embeddings_list = embeddings.tolist()
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings_list
        )
    
    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Dict]:
        """Search for similar documents using ChromaDB."""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Format results
        chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                chunks.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0
                })
        
        return chunks
    
    def delete_all(self):
        """Clear all documents from ChromaDB collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
    
    def save(self, filepath: str):
        """ChromaDB persists automatically."""
        pass
    
    def load(self, filepath: str):
        """ChromaDB loads automatically from persist_directory."""
        pass
