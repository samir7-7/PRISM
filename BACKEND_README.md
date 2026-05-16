# PRISM Backend - Setup and Usage Guide

## Overview

The PRISM backend is a FastAPI-based service that provides semantic code analysis for pull requests. It integrates with GitHub API and IBM watsonx.ai to deliver comprehensive risk assessment and impact analysis.

## Architecture

```
backend/
├── api/              # FastAPI route handlers
├── models/           # SQLAlchemy database models
├── schemas/          # Pydantic request/response schemas
├── services/         # Core business logic
├── repositories/     # Database operations
├── utils/            # Helper utilities
├── config.py         # Configuration management
├── db.py            # Database setup
└── main.py          # Application entry point
```

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- GitHub Personal Access Token
- IBM watsonx.ai API credentials

## Installation

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# GitHub Configuration
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_API_URL=https://api.github.com

# IBM watsonx.ai Configuration
IBM_BOB_API_KEY=your_actual_api_key_here
IBM_BOB_API_URL=https://us-south.ml.cloud.ibm.com
IBM_BOB_PROJECT_ID=your_actual_project_id_here
IBM_BOB_MODEL_ID=ibm/granite-13b-chat-v2

# Database Configuration
DATABASE_URL=sqlite:///./prism.db

# Application Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Initialize Database

The database will be automatically initialized on first run. The SQLite database file will be created at `./prism.db`.

## Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn backend.main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python directly

```bash
python -m backend.main
```

## API Endpoints

### Health Check

```bash
# Basic health check
GET http://localhost:8000/

# Detailed health check
GET http://localhost:8000/health

# API information
GET http://localhost:8000/api/info
```

### Analysis Endpoints

#### Analyze Pull Request

```bash
POST http://localhost:8000/api/analyze
Content-Type: application/json

{
  "pr_id": "123",
  "repository": "owner/repo"
}
```

**Response:**
```json
{
  "report_id": 1,
  "pr_id": "123",
  "repository": "owner/repo",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "changed_files": ["src/file1.py", "src/file2.py"],
  "impacted_nodes": ["module.function1", "module.function2"],
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "risk_factors": {
    "complexity_score": 80.0,
    "impact_scope": 70.0,
    "criticality": 85.0,
    "test_coverage": 60.0
  },
  "semantic_insights": "Analysis from IBM watsonx.ai...",
  "regression_scenarios": [...],
  "analysis_duration": 12.5,
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### Get Analysis Status

```bash
GET http://localhost:8000/api/analyze/status/{report_id}
```

### Report Endpoints

#### Get Report by ID

```bash
GET http://localhost:8000/api/reports/{report_id}
```

#### Get Report by PR

```bash
GET http://localhost:8000/api/reports/pr/{pr_id}?repository=owner/repo
```

#### List All Reports

```bash
GET http://localhost:8000/api/reports?page=1&page_size=50
```

#### Filter Reports by Repository

```bash
GET http://localhost:8000/api/reports?repository=owner/repo&page=1&page_size=50
```

#### Get Statistics Summary

```bash
GET http://localhost:8000/api/reports/stats/summary
```

#### Delete Report

```bash
DELETE http://localhost:8000/api/reports/{report_id}
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Manual Testing with curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test analysis (replace with actual PR)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "pr_id": "123",
    "repository": "octocat/Hello-World"
  }'

# Get report
curl http://localhost:8000/api/reports/1
```

### Using Python requests

```python
import requests

# Analyze PR
response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "pr_id": "123",
        "repository": "owner/repo"
    }
)

