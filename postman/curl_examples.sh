#!/bin/bash

# Policy Intelligence API - cURL Examples
# Make sure the API is running on http://localhost:8000

BASE_URL="http://localhost:8000"

echo "=== Health Check ==="
curl -X GET "${BASE_URL}/health" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n\n=== Root Endpoint ==="
curl -X GET "${BASE_URL}/" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n\n=== Metrics ==="
curl -X GET "${BASE_URL}/metrics" \
  -H "Content-Type: application/json"

echo -e "\n\n=== Policy Search - Auto Collision (RAG ENABLED) ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "My car was damaged in a collision with another vehicle at an intersection. The front bumper and headlights are completely destroyed.",
    "max_results": 5,
    "min_score": 0.5,
    "is_enable_rag": true
  }' | jq '.'

echo -e "\n\n=== Policy Search - Property Fire Damage (RAG DISABLED) ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "My house caught fire due to an electrical fault. There is significant smoke damage throughout the property and structural damage to the kitchen area.",
    "max_results": 10,
    "min_score": 0.6,
    "is_enable_rag": false
  }' | jq '.'

echo -e "\n\n=== Policy Search - Theft Claim ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "My personal belongings including jewelry and electronics were stolen from my home during a break-in. The items were not specifically listed in my policy.",
    "max_results": 8,
    "min_score": 0.4
  }' | jq '.'

echo -e "\n\n=== Policy Search - Medical Expenses ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "I was injured in a car accident and incurred significant medical expenses including hospital bills, physical therapy, and prescription medications.",
    "max_results": 5,
    "min_score": 0.5
  }' | jq '.'

echo -e "\n\n=== Policy Search - Flood Damage ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "My basement flooded after heavy rainfall, causing water damage to furniture and personal property stored there.",
    "max_results": 10,
    "min_score": 0.3
  }' | jq '.'

echo -e "\n\n=== Policy Search - Liability Claim ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "I am being sued for negligence after someone was injured on my property. I need to understand my liability coverage limits.",
    "max_results": 5,
    "min_score": 0.6
  }' | jq '.'

echo -e "\n\n=== Policy Search - Wear and Tear ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "My vehicle'\''s transmission failed after 150,000 miles. The mechanic says it'\''s due to normal wear and tear.",
    "max_results": 5,
    "min_score": 0.5
  }' | jq '.'

echo -e "\n\n=== Policy Search - Claims Procedure ==="
curl -X POST "${BASE_URL}/api/v1/policy/search" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_description": "I need to know what documents and information I need to provide when filing a claim, and what the time limits are for notification.",
    "max_results": 5,
    "min_score": 0.5
  }' | jq '.'

echo -e "\n\nDone!"
