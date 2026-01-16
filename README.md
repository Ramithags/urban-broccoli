# Policy Intelligence API

A production-ready FastAPI application for an Insurance company featuring a RAG-powered Policy Intelligence API. This system enables intelligent search and retrieval of relevant policy clauses based on claim descriptions using semantic similarity.

## Features

- **RAG-Powered Search**: Uses industry-bert-insurance-v0.1 model via Hugging Face SentenceTransformer for semantic embeddings
- **Vector Store**: ChromaDB for efficient similarity search (local for MVP)
- **Async Architecture**: FastAPI with asynchronous endpoints for high performance
- **Enterprise Standards**:
  - Pydantic schemas for request/response validation
  - Structured logging with structlog
  - Prometheus-style metrics for latency tracking
  - Health check endpoints
  - Comprehensive error handling

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Embedding Model**: industry-bert-insurance-v0.1 (SentenceTransformer)
- **Vector Database**: ChromaDB 0.4.18
- **Validation**: Pydantic 2.5.0
- **Logging**: structlog 23.2.0
- **Metrics**: prometheus-client 0.19.0
- **Server**: Uvicorn with async support

## Project Structure

```
urban-broccoli/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── schemas.py              # Pydantic schemas
│   ├── logging_config.py       # Structured logging setup
│   ├── metrics.py              # Prometheus metrics
│   └── services/
│       ├── __init__.py
│       ├── embedding_service.py    # SentenceTransformer service
│       ├── vector_store.py         # ChromaDB integration
│       └── sample_data.py          # Sample policy clauses
├── scripts/
│   └── init_sample_data.py     # Initialize vector store
├── postman/
│   ├── Policy_Intelligence_API.postman_collection.json
│   ├── Policy_Intelligence_API.postman_environment.json
│   ├── curl_examples.sh        # cURL test scripts
│   └── README.md               # Postman usage guide
├── requirements.txt
├── run.py                      # Simple startup script
├── .gitignore
└── README.md
```

## Quick Start

```bash
# 1. Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. Initialize sample data
python scripts/init_sample_data.py

# 4. Run the application
python run.py

# 5. Open http://localhost:8000/docs in your browser
```

For detailed instructions, see the [Installation](#installation) and [Running the Application](#running-the-application) sections below.

## Installation

### Python Version Requirements

- **Recommended**: Python 3.11 or 3.12 (most stable and fully supported)
- **Python 3.13**: ⚠️ **Not fully supported yet** - PyTorch (required by sentence-transformers) doesn't have Python 3.13 wheels yet. Please use Python 3.11 or 3.12 for now.

### Installation Steps

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Upgrade pip and setuptools** (especially important for Python 3.13):
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If you encounter installation issues, see `INSTALLATION_TROUBLESHOOTING.md` for detailed solutions.
   
   **Important**: If using Python 3.13, you may encounter PyTorch compatibility issues. We recommend using Python 3.11 or 3.12.

5. **Initialize sample data** (recommended for first-time setup):
   ```bash
   python scripts/init_sample_data.py
   ```
   
   This will populate the vector store with 10 sample policy clauses for testing.

## Running the Application

### Prerequisites

Before running the application, ensure:
- ✅ Virtual environment is activated
- ✅ All dependencies are installed (`pip install -r requirements.txt`)
- ✅ Sample data is initialized (optional but recommended)

### Running Methods

| Method | Command | Use Case | Auto-reload |
|--------|---------|----------|-------------|
| **run.py script** | `python run.py` | Development (Recommended) | ✅ Yes |
| **uvicorn (dev)** | `uvicorn app.main:app --reload` | Development | ✅ Yes |
| **uvicorn (prod)** | `uvicorn app.main:app --workers 4` | Production | ❌ No |

**Method 1: Using the provided run script** (Recommended for Development)
```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python run.py
```

**Method 2: Using uvicorn directly** (Development with auto-reload)
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run with uvicorn (development mode)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Method 3: Production mode** (Multiple workers, no auto-reload)
```bash
# Run with multiple workers for production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Method 4: Using environment variables** (Custom configuration)
```bash
# Set environment variables
export LOG_LEVEL=DEBUG
export EMBEDDING_DEVICE=cpu

# Run the application
python run.py
```

### Application Startup

When you start the application, you should see output similar to:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Note**: On first run, the embedding model (`industry-bert-insurance-v0.1`) will be downloaded from Hugging Face (~400MB). This may take a few minutes depending on your internet connection.

### Accessing the Application

Once the server is running, the API is available at:

- **API Base URL**: http://localhost:8000
- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check Endpoint**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Root Endpoint**: http://localhost:8000/

### Verifying the Application is Running

1. **Check Health Status**:
   ```bash
   curl http://localhost:8000/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0",
     "model_loaded": true,
     "vector_store_ready": true
   }
   ```

2. **View API Documentation**:
   Open http://localhost:8000/docs in your browser to see the interactive API documentation.

3. **Test Policy Search**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/policy/search" \
     -H "Content-Type: application/json" \
     -d '{
       "claim_description": "My car was damaged in a collision",
       "max_results": 5,
       "min_score": 0.5
     }'
   ```

