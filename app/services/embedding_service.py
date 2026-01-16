"""Embedding service using SentenceTransformer with industry-bert-insurance model."""
import os

import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.logging_config import logger
from app.metrics import track_embedding_operation


class EmbeddingService:
    """Service for generating embeddings using insurance BERT model."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.model: SentenceTransformer = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the embedding model asynchronously."""
        if self._initialized:
            return
        
        logger.info(
            "Initializing embedding model",
            model_name=settings.embedding_model,
            device=settings.embedding_device
        )
        
        # Run model loading in executor to avoid blocking
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(
            None,
            lambda: SentenceTransformer(
                settings.embedding_model,
                device=settings.embedding_device
            )
        )
        
        self._initialized = True
        logger.info("Embedding model initialized successfully")
    
    @track_embedding_operation
    async def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            List of embedding vectors
        """
        if not self._initialized:
            await self.initialize()
        
        if not texts:
            return []
        
        logger.debug("Encoding texts", text_count=len(texts))
        
        # Run encoding in executor to avoid blocking
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            ).tolist()
        )
        
        logger.debug("Texts encoded successfully", embedding_dim=len(embeddings[0]) if embeddings else 0)
        return embeddings
    
    async def encode_single(self, text: str) -> List[float]:
        """
        Encode a single text into an embedding.
        
        Args:
            text: Text string to encode
            
        Returns:
            Embedding vector
        """
        embeddings = await self.encode([text])
        return embeddings[0] if embeddings else []


# Global instance
embedding_service = EmbeddingService()
