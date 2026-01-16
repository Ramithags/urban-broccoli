"""ChromaDB vector store service for policy clauses."""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional, Tuple
from app.config import settings
from app.logging_config import logger
from app.metrics import track_vector_search
from app.services.embedding_service import embedding_service


class VectorStoreService:
    """Service for managing policy clauses in ChromaDB."""
    
    def __init__(self):
        """Initialize the vector store service."""
        self.client: chromadb.Client = None
        self.collection = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        if self._initialized:
            return
        
        logger.info(
            "Initializing ChromaDB",
            db_path=settings.chroma_db_path,
            collection_name=settings.chroma_collection_name
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=settings.chroma_collection_name
            )
            logger.info("Using existing ChromaDB collection")
        except Exception:
            self.collection = self.client.create_collection(
                name=settings.chroma_collection_name,
                metadata={
                    "description": "Insurance policy clauses",
                    "hnsw:space": "cosine"  # Use cosine similarity
                }
            )
            logger.info("Created new ChromaDB collection with cosine similarity")
        
        self._initialized = True
        logger.info("Vector store initialized successfully")
    
    async def add_policy_clauses(
        self,
        clauses: List[Dict[str, str]]
    ):
        """
        Add policy clauses to the vector store.
        
        Args:
            clauses: List of dictionaries with keys: clause_id, clause_text, 
                    policy_type (optional), section (optional)
        """
        if not self._initialized:
            await self.initialize()
        
        if not clauses:
            return
        
        logger.info("Adding policy clauses to vector store", count=len(clauses))
        
        # Extract texts for embedding
        texts = [clause["clause_text"] for clause in clauses]
        
        # Generate embeddings
        embeddings = await embedding_service.encode(texts)
        
        # Prepare data for ChromaDB
        ids = [clause["clause_id"] for clause in clauses]
        documents = texts
        metadatas = [
            {
                "policy_type": clause.get("policy_type", ""),
                "section": clause.get("section", "")
            }
            for clause in clauses
        ]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("Policy clauses added successfully")
    
    @track_vector_search
    async def search(
        self,
        query_text: str,
        max_results: int = 10,
        min_score: float = 0.0
    ) -> List[Tuple[Dict, float]]:
        """
        Search for relevant policy clauses.
        
        Args:
            query_text: The search query (claim description)
            max_results: Maximum number of results to return
            min_score: Minimum relevance score threshold
            
        Returns:
            List of tuples containing (clause_dict, score)
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(
            "Searching vector store",
            query_length=len(query_text),
            max_results=max_results,
            min_score=min_score
        )
        
        # Generate query embedding
        query_embedding = await embedding_service.encode_single(query_text)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                # ChromaDB distances:
                # l2: squared L2 distance (0 to infinity)
                # ip: inner product (1.0 - similarity)
                # cosine: 1.0 - similarity (0 to 2)
                distance = results["distances"][0][i]
                score = 1.0 - distance
                
                logger.debug(
                    "Result found",
                    id=results["ids"][0][i],
                    distance=distance,
                    calculated_score=score
                )
                
                if score >= min_score:
                    clause_dict = {
                        "clause_id": results["ids"][0][i],
                        "clause_text": results["documents"][0][i],
                        "policy_type": results["metadatas"][0][i].get("policy_type"),
                        "section": results["metadatas"][0][i].get("section"),
                        "relevance_score": score
                    }
                    formatted_results.append((clause_dict, score))
        
        if not formatted_results and results["ids"] and len(results["ids"][0]) > 0:
            best_score = 1.0 - results["distances"][0][0]
            logger.info(
                "All results filtered out by min_score",
                best_found_score=best_score,
                threshold=min_score
            )
        
        logger.info(
            "Search completed",
            results_count=len(formatted_results)
        )
        
        return formatted_results
    
    async def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        if not self._initialized:
            await self.initialize()
        
        return self.collection.count()


# Global instance
vector_store_service = VectorStoreService()
