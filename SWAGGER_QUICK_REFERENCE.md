# PRISM API - Swagger Quick Reference

## 🚀 Quick Access

| Resource | URL | Purpose |
|----------|-----|---------|
| **Swagger UI** | `http://localhost:8000/docs` | Interactive API testing |
| **ReDoc** | `http://localhost:8000/redoc` | Clean documentation view |
| **OpenAPI Spec** | `http://localhost:8000/openapi.json` | Raw specification |
| **Health Check** | `http://localhost:8000/health` | Service status |
| **API Info** | `http://localhost:8000/api/info` | Capabilities list |

## 📋 Key Endpoints

### Analysis
```
POST   /api/analyze                    # Analyze a PR
GET    /api/analyze/status/{id}        # Check analysis status
POST   /api/analyze/batch              # Batch analysis (max 5)
```

### Reports
```
GET    /api/reports/{id}               # Get specific report
GET    /api/reports                    # List all reports
GET    /api/reports/pr/{pr_id}         # Get report by PR
DELETE /api/reports/{id}               # Delete report
GET    /api/reports/stats/summary      # Statistics
```

## 🔧 Configuration Files

```
backend/
├── swagger_config.py          # Swagger/OpenAPI configuration
├── main.py                    # FastAPI app with Swagger setup
├── schemas/
│   ├── analysis.py           # Request/response schemas
│   └── report.py             # Report schemas
└── api/
    ├── analysis.py           # Analysis endpoints
    └── reports.py            # Report endpoints
```

## 📝 Example Request

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "pr_id": "123",
    "repository": "owner/repo-name"
  }'
```

## 🎨 Customization Points

### Change API Title/Description
Edit `backend/swagger_config.py`:
```python
API_TITLE = "Your API Name"
API_DESCRIPTION = """Your description"""
```

### Add New Tag
Edit `backend/swagger_config.py`:
```python
TAGS_METADATA = [
    {
        "name": "your-tag",
        "description": "Tag description"
    }
]
```

### Customize Swagger UI Theme
Edit `backend/swagger_config.py`:
```python
SWAGGER_UI_PARAMETERS = {
    "syntaxHighlight.theme": "monokai",  # or "agate", "arta"
    "deepLinking": True,
    "filter": True
}
```

## 🧪 Testing in Swagger UI

1. Go to `http://localhost:8000/docs`
2. Click on an endpoint to expand
3. Click **"Try it out"**
4. Fill in parameters
5. Click **"Execute"**
6. View response below

## 📦 Generate Client SDK

```bash
# Python
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client-python

# TypeScript
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./client-typescript
```

## 🔍 Schema Examples

### Request Schema
```python
class AnalyzeRequest(BaseModel):
    pr_id: str = Field(..., description="PR ID")
    repository: str = Field(..., description="Repository")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pr_id": "123",
                "repository": "owner/repo"
            }
        }
```

### Endpoint Documentation
```python
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_pr(request: AnalyzeRequest):
    """
    Analyze a pull request.
    
    Performs complete semantic analysis including:
    - AST parsing
    - Dependency graph construction
    - Risk scoring
    - AI insights
    """
    pass
```

## 🎯 Response Models

All responses use Pydantic models for automatic validation and documentation:

- `AnalyzeRequest` - Analysis request
- `AnalyzeResponse` - Analysis results
- `ReportResponse` - Full report details
- `ReportListResponse` - Paginated report list
- `RiskFactors` - Risk breakdown
- `RegressionScenario` - Test scenario

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Swagger UI not loading | Check server is running at `http://localhost:8000` |
| Missing endpoints | Verify router is included in `main.py` |
| Schema errors | Check Pydantic model definitions |
| CORS errors | Update `cors_origins` in `backend/config.py` |

## 📚 Documentation Structure

```
API Documentation
├── Health (/)
│   ├── GET /              # Root endpoint
│   ├── GET /health        # Health check
│   └── GET /api/info      # API info
├── Analysis (/api)
│   ├── POST /analyze      # Analyze PR
│   ├── GET /analyze/status/{id}
│   └── POST /analyze/batch
└── Reports (/api/reports)
    ├── GET /{id}
    ├── GET /
    ├── GET /pr/{pr_id}
    ├── DELETE /{id}
    └── GET /stats/summary
```

## 🔐 Environment Variables

Required for API functionality (not Swagger):
```bash
GITHUB_TOKEN=your_token
IBM_BOB_API_KEY=your_key
IBM_BOB_PROJECT_ID=your_project_id
```

## 💡 Pro Tips

1. **Use Swagger UI** for quick testing during development
2. **Use ReDoc** for sharing documentation with team
3. **Export OpenAPI spec** for client generation
4. **Add examples** to all schemas for better documentation
5. **Group endpoints** with tags for better organization
6. **Document errors** with proper HTTP status codes

## 📞 Support

- Full Guide: `SWAGGER_GUIDE.md`
- API Documentation: `http://localhost:8000/docs`
- Backend README: `BACKEND_README.md`

---

**Made with Bob** 🤖