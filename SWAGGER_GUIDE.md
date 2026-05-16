# PRISM API - Swagger/OpenAPI Documentation Guide

## Overview

The PRISM API uses **FastAPI's built-in OpenAPI (Swagger)** support to provide interactive API documentation. This guide explains how to access and use the documentation.

## Accessing the Documentation

### Swagger UI (Interactive)
```
http://localhost:8000/docs
```

**Features:**
- Interactive API testing
- Try out endpoints directly from the browser
- View request/response schemas
- See example payloads
- Test authentication

### ReDoc (Alternative View)
```
http://localhost:8000/redoc
```

**Features:**
- Clean, three-panel layout
- Better for reading and understanding
- Downloadable OpenAPI spec
- Search functionality

### OpenAPI JSON Spec
```
http://localhost:8000/openapi.json
```

Raw OpenAPI 3.0 specification in JSON format. Use this to:
- Generate client SDKs
- Import into API testing tools (Postman, Insomnia)
- Integrate with API gateways

## Configuration Files

### `backend/swagger_config.py`
Central configuration for all Swagger/OpenAPI settings:

```python
# API Metadata
API_TITLE = "PRISM API"
API_DESCRIPTION = "..."  # Markdown supported
API_VERSION = "1.0.0"
API_CONTACT = {...}
API_LICENSE = {...}

# Tags for endpoint grouping
TAGS_METADATA = [...]

# UI customization
SWAGGER_UI_PARAMETERS = {...}
REDOC_OPTIONS = {...}
```

### `backend/main.py`
FastAPI application with Swagger configuration:

```python
from backend.swagger_config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    TAGS_METADATA,
    SWAGGER_UI_PARAMETERS
)

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    openapi_tags=TAGS_METADATA,
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS
)
```

## Endpoint Documentation

### Adding Documentation to Endpoints

Use docstrings and Pydantic models for automatic documentation:

```python
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_pr(request: AnalyzeRequest):
    """
    Analyze a pull request for semantic risks.
    
    This endpoint performs:
    - AST analysis
    - Dependency graph construction
    - Risk scoring
    - AI insights generation
    
    Args:
        request: Analysis request with PR ID and repository
        
    Returns:
        Complete analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    pass
```

### Schema Examples

Define examples in Pydantic models:

```python
class AnalyzeRequest(BaseModel):
    pr_id: str = Field(..., description="Pull request ID")
    repository: str = Field(..., description="Repository (owner/repo)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pr_id": "123",
                "repository": "owner/repo"
            }
        }
```

## API Endpoints

### Analysis Endpoints

#### `POST /api/analyze`
Analyze a pull request for risks and impact.

**Request:**
```json
{
  "pr_id": "123",
  "repository": "owner/repo-name"
}
```

**Response:**
```json
{
  "report_id": 1,
  "pr_id": "123",
  "repository": "owner/repo-name",
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "changed_files": [...],
  "impacted_nodes": [...],
  "semantic_insights": "...",
  "regression_scenarios": [...]
}
```

#### `GET /api/analyze/status/{report_id}`
Check analysis status by report ID.

#### `POST /api/analyze/batch`
Queue multiple PR analyses (max 5).

### Report Endpoints

#### `GET /api/reports/{report_id}`
Retrieve a specific analysis report.

#### `GET /api/reports`
List all reports with pagination.

**Query Parameters:**
- `repository` (optional): Filter by repository
- `page` (default: 1): Page number
- `page_size` (default: 50, max: 100): Items per page

#### `GET /api/reports/pr/{pr_id}`
Get the most recent report for a specific PR.

**Query Parameters:**
- `repository` (required): Repository name

#### `DELETE /api/reports/{report_id}`
Delete an analysis report.

#### `GET /api/reports/stats/summary`
Get summary statistics about all reports.

### Health Endpoints

#### `GET /`
Root endpoint with API information.

#### `GET /health`
Detailed health check for monitoring.

#### `GET /api/info`
Complete API capabilities and endpoint listing.

## Customization

### Swagger UI Theme

Modify `SWAGGER_UI_PARAMETERS` in `swagger_config.py`:

```python
SWAGGER_UI_PARAMETERS = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "filter": True,
    "syntaxHighlight.theme": "monokai",  # or "agate", "arta", etc.
    "tryItOutEnabled": True,
    "persistAuthorization": True,
}
```

### ReDoc Theme

Modify `REDOC_OPTIONS` in `swagger_config.py`:

```python
REDOC_OPTIONS = {
    "theme": {
        "colors": {
            "primary": {
                "main": "#2196F3"  # Change primary color
            }
        }
    }
}
```

### Adding New Tags

Add to `TAGS_METADATA` in `swagger_config.py`:

```python
TAGS_METADATA = [
    {
        "name": "new-feature",
        "description": "Description of the new feature endpoints"
    }
]
```

Then use in endpoints:

```python
@router.get("/new-endpoint", tags=["new-feature"])
async def new_endpoint():
    pass
```

## Testing with Swagger UI

1. **Navigate to** `http://localhost:8000/docs`
2. **Expand an endpoint** by clicking on it
3. **Click "Try it out"** button
4. **Fill in parameters** (request body, query params, etc.)
5. **Click "Execute"** to send the request
6. **View the response** below (status code, body, headers)

## Generating Client SDKs

Use the OpenAPI spec to generate client libraries:

### Python Client
```bash
# Install openapi-generator
pip install openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client-python
```

### JavaScript/TypeScript Client
```bash
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./client-typescript
```

### Other Languages
OpenAPI Generator supports 50+ languages including:
- Java
- Go
- Ruby
- PHP
- C#
- Rust
- And many more

## Best Practices

1. **Always add docstrings** to endpoints
2. **Use Pydantic models** for request/response validation
3. **Provide examples** in schema definitions
4. **Group related endpoints** with tags
5. **Document error responses** with HTTPException
6. **Keep descriptions concise** but informative
7. **Use Field descriptions** for model attributes
8. **Test endpoints** in Swagger UI before deployment

## Troubleshooting

### Swagger UI not loading
- Check if the server is running: `http://localhost:8000/health`
- Verify CORS settings in `backend/config.py`
- Check browser console for errors

### Missing endpoints
- Ensure routers are included in `main.py`
- Check if endpoints have proper decorators
- Verify tags are defined in `TAGS_METADATA`

### Schema validation errors
- Check Pydantic model definitions
- Ensure all required fields are present
- Verify field types match expected values

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://github.com/Redocly/redoc)
- [OpenAPI Generator](https://openapi-generator.tech/)

## Support

For issues or questions about the API documentation:
- Check the `/api/info` endpoint for current capabilities
- Review this guide
- Contact the development team

---

**Made with Bob** 🤖