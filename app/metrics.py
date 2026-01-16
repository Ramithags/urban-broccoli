"""Prometheus-style metrics for latency tracking."""

from functools import wraps
from prometheus_client import Counter, Histogram, Gauge
from typing import Callable
from time import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


# Metrics definitions
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

active_requests = Gauge(
    "active_requests",
    "Number of active HTTP requests"
)

embedding_operations_total = Counter(
    "embedding_operations_total",
    "Total number of embedding operations"
)

embedding_duration_seconds = Histogram(
    "embedding_duration_seconds",
    "Embedding operation duration in seconds",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0]
)

vector_search_operations_total = Counter(
    "vector_search_operations_total",
    "Total number of vector search operations"
)

vector_search_duration_seconds = Histogram(
    "vector_search_duration_seconds",
    "Vector search duration in seconds",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Track metrics for each request."""
        active_requests.inc()
        start_time = time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time() - start_time
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        finally:
            active_requests.dec()


def track_embedding_operation(func: Callable):
    """Decorator to track embedding operation metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        try:
            result = await func(*args, **kwargs)
            embedding_operations_total.inc()
            return result
        finally:
            duration = time() - start_time
            embedding_duration_seconds.observe(duration)
    
    return wrapper


def track_vector_search(func: Callable):
    """Decorator to track vector search metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        try:
            result = await func(*args, **kwargs)
            vector_search_operations_total.inc()
            return result
        finally:
            duration = time() - start_time
            vector_search_duration_seconds.observe(duration)
    
    return wrapper
