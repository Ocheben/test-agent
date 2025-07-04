from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass
from .vector_store import BaseVectorStore, Document, create_vector_store


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    documents: List[Document]
    query: str
    total_found: int
    retrieval_time: float


class DocumentRetriever:
    """Enhanced document retriever with multiple strategies."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 5
    ):
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
    
    async def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add text to the vector store with chunking."""
        chunks = self._chunk_text(text)
        documents = []
        
        base_metadata = metadata or {}
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source": "text_input"
            }
            
            doc = Document(
                content=chunk,
                metadata=chunk_metadata,
                id=f"{base_metadata.get('id', 'text')}_{i}"
            )
            documents.append(doc)
        
        await self.vector_store.add_documents(documents)
    
    async def add_documents(self, documents: List[Document]) -> None:
        """Add pre-formatted documents to the vector store."""
        await self.vector_store.add_documents(documents)
    
    async def retrieve(self, query: str, k: Optional[int] = None) -> RetrievalResult:
        """Retrieve relevant documents for a query."""
        import time
        
        start_time = time.time()
        k = k or self.top_k
        
        # Basic similarity search
        documents = await self.vector_store.similarity_search(query, k)
        
        retrieval_time = time.time() - start_time
        
        return RetrievalResult(
            documents=documents,
            query=query,
            total_found=len(documents),
            retrieval_time=retrieval_time
        )
    
    async def hybrid_retrieve(self, query: str, k: Optional[int] = None) -> RetrievalResult:
        """Enhanced retrieval with query expansion and reranking."""
        import time
        
        start_time = time.time()
        k = k or self.top_k
        
        # Generate multiple query variations
        query_variations = self._generate_query_variations(query)
        
        # Retrieve for each variation
        all_documents = []
        for q in query_variations:
            docs = await self.vector_store.similarity_search(q, k)
            all_documents.extend(docs)
        
        # Remove duplicates and rerank
        unique_docs = self._deduplicate_documents(all_documents)
        reranked_docs = self._rerank_documents(query, unique_docs)
        
        # Take top k results
        final_docs = reranked_docs[:k]
        
        retrieval_time = time.time() - start_time
        
        return RetrievalResult(
            documents=final_docs,
            query=query,
            total_found=len(final_docs),
            retrieval_time=retrieval_time
        )
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size // 2, end - 200), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
                    elif text[i] in '\n':
                        end = i
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate variations of the query for better retrieval."""
        variations = [query]
        
        # Add question form if not already a question
        if not query.strip().endswith('?'):
            variations.append(f"What is {query}?")
            variations.append(f"How does {query} work?")
        
        # Add keyword extraction (simple version)
        words = query.lower().split()
        important_words = [w for w in words if len(w) > 3 and w not in ['what', 'how', 'when', 'where', 'why', 'who']]
        if important_words:
            variations.append(' '.join(important_words))
        
        return variations[:3]  # Limit to 3 variations
    
    def _deduplicate_documents(self, documents: List[Document]) -> List[Document]:
        """Remove duplicate documents based on content similarity."""
        unique_docs = []
        seen_content = set()
        
        for doc in documents:
            # Simple deduplication by content hash
            content_hash = hash(doc.content.strip().lower())
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)
        
        return unique_docs
    
    def _rerank_documents(self, query: str, documents: List[Document]) -> List[Document]:
        """Rerank documents based on relevance to the original query."""
        # Simple scoring based on keyword overlap
        query_words = set(query.lower().split())
        
        def score_document(doc: Document) -> float:
            doc_words = set(doc.content.lower().split())
            overlap = len(query_words.intersection(doc_words))
            return overlap / max(len(query_words), 1)
        
        # Sort by score (descending)
        scored_docs = [(doc, score_document(doc)) for doc in documents]
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored_docs]


class RAGOrchestrator:
    """Orchestrates the RAG pipeline with multiple retrieval strategies."""
    
    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        retriever: Optional[DocumentRetriever] = None
    ):
        self.vector_store = vector_store or create_vector_store("chroma")
        self.retriever = retriever or DocumentRetriever(self.vector_store)
        self.knowledge_base = []
    
    async def add_knowledge(
        self,
        content: str,
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add knowledge to the RAG system."""
        base_metadata = {
            "source": source,
            "timestamp": str(asyncio.get_event_loop().time()),
            **(metadata or {})
        }
        
        await self.retriever.add_text(content, base_metadata)
        self.knowledge_base.append({
            "content": content,
            "metadata": base_metadata
        })
    
    async def query_knowledge(
        self,
        query: str,
        use_hybrid: bool = True,
        k: int = 5
    ) -> RetrievalResult:
        """Query the knowledge base for relevant information."""
        if use_hybrid:
            return await self.retriever.hybrid_retrieve(query, k)
        else:
            return await self.retriever.retrieve(query, k)
    
    async def get_context_for_query(self, query: str, max_context_length: int = 4000) -> str:
        """Get formatted context for a query."""
        result = await self.query_knowledge(query)
        
        context_parts = []
        current_length = 0
        
        for doc in result.documents:
            doc_text = f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.content}\n"
            
            if current_length + len(doc_text) > max_context_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "\n---\n".join(context_parts)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        return {
            "total_documents": len(self.knowledge_base),
            "sources": list(set(item["metadata"].get("source", "unknown") for item in self.knowledge_base)),
            "vector_store_type": type(self.vector_store).__name__
        }