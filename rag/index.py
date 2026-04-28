"""
Vector Index for RAG.
Creates and manages embeddings using ChromaDB.
"""

from typing import List, Optional
from pathlib import Path
import chromadb
import httpx
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from config import DATA_DIR, OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_PROXY_URL, DOCUMENTS_DIR
from utils.logging import logger
from rag.loader import document_loader


class VectorIndex:
    """Manages vector embeddings and similarity search."""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Initialize vector index.
        
        Args:
            persist_directory: Directory to persist embeddings
        """
        if persist_directory is None:
            persist_directory = DATA_DIR / "chroma_db"
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        embedding_kwargs = {
            "openai_api_key": OPENAI_API_KEY,
            "base_url": OPENAI_BASE_URL,
        }
        if OPENAI_PROXY_URL:
            embedding_kwargs["http_client"] = httpx.Client(proxy=OPENAI_PROXY_URL)
            embedding_kwargs["http_async_client"] = httpx.AsyncClient(proxy=OPENAI_PROXY_URL)

        self.embeddings = OpenAIEmbeddings(**embedding_kwargs)
        
        # Initialize or load vector store
        self.vectorstore = None
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create new one."""
        try:
            # Try to load existing vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Loaded existing vector store")
        except Exception as e:
            logger.warning(f"Could not load existing vectorstore: {e}")
            # Create new vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Created new vector store")
    
    def add_documents(self, documents: List) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document chunks
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 3
    ) -> List:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant document chunks
        """
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            logger.debug(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3
    ) -> List[tuple]:
        """
        Search for similar documents with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.debug(f"Found {len(results)} similar documents with scores")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {e}")
            raise
    
    def index_documents_directory(
        self,
        directory: Path = DOCUMENTS_DIR,
        force_reindex: bool = False
    ) -> int:
        """
        Index all documents from a directory.
        
        Args:
            directory: Directory containing documents
            force_reindex: If True, clear existing index first
        
        Returns:
            Number of documents indexed
        """
        try:
            # Clear existing index if requested
            if force_reindex:
                logger.info("Clearing existing index")
                self.clear_index()
            
            # Load documents
            documents = document_loader.load_directory(directory)
            
            if not documents:
                logger.warning("No documents found to index")
                return 0
            
            # Add to vector store
            self.add_documents(documents)
            
            logger.info(f"Indexed {len(documents)} document chunks")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    def clear_index(self):
        """Clear the entire vector store."""
        try:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            if self.vectorstore is not None:
                self.vectorstore.delete_collection()

            self._load_or_create_vectorstore()
            
            logger.info("Vector store cleared")
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            raise
    
    def get_stats(self) -> dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            # ChromaDB collection stats
            collection = self.vectorstore._collection
            count = collection.count()
            indexed_sources = self.get_indexed_sources()
            
            return {
                "total_documents": count,
                "indexed_sources": sorted(indexed_sources),
                "persist_directory": str(self.persist_directory)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    def get_indexed_sources(self) -> set[str]:
        """Return source filenames currently stored in the vector index."""
        collection = self.vectorstore._collection
        count = collection.count()
        if count == 0:
            return set()

        items = collection.get(include=["metadatas"], limit=count)
        metadatas = items.get("metadatas", [])
        return {
            metadata.get("source")
            for metadata in metadatas
            if metadata and metadata.get("source")
        }


# Global index instance
vector_index = VectorIndex()

