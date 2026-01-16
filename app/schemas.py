"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PolicyClause(BaseModel):
    """Schema for a policy clause."""
    
    clause_id: str = Field(..., description="Unique identifier for the clause")
    clause_text: str = Field(..., description="The actual clause text")
    policy_type: Optional[str] = Field(None, description="Type of insurance policy")
    section: Optional[str] = Field(None, description="Section of the policy")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")


class PolicySearchRequest(BaseModel):
    """Schema for policy search request."""
    
    claim_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Description of the insurance claim"
    )
    max_results: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results to return"
    )
    min_score: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score threshold"
    )
    is_enable_rag: Optional[bool] = Field(
        default=False,
        alias="isEnableRag",
        description="Whether to enable AI-generated analysis (RAG)"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "claim_description": "My car was damaged in a collision",
                "max_results": 5,
                "min_score": 0.5,
                "isEnableRag": True
            }
        }


class PolicySearchResponse(BaseModel):
    """Schema for policy search response."""
    
    query: str = Field(..., description="The original query")
    results: List[PolicyClause] = Field(..., description="List of relevant policy clauses")
    analysis: Optional[str] = Field(None, description="AI-generated analysis of the claim against retrieved clauses")
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether the embedding model is loaded")
    vector_store_ready: bool = Field(..., description="Whether the vector store is ready")
