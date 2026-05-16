# PRISM API Documentation

**Predictive Risk Intelligence for Software Modifications**

A semantic code analysis API that analyzes pull requests to identify risks, impacted components, and generate regression test scenarios using IBM watsonx.ai.

---

## Table of Contents

- [Overview](#overview)
- [API Flow](#api-flow)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health & Info](#health--info)
  - [Analysis](#analysis)
  - [Reports](#reports)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)

---

## Overview

PRISM API provides comprehensive pull request analysis through a multi-stage pipeline that:

1. Fetches PR data from GitHub
2. Analyzes code structure using AST (Abstract Syntax Tree)
3. Builds dependency graphs
4. Identifies impacted components
5. Calculates risk scores
6. Generates semantic insights via IBM watsonx.ai
7. Creates regression test scenarios

---

## API Flow

### Complete Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT REQUEST                               │
│  POST /api/analyze                                               │
│  { "pr_id": "123", "repository": "owner/repo" }                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Fetch PR Data from GitHub                              │
│  • Get PR information (title, description, author)               │
│  • Fetch PR diff                                                 │
│  • Extract PR URL                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Parse Diff                                              │
│  • Extract changed files                                         │
│  • Identify added/modified/deleted lines                         │
│  • Generate change summary                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: AST Analysis                                            │
│  • Fetch file contents from GitHub                               │
│  • Parse code into Abstract Syntax Tree                          │
│  • Extract code elements (functions, classes, methods)           │
│  • Identify dependencies and imports                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Build Dependency Graph                                  │
│  • Create nodes for each code element                            │
│  • Establish edges for dependencies                              │
│  • Calculate node metrics (complexity, centrality)               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Impact Analysis                                         │
│  • Traverse graph from changed nodes                             │
│  • Identify directly impacted components                         │
│  • Find transitively impacted components                         │
│  • Calculate impact scope                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Risk Scoring                                            │
│  • Calculate complexity score                                    │
│  • Assess impact scope                                           │
│  • Evaluate component criticality                                │
│  • Estimate test coverage factor                                 │
│  • Compute overall risk score (0-100)                            │
│  • Assign risk level (LOW/MEDIUM/HIGH/CRITICAL)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: IBM watsonx.ai Semantic Analysis                        │
│  • Send change summary to IBM watsonx.ai                         │
│  • Include impacted components context                           │
│  • Get semantic insights and recommendations                     │
│  • Identify potential issues and side effects                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Generate Regression Test Scenarios                      │
│  • Analyze impacted components                                   │
│  • Create test scenarios for each impact                         │
│  • Prioritize scenarios by risk                                  │
│  • Generate test steps and expected behaviors                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: Store Results & Return Response                         │
│  • Serialize dependency graph                                    │
│  • Save report to database                                       │
│  • Return complete analysis results                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT RESPONSE                              │
│  {                                                               │
│    "report_id": 1,                                               │
│    "risk_score": 75.5,                                           │
│    "risk_level": "HIGH",                                         │
│    "impacted_nodes": [...],                                      │
│    "semantic_insights": "...",                                   │
│    "regression_scenarios": [...]                                 │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your actual domain.

---

## Authentication

Currently, the API does not require authentication for hackathon purposes. In production, implement:

- API key authentication
- OAuth 2.0
- JWT tokens

**GitHub Token**: Required for accessing GitHub API. Set in `.env`:
```
GITHUB_TOKEN=your_github_personal_access_token
```

**IBM watsonx.ai Credentials**: Required for semantic analysis. Set in `.env`:
```
IBM_WATSONX_API_KEY=your_api_key
IBM_WATSONX_PROJECT_ID=your_project_id
```

---

## Endpoints

### Health & Info

#### `GET /`
Root endpoint - basic health check.

**Response:**
```json
{
  "service": "PRISM API",
  "status": "running",
  "version": "1.0.0",
  "description": "Predictive Risk Intelligence for Software Modifications"
}
```

#### `GET /health`
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "github_api": "configured",
    "ibm_watsonx": "configured",
    "ast_analyzer": "ready",
    "graph_builder": "ready"
  }
}
```

#### `GET /api/info`
API capabilities and endpoint information.

**Response:**
```json
{
  "name": "PRISM API",
  "version": "1.0.0",
  "capabilities": [
    "Pull request analysis",
    "Dependency graph construction",
    "Impact analysis",
    "Risk scoring",
    "Semantic insights via IBM watsonx.ai",
    "Regression test scenario generation"
  ],
  "endpoints": {
    "analyze": "POST /api/analyze",
    "get_report": "GET /api/reports/{id}",
    "list_reports": "GET /api/reports",
    "get_by_pr": "GET /api/reports/pr/{pr_id}",
    "stats": "GET /api/reports/stats/summary"
  },
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc"
  }
}
```

---

### Analysis

#### `POST /api/analyze`
Analyze a pull request for semantic risks and impact.

**Request Body:**
```json
{
  "pr_id": "123",
  "repository": "octocat/Hello-World"
}
```

**Parameters:**
- `pr_id` (string, required): Pull request ID or number
- `repository` (string, required): Repository in format 'owner/repo'

**Response:** `200 OK`
```json
{
  "report_id": 1,
  "pr_id": "123",
  "repository": "octocat/Hello-World",
  "pr_url": "https://github.com/octocat/Hello-World/pull/123",
  "changed_files": [
    "src/main.py",
    "src/utils.py"
  ],
  "impacted_nodes": [
    "main.process_data",
    "utils.validate_input",
    "api.handler"
  ],
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "risk_factors": {
    "complexity_score": 80,
    "impact_scope": 70,
    "criticality": 85,
    "test_coverage": 60
  },
  "semantic_insights": "This change modifies core data processing logic. The validation function now handles edge cases differently, which may affect downstream consumers. Recommend thorough testing of error handling paths.",
  "regression_scenarios": [
    {
      "scenario_id": "RS-001",
      "title": "Test data validation with edge cases",
      "description": "Verify that modified validation logic handles edge cases correctly",
      "affected_component": "utils.validate_input",
      "test_steps": [
        "Call validate_input with null value",
        "Call validate_input with empty string",
        "Call validate_input with special characters"
      ],
      "expected_behavior": "Should handle all edge cases gracefully without throwing exceptions",
      "priority": "HIGH"
    }
  ],
  "analysis_duration": 12.5,
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "Analysis failed: GitHub API rate limit exceeded"
}
```

---

#### `GET /api/analyze/status/{report_id}`
Get the status of an analysis by report ID.

**Parameters:**
- `report_id` (integer, required): Database ID of the analysis report

**Response:** `200 OK`
```json
{
  "report_id": 1,
  "status": "completed",
  "pr_id": "123",
  "repository": "octocat/Hello-World",
  "created_at": "2024-01-01T12:00:00Z",
  "risk_level": "HIGH",
  "error_message": null
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Report not found"
}
```

---

#### `POST /api/analyze/batch`
Queue multiple PR analyses to run in the background.

**Request Body:**
```json
[
  {
    "pr_id": "123",
    "repository": "octocat/Hello-World"
  },
  {
    "pr_id": "124",
    "repository": "octocat/Hello-World"
  }
]
```

**Response:** `200 OK`
```json
{
  "message": "Queued 2 analyses",
  "analyses": [
    {
      "pr_id": "123",
      "repository": "octocat/Hello-World",
      "status": "queued"
    },
    {
      "pr_id": "124",
      "repository": "octocat/Hello-World",
      "status": "queued"
    }
  ]
}
```

**Note:** Limited to 5 PRs per batch request.

---

### Reports

#### `GET /api/reports/{report_id}`
Retrieve a specific analysis report by ID.

**Parameters:**
- `report_id` (integer, required): Database ID of the report

**Response:** `200 OK`
```json
{
  "id": 1,
  "pr_id": "123",
  "repository": "octocat/Hello-World",
  "pr_url": "https://github.com/octocat/Hello-World/pull/123",
  "changed_files": ["src/main.py"],
  "dependency_graph": {
    "nodes": [...],
    "edges": [...]
  },
  "impacted_nodes": ["main.process_data"],
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "risk_factors": {
    "complexity_score": 80,
    "impact_scope": 70,
    "criticality": 85,
    "test_coverage": 60
  },
  "semantic_insights": "...",
  "regression_scenarios": [...],
  "created_at": "2024-01-01T12:00:00Z",
  "analysis_duration": 12.5,
  "status": "completed",
  "error_message": null
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Report with ID 1 not found"
}
```

---

#### `GET /api/reports`
List all analysis reports with pagination.

**Query Parameters:**
- `repository` (string, optional): Filter by repository name
- `page` (integer, optional, default: 1): Page number (1-indexed)
- `page_size` (integer, optional, default: 50): Items per page (max: 100)

**Response:** `200 OK`
```json
{
  "reports": [
    {
      "id": 1,
      "pr_id": "123",
      "repository": "octocat/Hello-World",
      "risk_score": 75.5,
      "risk_level": "HIGH",
      "created_at": "2024-01-01T12:00:00Z",
      "status": "completed"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

---

#### `GET /api/reports/pr/{pr_id}`
Retrieve the most recent analysis report for a specific PR.

**Parameters:**
- `pr_id` (string, required): Pull request ID

**Query Parameters:**
- `repository` (string, required): Repository in format 'owner/repo'

**Example:**
```
GET /api/reports/pr/123?repository=octocat/Hello-World
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "pr_id": "123",
  "repository": "octocat/Hello-World",
  ...
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "No report found for PR 123 in octocat/Hello-World"
}
```

---

#### `DELETE /api/reports/{report_id}`
Delete an analysis report.

**Parameters:**
- `report_id` (integer, required): Database ID of the report

**Response:** `200 OK`
```json
{
  "message": "Report 1 deleted successfully"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Report with ID 1 not found"
}
```

---

#### `GET /api/reports/stats/summary`
Get summary statistics about all reports.

**Response:** `200 OK`
```json
{
  "total_reports": 150,
  "average_risk_score": 62.3,
  "risk_distribution": {
    "LOW": 45,
    "MEDIUM": 60,
    "HIGH": 35,
    "CRITICAL": 10
  },
  "most_analyzed_repositories": [
    {
      "repository": "octocat/Hello-World",
      "count": 25
    },
    {
      "repository": "user/repo",
      "count": 20
    }
  ]
}
```

---

## Data Models

### AnalyzeRequest
```json
{
  "pr_id": "string",
  "repository": "string"
}
```

### RiskFactors
```json
{
  "complexity_score": 0-100,
  "impact_scope": 0-100,
  "criticality": 0-100,
  "test_coverage": 0-100
}
```

### RegressionScenario
```json
{
  "scenario_id": "string",
  "title": "string",
  "description": "string",
  "affected_component": "string",
  "test_steps": ["string"],
  "expected_behavior": "string",
  "priority": "HIGH|MEDIUM|LOW"
}
```

### Risk Levels
- `LOW`: Risk score 0-30
- `MEDIUM`: Risk score 31-60
- `HIGH`: Risk score 61-85
- `CRITICAL`: Risk score 86-100

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

### Error Scenarios

1. **GitHub API Errors**: Rate limits, invalid repository, PR not found
2. **Analysis Errors**: AST parsing failures, graph building issues
3. **IBM watsonx.ai Errors**: API unavailable, authentication failures
4. **Database Errors**: Connection issues, query failures

---

## Rate Limits

### GitHub API
- 5,000 requests per hour (authenticated)
- 60 requests per hour (unauthenticated)

### IBM watsonx.ai
- Depends on your IBM Cloud plan
- Monitor usage in IBM Cloud dashboard

### PRISM API
- No rate limits for hackathon version
- Production: Implement rate limiting per API key

---

## Interactive Documentation

PRISM API provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Test API calls directly from the browser
- Download OpenAPI specification

---

## Example Usage

### Using cURL

```bash
# Analyze a PR
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "pr_id": "123",
    "repository": "octocat/Hello-World"
  }'

# Get report by ID
curl "http://localhost:8000/api/reports/1"

# List reports
curl "http://localhost:8000/api/reports?page=1&page_size=10"

# Get report by PR
curl "http://localhost:8000/api/reports/pr/123?repository=octocat/Hello-World"
```

### Using Python

```python
import requests

# Analyze a PR
response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "pr_id": "123",
        "repository": "octocat/Hello-World"
    }
)
result = response.json()
print(f"Risk Score: {result['risk_score']}")
print(f"Risk Level: {result['risk_level']}")

# Get report
report = requests.get(f"http://localhost:8000/api/reports/{result['report_id']}")
print(report.json())
```

### Using JavaScript/Fetch

```javascript
// Analyze a PR
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    pr_id: '123',
    repository: 'octocat/Hello-World'
  })
});

const result = await response.json();
console.log('Risk Score:', result.risk_score);
console.log('Risk Level:', result.risk_level);
```

---

## Development

### Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the server
python -m backend.main

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ast_analyzer.py

# Run with coverage
pytest --cov=backend tests/
```

---

## Support

For issues, questions, or contributions:

- **Documentation**: See `BACKEND_README.md` for detailed backend documentation
- **GitHub Issues**: Report bugs and request features
- **API Docs**: Visit `/docs` for interactive documentation

---

## License

Made with ❤️ by Bob for IBM Hackathon

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-01