result = response.json()
print(f"Risk Score: {result['risk_score']}")
print(f"Risk Level: {result['risk_level']}")
```

## Core Services

### 1. Analysis Pipeline (`services/analysis_pipeline.py`)

Orchestrates the complete analysis workflow:
- Fetches PR data from GitHub
- Parses diff to extract changes
- Analyzes code structure with AST
- Builds dependency graph
- Identifies impacted components
- Calculates risk score
- Gets semantic insights from IBM watsonx.ai
- Generates regression test scenarios

### 2. AST Analyzer (`services/ast_analyzer.py`)

Uses tree-sitter to parse code and extract:
- Function definitions
- Class definitions
- Import statements
- Code structure

Supports: Python, JavaScript, TypeScript

### 3. Graph Builder (`services/graph_builder.py`)

Constructs dependency graphs using NetworkX:
- Nodes represent code elements
- Edges represent dependencies
- Supports graph expansion and traversal

### 4. Impact Traverser (`services/impact_traverser.py`)

Identifies downstream impacts:
- BFS/DFS graph traversal
- Impact depth calculation
- Critical path analysis

### 5. Risk Scorer (`services/risk_scorer.py`)

Calculates risk scores based on:
- Code complexity (25%)
- Impact scope (35%)
- Component criticality (30%)
- Test coverage (10%)

Risk Levels:
- **LOW**: 0-24
- **MEDIUM**: 25-49
- **HIGH**: 50-74
- **CRITICAL**: 75-100

### 6. IBM watsonx.ai Client (`services/ibm_bob_client.py`)

Integrates with IBM's Granite model for:
- Semantic code analysis
- Risk identification
- Testing recommendations
- Deployment considerations

### 7. Regression Generator (`services/regression_generator.py`)

Generates actionable test scenarios:
- File-level scenarios
- Impact-based scenarios
- Integration scenarios
- AI-suggested scenarios

## Database Schema

### AnalysisReport Table

```sql
CREATE TABLE analysis_reports (
    id INTEGER PRIMARY KEY,
    pr_id VARCHAR(50) NOT NULL,
    repository VARCHAR(255) NOT NULL,
    pr_url VARCHAR(500),
    changed_files TEXT,           -- JSON array
    dependency_graph TEXT,         -- JSON serialized graph
    impacted_nodes TEXT,           -- JSON array
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20),
    risk_factors TEXT,             -- JSON object
    semantic_insights TEXT,
    regression_scenarios TEXT,     -- JSON array
    created_at DATETIME NOT NULL,
    analysis_duration FLOAT,
    status VARCHAR(20),
    error_message TEXT
);
```

## Configuration

All configuration is managed through environment variables (see `.env.example`).

### Key Settings

- `GITHUB_TOKEN`: Required for GitHub API access
- `IBM_BOB_API_KEY`: Required for IBM watsonx.ai
- `DATABASE_URL`: SQLite by default, supports PostgreSQL
- `CORS_ORIGINS`: Frontend URLs for CORS
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR

## Error Handling

The backend implements graceful degradation:

- **GitHub API fails**: Returns clear error message
- **AST parsing fails**: Skips file, continues with others
- **IBM watsonx.ai fails**: Returns graph-only analysis
- **Graph building fails**: Returns partial results

All errors are logged with full context.

## Performance Considerations

### For Hackathon (Current Implementation)

- Analyzes only changed files (not entire repository)
- Limits to 10 files per analysis
- Simple in-memory graph construction
- Synchronous processing

### For Production (Future Enhancements)

- Implement caching layer for GitHub API
- Use async task queue (Celery/RQ)
- Persistent graph database
- Incremental graph updates
- Horizontal scaling with load balancer

## Troubleshooting

### Common Issues

**1. Import errors for tree-sitter**
```bash
# Install build tools
pip install wheel
# On Linux/Mac
sudo apt-get install build-essential
```

**2. GitHub API rate limit**
- Use authenticated token
- Implement caching during development

**3. IBM watsonx.ai timeout**
- Check API credentials
- Verify network connectivity
- System implements graceful degradation

**4. SQLite locked error**
- Already handled with `check_same_thread=False`
- For production, use PostgreSQL

## Development Workflow

1. **Make changes** to backend code
2. **Server auto-reloads** (if using `--reload`)
3. **Test endpoints** via Swagger UI or curl
4. **Check logs** for errors
5. **Commit changes** when tests pass

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY .env .env

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables in Production

Use secrets management:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## Monitoring

### Logging

All services log to stdout with structured format:
```
2024-01-01 12:00:00 - backend.services.analysis_pipeline - INFO - Starting analysis for PR 123
```

### Metrics to Track

- Analysis duration
- Success/failure rate
- Risk score distribution
- API response times
- GitHub API usage
- IBM watsonx.ai usage

## Support

For issues or questions:
1. Check logs in console output
2. Review API documentation at `/docs`
3. Verify environment variables
4. Check GitHub/IBM API credentials

## License

MIT License - See LICENSE file for details