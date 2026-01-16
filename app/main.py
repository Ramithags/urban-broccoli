"""FastAPI application main file."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from app.config import settings
from app.logging_config import logger
from app.metrics import MetricsMiddleware
from app.schemas import (
    PolicySearchRequest,
    PolicySearchResponse,
    PolicyClause,
    HealthResponse
)
from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.services.generation_service import generation_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Policy Intelligence API")
    
    try:
        # Initialize services
        await embedding_service.initialize()
        await vector_store_service.initialize()
        await generation_service.initialize()
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Policy Intelligence API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-powered Policy Intelligence API for insurance claim analysis",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the API and its dependencies.
    """
    try:
        model_loaded = embedding_service._initialized
        vector_store_ready = vector_store_service._initialized
        
        status = "healthy" if (model_loaded and vector_store_ready) else "degraded"
        
        return HealthResponse(
            status=status,
            version=settings.app_version,
            model_loaded=model_loaded,
            vector_store_ready=vector_store_ready
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post(
    f"{settings.api_prefix}/policy/search",
    response_model=PolicySearchResponse,
    tags=["Policy Search"]
)
async def search_policies(request: PolicySearchRequest):
    """
    Search for relevant policy clauses based on a claim description.
    
    This endpoint uses RAG (Retrieval-Augmented Generation) to find the most
    relevant policy clauses for a given insurance claim description using
    the industry-bert-insurance embedding model.
    
    Args:
        request: PolicySearchRequest containing claim description and search parameters
        
    Returns:
        PolicySearchResponse with relevant policy clauses and metadata
    """
    start_time = time.time()
    
    try:
        logger.info(
            "Policy search request received",
            query_length=len(request.claim_description),
            max_results=request.max_results,
            min_score=request.min_score
        )
        
        # Perform vector search
        results = await vector_store_service.search(
            query_text=request.claim_description,
            max_results=request.max_results or settings.max_results,
            min_score=request.min_score or 0.0
        )
        
        # Format results
        policy_clauses = [
            PolicyClause(**clause_dict)
            for clause_dict, _ in results
        ]
        
        # GENERATION STEP: Generate AI analysis based on results if RAG is enabled
        analysis = None
        if request.is_enable_rag and policy_clauses:
            logger.info("RAG analysis enabled, generating AI response")
            analysis = await generation_service.generate_analysis(
                query=request.claim_description,
                retrieved_clauses=[c.model_dump() for c in policy_clauses]
            )
        else:
            logger.info("RAG analysis disabled, skipping generation step")
        
        search_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            "Policy search and RAG analysis completed",
            results_count=len(policy_clauses),
            search_time_ms=search_time_ms
        )
        
        return PolicySearchResponse(
            query=request.claim_description,
            results=policy_clauses,
            analysis=analysis,
            total_results=len(policy_clauses),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        logger.error("Policy search failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
