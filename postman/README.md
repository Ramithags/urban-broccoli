# Postman Collection for Policy Intelligence API

This directory contains Postman collections and environments for testing the Policy Intelligence API.

## Files

- **Policy_Intelligence_API.postman_collection.json**: Main Postman collection with all API endpoints
- **Policy_Intelligence_API.postman_environment.json**: Environment variables for local development

## Import Instructions

### Option 1: Import via Postman UI

1. Open Postman
2. Click **Import** button (top left)
3. Select both JSON files:
   - `Policy_Intelligence_API.postman_collection.json`
   - `Policy_Intelligence_API.postman_environment.json`
4. Click **Import**

### Option 2: Import via Command Line

```bash
# Using Postman CLI (Newman)
newman run Policy_Intelligence_API.postman_collection.json \
  -e Policy_Intelligence_API.postman_environment.json
```

## Collection Structure

### Endpoints Included

1. **Health Check** (`GET /health`)
   - Check API health and service status

2. **Root Endpoint** (`GET /`)
   - Get API information

3. **Metrics** (`GET /metrics`)
   - View Prometheus-style metrics

4. **Policy Search** (`POST /api/v1/policy/search`)
   - Multiple example requests for different claim scenarios:
     - Auto collision claims
     - Property fire damage
     - Theft claims
     - Medical expenses
     - Flood damage
     - Liability claims
     - Wear and tear exclusions
     - Claims procedure queries

## Environment Variables

The collection uses the following environment variables:

- `base_url`: Base URL for the API (default: `http://localhost:8000`)
- `api_prefix`: API prefix path (default: `/api/v1`)

## Usage

1. **Select Environment**: Choose "Policy Intelligence API - Local" from the environment dropdown
2. **Update Base URL**: If your API runs on a different port, update the `base_url` variable
3. **Run Requests**: Click on any request and hit **Send**

## Example Request Body

```json
{
    "claim_description": "My car was damaged in a collision with another vehicle",
    "max_results": 10,
    "min_score": 0.5
}
```

## Testing Different Scenarios

The collection includes pre-configured requests for various insurance claim scenarios. Each request demonstrates different use cases:

- **High relevance searches**: Using `min_score: 0.6` for strict matching
- **Broad searches**: Using `min_score: 0.3` to find related clauses
- **Different claim types**: Auto, property, liability, medical, etc.

## Tips

1. **Start with Health Check**: Always verify the API is running before testing search endpoints
2. **Initialize Sample Data**: Run `python scripts/init_sample_data.py` before testing search endpoints
3. **Adjust Parameters**: Modify `max_results` and `min_score` to see different result sets
4. **Check Metrics**: Use the Metrics endpoint to monitor API performance

## Running Automated Tests

You can add test scripts to the collection to automate validation:

```javascript
// Example test script for Policy Search
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has results", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('results');
    pm.expect(jsonData.results).to.be.an('array');
});

pm.test("Search time is reasonable", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.search_time_ms).to.be.below(5000);
});
```

## Troubleshooting

- **Connection Refused**: Ensure the API server is running (`python run.py`)
- **Empty Results**: Make sure sample data is initialized (`python scripts/init_sample_data.py`)
- **Model Download**: First request may take longer as the embedding model downloads from Hugging Face
