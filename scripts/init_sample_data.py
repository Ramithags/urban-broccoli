"""Script to initialize the vector store with sample policy clauses."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.services.sample_data import SAMPLE_POLICY_CLAUSES
from app.logging_config import logger


async def main():
    """Initialize vector store with sample data."""
    logger.info("Initializing vector store with sample data")
    
    try:
        # Initialize services
        await embedding_service.initialize()
        await vector_store_service.initialize()
        
        # Add sample clauses
        await vector_store_service.add_policy_clauses(SAMPLE_POLICY_CLAUSES)
        
        # Verify
        count = await vector_store_service.get_collection_count()
        logger.info(f"Successfully initialized vector store with {count} policy clauses")
        
    except Exception as e:
        logger.error(f"Failed to initialize sample data: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