### Stopping the Application

Press `CTRL+C` in the terminal where the server is running to stop the application gracefully.

### Common Issues

**Issue**: Port 8000 is already in use
```bash
# Solution 1: Use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Solution 2: Find and kill the process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Issue**: Model download fails
- Check your internet connection
- Ensure you have sufficient disk space (~500MB)
- The model will be cached in `~/.cache/huggingface/` for future use

**Issue**: Vector store not initialized
```bash
# Run the initialization script
python scripts/init_sample_data.py
```

**Issue**: Import errors
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip list`
- Reinstall if needed: `pip install -r requirements.txt --force-reinstall`

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

Returns the health status of the API and its dependencies.

#### 2. Policy Search
```bash
POST /api/v1/policy/search
```

**Request Body**:
```json
{
  "claim_description": "My car was damaged in a collision with another vehicle",
  "max_results": 10,
  "min_score": 0.5
}
```

**Response**:
```json
{
  "query": "My car was damaged in a collision with another vehicle",
  "results": [
    {
      "clause_id": "CLAUSE_001",
      "clause_text": "This policy covers damage to the insured vehicle...",
      "policy_type": "Auto Insurance",
      "section": "Coverage",
      "relevance_score": 0.95
    }
  ],
  "total_results": 1,
  "search_time_ms": 45.2,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Example cURL Request

```bash
curl -X POST "http://localhost:8000/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "My vehicle was damaged in an accident",
    "max_results": 5,
    "min_score": 0.6
  }'
```

### Postman Collection

A complete Postman collection with pre-configured requests is available in the `postman/` directory:

1. **Import Collection**: 
   - Open Postman
   - Click **Import**
   - Select `postman/Policy_Intelligence_API.postman_collection.json`
   - Select `postman/Policy_Intelligence_API.postman_environment.json`

2. **Collection Includes**:
   - Health check endpoint
   - Root endpoint
   - Metrics endpoint
   - 8 pre-configured policy search examples covering various claim scenarios:
     - Auto collision claims
     - Property fire damage
     - Theft claims
     - Medical expenses
     - Flood damage
     - Liability claims
     - Wear and tear exclusions
     - Claims procedure queries

3. **cURL Scripts**: 
   - Run `bash postman/curl_examples.sh` for command-line testing
   - Requires `jq` for JSON formatting (install via `brew install jq` or `apt-get install jq`)

See `postman/README.md` for detailed instructions.

## Configuration

Configuration is managed through `app/config.py` using Pydantic Settings. You can override settings via environment variables or a `.env` file:

```env
# .env file example
APP_NAME=Policy Intelligence API
DEBUG=false
EMBEDDING_MODEL=industry-bert-insurance-v0.1
EMBEDDING_DEVICE=cpu
CHROMA_DB_PATH=./.chromadb
CHROMA_COLLECTION_NAME=policy_clauses
API_PREFIX=/api/v1
MAX_RESULTS=10
LOG_LEVEL=INFO
```

## Metrics

The API exposes Prometheus-style metrics at `/metrics`:

- `http_requests_total`: Total HTTP requests by method, endpoint, and status code
- `http_request_duration_seconds`: HTTP request latency histogram
- `active_requests`: Current number of active requests
- `embedding_operations_total`: Total embedding operations
- `embedding_duration_seconds`: Embedding operation latency
- `vector_search_operations_total`: Total vector search operations
- `vector_search_duration_seconds`: Vector search latency

## Logging

Structured logging is configured using structlog. Logs are output in JSON format with:
- Timestamps (ISO format)
- Log levels
- Contextual information
- Exception traces

## Adding Policy Clauses

To add your own policy clauses to the vector store, you can use the `VectorStoreService`:

```python
from app.services.vector_store import vector_store_service

clauses = [
    {
        "clause_id": "CUSTOM_001",
        "clause_text": "Your policy clause text here...",
        "policy_type": "Auto Insurance",
        "section": "Coverage"
    }
]

await vector_store_service.add_policy_clauses(clauses)
```

## Development

### Running Tests

```bash
# Add test files and run with pytest
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/
```

## Production Considerations

For production deployment, consider:

1. **GPU Support**: Set `EMBEDDING_DEVICE=cuda` if GPU is available
2. **Database**: Migrate from local ChromaDB to a production vector database (e.g., Pinecone, Weaviate, or managed ChromaDB)
3. **CORS**: Configure appropriate CORS origins in `app/main.py`
4. **Authentication**: Add API key or OAuth2 authentication
5. **Rate Limiting**: Implement rate limiting middleware
6. **Monitoring**: Set up Prometheus/Grafana for metrics visualization
7. **Logging**: Configure log aggregation (e.g., ELK stack, Datadog)
8. **Caching**: Add Redis for caching frequent queries
9. **Load Balancing**: Use multiple workers with Gunicorn/Uvicorn

## License

[Specify your license here]

## Author

Built as a demonstration of production-ready AI/ML API development.
