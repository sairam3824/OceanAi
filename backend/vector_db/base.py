"""Abstract base class for vector database implementations."""
from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np


class VectorDB(ABC):
    """Abstract base class for vector database implementations."""
    
    @abstractmethod
    def add_documents(self, chunks: List[Dict], embeddings: np.ndarray):
        """Add document chunks with embeddings to the database."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Dict]:
        """Search for similar documents using the query embedding."""
        pass
    
    @abstractmethod
    def delete_all(self):
        """Clear all documents from the database."""
        pass
    
    @abstractmethod
    def save(self, filepath: str):
        """Save the database to disk."""
        pass
    
    @abstractmethod
    def load(self, filepath: str):
        """Load the database from disk."""
        pass
