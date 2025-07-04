from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import os
import pickle
from dataclasses import dataclass


@dataclass
class Document:
    """Document representation for RAG."""
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    id: Optional[str] = None


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    async def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from the store."""
        pass


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""
    
    def __init__(self, collection_name: str = "default", persist_directory: str = "./data/chroma"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client = None
        self._collection = None
        self._embedding_function = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False)
                )
            except ImportError:
                raise ImportError("ChromaDB not installed. Run: pip install chromadb")
        return self._client
    
    def _get_embedding_function(self):
        if self._embedding_function is None:
            try:
                from chromadb.utils import embedding_functions
                self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            except ImportError:
                raise ImportError("Sentence transformers not installed. Run: pip install sentence-transformers")
        return self._embedding_function
    
    def _get_collection(self):
        if self._collection is None:
            client = self._get_client()
            embedding_function = self._get_embedding_function()
            
            try:
                self._collection = client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
            except Exception:
                self._collection = client.create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
        return self._collection
    
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to ChromaDB."""
        collection = self._get_collection()
        
        ids = [doc.id or f"doc_{i}" for i, doc in enumerate(documents)]
        documents_content = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        collection.add(
            documents=documents_content,
            metadatas=metadatas,
            ids=ids
        )
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents in ChromaDB."""
        collection = self._get_collection()
        
        results = collection.query(
            query_texts=[query],
            n_results=k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, content in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                doc_id = results['ids'][0][i] if results['ids'] and results['ids'][0] else None
                
                documents.append(Document(
                    content=content,
                    metadata=metadata,
                    id=doc_id
                ))
        
        return documents
    
    async def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from ChromaDB."""
        collection = self._get_collection()
        collection.delete(ids=document_ids)


class FAISSVectorStore(BaseVectorStore):
    """FAISS vector store implementation."""
    
    def __init__(self, embedding_dim: int = 384, persist_path: str = "./data/faiss"):
        self.embedding_dim = embedding_dim
        self.persist_path = persist_path
        self._index = None
        self._documents = []
        self._embedding_model = None
        os.makedirs(persist_path, exist_ok=True)
    
    def _get_embedding_model(self):
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise ImportError("Sentence transformers not installed. Run: pip install sentence-transformers")
        return self._embedding_model
    
    def _get_index(self):
        if self._index is None:
            try:
                import faiss
                self._index = faiss.IndexFlatL2(self.embedding_dim)
                
                # Try to load existing index
                index_path = os.path.join(self.persist_path, "index.faiss")
                docs_path = os.path.join(self.persist_path, "documents.pkl")
                
                if os.path.exists(index_path) and os.path.exists(docs_path):
                    self._index = faiss.read_index(index_path)
                    with open(docs_path, 'rb') as f:
                        self._documents = pickle.load(f)
                        
            except ImportError:
                raise ImportError("FAISS not installed. Run: pip install faiss-cpu")
        return self._index
    
    def _save_index(self):
        """Save index and documents to disk."""
        try:
            import faiss
            index_path = os.path.join(self.persist_path, "index.faiss")
            docs_path = os.path.join(self.persist_path, "documents.pkl")
            
            faiss.write_index(self._index, index_path)
            with open(docs_path, 'wb') as f:
                pickle.dump(self._documents, f)
        except ImportError:
            pass
    
    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        model = self._get_embedding_model()
        embedding = model.encode([text])[0]
        return embedding.tolist()
    
    async def add_documents(self, documents: List[Document]) -> None:
        """Add documents to FAISS index."""
        index = self._get_index()
        
        import numpy as np
        
        for doc in documents:
            if doc.embedding is None:
                doc.embedding = self._embed_text(doc.content)
            
            embedding_array = np.array([doc.embedding], dtype=np.float32)
            index.add(embedding_array)
            self._documents.append(doc)
        
        self._save_index()
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents using FAISS."""
        index = self._get_index()
        
        if index.ntotal == 0:
            return []
        
        import numpy as np
        
        query_embedding = self._embed_text(query)
        query_array = np.array([query_embedding], dtype=np.float32)
        
        distances, indices = index.search(query_array, min(k, index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self._documents):
                doc = self._documents[idx]
                # Add distance to metadata
                doc.metadata['distance'] = float(distances[0][i])
                results.append(doc)
        
        return results
    
    async def delete_documents(self, document_ids: List[str]) -> None:
        """Delete documents from FAISS store."""
        # FAISS doesn't support easy deletion, so we rebuild the index
        remaining_docs = [doc for doc in self._documents if doc.id not in document_ids]
        
        # Clear current index
        self._index = None
        self._documents = []
        
        # Rebuild with remaining documents
        if remaining_docs:
            await self.add_documents(remaining_docs)


def create_vector_store(store_type: str = "chroma", **kwargs) -> BaseVectorStore:
    """Factory function to create vector store instances."""
    
    if store_type.lower() == "chroma":
        return ChromaVectorStore(**kwargs)
    elif store_type.lower() == "faiss":
        return FAISSVectorStore(**kwargs)
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")